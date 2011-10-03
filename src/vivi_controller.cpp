
#include "vivi_controller.h"
#include <time.h>
#include <math.h>

//#include "artifastring/violin_instrument.h"
#include "artifastring/monowav.h"
#include "actions_file.h"

//#define NDEBUG
#include <assert.h>

#include "midi_pos.h"

using namespace std;

// used in normal hops
const double VELOCITY_STDDEV = 0.01;
const double FORCE_STDDEV = 0.01;
const double MAX_HAND_ACCEL = 5.0; // m/s
const double DH = HOPSIZE * dt;

// used in basic
const double BASIC_VELOCITY_STDDEV = 0.02;
const double BASIC_FORCE_STDDEV = 0.02;

// don't listen to sound until this percent of speed is reached
const double MIN_VELOCITY_FACTOR = 0.80;

// don't listen to sound until this many hops have passed
//const int MIN_SETTLE_HOPS = 4;


const double LET_VIBRATE = 0.5;
const int LIGHTEN_NOTE_HOPS = 12; // FIXME: fix magic number for dampen

ViviController::ViviController() {

    // always used classes
    violin = new ViolinInstrument();
    // setup random generator
    const gsl_rng_type * T = gsl_rng_default;
    random = gsl_rng_alloc (T);
    const long seed = time(NULL) * getpid();
    gsl_rng_set(random, seed);


    wavfile = NULL;
    actions_file = NULL;
    cats_file = NULL;
    for (int i=0; i<NUM_STRINGS; i++) {
        for (int j=0; j<NUM_DYNAMICS; j++) {
            ears[i][j] = NULL;
        }
    }
    reset();
}


ViviController::~ViviController() {
    gsl_rng_free(random);
    filesClose();
    delete violin;
    for (int i=0; i<NUM_STRINGS; i++) {
        for (int j=0; j<NUM_DYNAMICS; j++) {
            if (ears[i][j] != NULL) {
                delete ears[i][j];
            }
        }
    }
}

void ViviController::reset() {
    filesClose();
    violin->reset();
    // only action that matters; others are overwritten anyway
    actions.bow_velocity = 0;

    for (int i=0; i<CATS_MEAN_LENGTH; i++) {
        cats[i] = 0; // neutral
    }
    cats_index = 0;

    m_bow_pos_along = 0.1; // default near frog?
    m_feedback_adjust_force = false;
}

Ears* ViviController::getEars(int st, int dyn) {
    if (ears[st][dyn] == NULL) {
        ears[st][dyn] = new Ears();
    }
    return ears[st][dyn];
}

bool ViviController::load_ears_training(int st, int dyn,
                                        const char *training_file)
{
    if (ears[st][dyn] == NULL) {
        ears[st][dyn] = new Ears();
    }
    if (training_file != NULL) {
        // TODO: replace with const char *
        ears[st][dyn]->set_predict_buffer(training_file);
    }
    return true;
}

void ViviController::set_stable_K(int st, int dyn, double K)
{
    m_K[st][dyn] = K;
}

void ViviController::set_dampen(int st, int dyn, double dampen)
{
    m_dampen[st][dyn] = dampen;
}


inline double ViviController::norm_bounded(double mu, double sigma) {
    if (sigma == 0) {
        return mu;
    }
    double gauss;
    for (int i=0; i<3; i++) {
        gauss = gsl_ran_gaussian_ratio_method(random,sigma);
        if (fabs(gauss) <= 3*sigma) {
            return mu + gauss;
        }
    }
    return mu;
}


void ViviController::filesClose() {
    if (wavfile != NULL) {
        delete wavfile;
        wavfile = NULL;
    }
    if (actions_file != NULL) {
        // finish current action(s)
        actions_file->wait(m_total_samples*dt);
        delete actions_file;
        actions_file = NULL;
    }
    if (cats_file != NULL) {
        delete cats_file;
        cats_file = NULL;
    }
}


bool ViviController::filesNew(const char *filenames_base) {
    reset();
    // wav file
    std::string filename;
    filename.assign(filenames_base);
    filename.append(".wav");
    wavfile = new MonoWav(filename.c_str());
    // actions file
    filename.assign(filenames_base);
    filename.append(".actions");
    actions_file = new ActionsFile(filename.c_str());
    // cats file
    filename.assign(filenames_base);
    filename.append(".cats");
    cats_file = new ActionsFile(filename.c_str());
    // update positions
    m_total_samples = 0;
    return true;
}

void ViviController::basic(NoteBeginning begin, double seconds,
                           double skip_seconds)
{
    actions.string_number = begin.physical.string_number;
    actions.finger_position = begin.physical.finger_position;
    actions.bow_force = begin.physical.bow_force;
    actions.bow_bridge_distance = begin.physical.bow_bridge_distance;
    // ok to copy bow_velocity here.
    actions.bow_velocity = begin.physical.bow_velocity;

    int dyn = round(begin.physical.dynamic);
    char note_search_params[MAX_LINE_LENGTH];
    sprintf(note_search_params, "basic\tst %i\tdyn %i\tfinger_midi %.3f",
            actions.string_number, dyn,
            pos2midi(actions.finger_position));
    comment(note_search_params);

    const double orig_force = actions.bow_force;
    const double orig_velocity = actions.bow_velocity;

    finger();

    // skip, maybe going slightly over given time
    actions_file->skipStart(m_total_samples*dt);
    short mem_buf[HOPSIZE];
    for (int i = 0; i < skip_seconds/DH; i++) {
        actions.bow_force = norm_bounded(orig_force,
                                         BASIC_FORCE_STDDEV
                                         * orig_force);
        actions.bow_velocity = norm_bounded(orig_velocity,
                                            BASIC_VELOCITY_STDDEV
                                            * orig_velocity);

        violin->bow(actions.string_number,
                    actions.bow_bridge_distance,
                    actions.bow_force,
                    actions.bow_velocity);
        actions_file->bow(m_total_samples*dt, actions.string_number,
                          actions.bow_bridge_distance, actions.bow_force,
                          actions.bow_velocity,
                          m_bow_pos_along);
        violin->wait_samples(mem_buf, HOPSIZE);
        m_total_samples += HOPSIZE;
    }
    actions_file->skipStop(m_total_samples*dt);

    // actual note, maybe going slightly over given time
    for (int i = 0; i < seconds/DH; i++) {
        actions.bow_force = norm_bounded(orig_force,
                                         BASIC_FORCE_STDDEV
                                         * orig_force);
        actions.bow_velocity = norm_bounded(orig_velocity,
                                            BASIC_VELOCITY_STDDEV
                                            * orig_velocity);

        violin->bow(actions.string_number,
                    actions.bow_bridge_distance,
                    actions.bow_force,
                    actions.bow_velocity);
        actions_file->bow(m_total_samples*dt, actions.string_number,
                          actions.bow_bridge_distance, actions.bow_force,
                          actions.bow_velocity,
                          m_bow_pos_along);
        short *buf = wavfile->request_fill(HOPSIZE);
        violin->wait_samples(buf, HOPSIZE);
        m_total_samples += HOPSIZE;
    }
}

void ViviController::rest(double seconds)
{
    comment("rest");
    bowStop();

    actions_file->wait(m_total_samples*dt);

    m_note_samples = 0;
    for (int i = 0; i < seconds/DH-1; i++) {
        hop_passive();
    }

    // finish final "half hop"
    int remaining_samples = seconds*44100.0 - m_note_samples;
    // finish final "half hop"
    if (remaining_samples > 0) {
        hop_passive(remaining_samples);
    }
}

void ViviController::pizz(NoteBeginning begin, double seconds)
{
    comment("rest");

    // set up note parameters
    actions.string_number = begin.physical.string_number;
    actions.finger_position = begin.physical.finger_position;
    actions.bow_force = begin.physical.bow_force;
    actions.bow_bridge_distance = begin.physical.bow_bridge_distance;

    finger();
    actions_file->pluck(m_total_samples*dt, actions.string_number,
                        actions.bow_bridge_distance, actions.bow_force);
    violin->pluck(actions.string_number, actions.bow_bridge_distance,
                  actions.bow_force);

    m_note_samples = 0;
    for (int i = 0; i < seconds/DH-1; i++) {
        hop_passive();
    }
    // finish final "half hop"
    int remaining_samples = seconds*44100.0 - m_note_samples;
    // finish final "half hop"
    if (remaining_samples > 0) {
        hop_passive(remaining_samples);
    }

}

void ViviController::note_setup_actions(NoteBeginning begin)
{
    //begin.physical.print();
    actions.string_number = begin.physical.string_number;
    actions.bow_bridge_distance = begin.physical.bow_bridge_distance;
    if (!begin.ignore_finger) {
        actions.finger_position = begin.physical.finger_position;
    }
    if (!begin.keep_bow_force) {
        actions.bow_force = begin.physical.bow_force;
    }
    if (begin.set_bow_position_along >= 0) {
        m_bow_pos_along= begin.set_bow_position_along;
    }

    // don't copy bow_velocity; put it in m_velocity_target instead
    m_velocity_target = begin.physical.bow_velocity;
    m_velocity_cutoff_force_adj = m_velocity_target * MIN_VELOCITY_FACTOR;
    // other setup
    m_st = actions.string_number;
    m_dyn = round(begin.physical.dynamic);
}

void ViviController::note_write_actions(NoteBeginning begin,
                                        NoteEnding end, const char *point_and_click)
{
    char note_search_params[MAX_LINE_LENGTH];
    if (point_and_click == NULL) {
        sprintf(note_search_params, "note\tst %i\tdyn %i\tfinger_midi %.3f",
                m_st, m_dyn,
                pos2midi(actions.finger_position));
    } else {
        sprintf(note_search_params, "note\tst %i\tdyn %i\tfinger_midi %.3f %s",
                m_st, m_dyn,
                pos2midi(actions.finger_position),
                point_and_click);
    }
    comment(note_search_params);
    comment(begin.params_text().c_str());
    comment(end.params_text().c_str());
}

void ViviController::finger()
{
    actions_file->finger(m_total_samples*dt, actions.string_number,
                         actions.finger_position);
    violin->finger(actions.string_number, actions.finger_position);
}

void ViviController::note(NoteBeginning begin, double seconds,
                          NoteEnding end,
                          const char *point_and_click,
                          double alter_force)
{
    assert((begin.physical.string_number >= 0) &&
           (begin.physical.string_number < NUM_STRINGS));
    assert((begin.physical.dynamic >= 0) &&
           (begin.physical.dynamic < NUM_DYNAMICS));

    note_setup_actions(begin);
    note_write_actions(begin, end, point_and_click);

    char alter_force_text[MAX_LINE_LENGTH];
    sprintf(alter_force_text, "alter bow force: %.3f", alter_force);
    actions_file->comment(alter_force_text);
    actions.bow_force *= pow(m_K[m_st][m_dyn], alter_force);

    if (!begin.ignore_finger) {
        finger();
    }

    // number of hops
    int main_hops = seconds/DH; // gets rounded down
    int accel_hops = ceil(fabs(m_velocity_target / (MAX_HAND_ACCEL*DH)));
    int decel_hop;
    if (!end.keep_bow_velocity) {
        decel_hop = main_hops - accel_hops;
    } else {
        decel_hop = main_hops; // don't decelerate?
    }

    int lighten_hop = main_hops; // don't lighten?
    if (end.lighten_bow_force) {
        //decel_hop -= LIGHTEN_NOTE_HOPS;
        lighten_hop = main_hops - LIGHTEN_NOTE_HOPS;
    }
    if (end.let_string_vibrate) {
        //lighten_hop = main_hops - LIGHTEN_NOTE_HOPS;
    }

    m_note_samples = 0;
    m_feedback_adjust_force = false;

    double final_lighten_step = -1;

    for (int i = 0; i < main_hops; i++) {
//        printf("i: %i\n", i);
        hop();

        // start listening to audio?
        if ((!m_feedback_adjust_force) && (m_velocity_target != 0)) {
            if (m_velocity_cutoff_force_adj > 0) {
                if (actions.bow_velocity > m_velocity_cutoff_force_adj) {
                    m_feedback_adjust_force = true;
                }
            } else {
                if (actions.bow_velocity < m_velocity_cutoff_force_adj) {
                    m_feedback_adjust_force = true;
                }
            }
        }
        if (i == decel_hop) {
            m_feedback_adjust_force = false;
            m_velocity_target = 0.0;
        }
        if (i >= lighten_hop) {
            m_feedback_adjust_force = false;
            if (final_lighten_step < 0) {
                if (end.lighten_bow_force) {
                    actions.bow_force *= m_dampen[m_st][m_dyn];
                }
                if (actions.bow_force < 0.1) { // in Newtons
                    final_lighten_step = actions.bow_force / (main_hops-lighten_hop);
                }
            } else {
                actions.bow_force -= final_lighten_step;
                if (actions.bow_force < 0) {
                    actions.bow_force = 0.0;
                }
            }
        }
        /*
        // FIXME: oh god ick
        if (i > lighten_hop) {
            m_feedback_adjust_force = false;
            if (end.let_string_vibrate) {
                actions.bow_force *= LET_VIBRATE;
            } else {
                actions.bow_force *= m_dampen[m_st][m_dyn];
            }
        }
        */
        if (end.physical.string_number >= 0) {
            double x = m_note_samples / (44100.0 * seconds);
            actions.bow_velocity = interpolate(x,
                                               0, begin.physical.bow_velocity,
                                               1, end.physical.bow_velocity);
            actions.bow_bridge_distance = interpolate(x,
                                          0, begin.physical.bow_bridge_distance,
                                          1, end.physical.bow_bridge_distance);
            actions.dynamic = interpolate(x,
                                          0, begin.physical.dynamic,
                                          1, end.physical.dynamic);
            m_dyn = actions.get_dyn();
        }
    }
    // finish final "half hop"
    int remaining_samples = seconds*44100.0 - m_note_samples;
    // finish final "half hop"
    if (remaining_samples > 0) {
        hop(remaining_samples);
    }

    if ((!end.keep_bow_velocity) || (end.lighten_bow_force)) {
        if (!end.keep_bow_velocity) {
            actions.bow_velocity = 0.0;
        }
        if (end.lighten_bow_force) {
            actions.bow_force = 0.0;
        }
        violin->bow(actions.string_number,
                    actions.bow_bridge_distance,
                    actions.bow_force,
                    actions.bow_velocity);
        actions_file->bow(m_total_samples*dt, actions.string_number,
                          actions.bow_bridge_distance, actions.bow_force,
                          actions.bow_velocity,
                          m_bow_pos_along);
    }
//zz
}

void ViviController::bowStop() {
    actions.bow_velocity = 0.0;
    actions.bow_force = 0.0;
    violin->bow(actions.string_number,
                actions.bow_bridge_distance,
                actions.bow_force,
                actions.bow_velocity);
    actions_file->bow(m_total_samples*dt, actions.string_number,
                      actions.bow_bridge_distance, actions.bow_force,
                      actions.bow_velocity,
                      m_bow_pos_along);
}

inline void ViviController::hop_passive(int num_samples)
{
    short *buf = wavfile->request_fill(num_samples);
    violin->wait_samples(buf, num_samples);
    m_total_samples += num_samples;
    m_note_samples  += num_samples;
    // TODO: what else do I need?
}

inline void ViviController::hop(int num_samples) {
    assert((m_st >= 0) && (m_st < NUM_STRINGS));
    assert((m_dyn >= 0) && (m_dyn < NUM_DYNAMICS));
    // approach target velocity
    const double dv = m_velocity_target - actions.bow_velocity;
    if (dv > MAX_HAND_ACCEL*DH) {
        actions.bow_velocity += MAX_HAND_ACCEL*DH;
    } else {
        if (dv < -MAX_HAND_ACCEL*DH) {
            actions.bow_velocity -= MAX_HAND_ACCEL*DH;
        } else {
            actions.bow_velocity += dv;
        }
    }
    // jitter
    actions.bow_velocity += norm_bounded(0, fabs(actions.bow_velocity)
                                         * VELOCITY_STDDEV);
    actions.bow_force += norm_bounded(0, actions.bow_force * FORCE_STDDEV);
    violin->bow(actions.string_number,
                actions.bow_bridge_distance,
                actions.bow_force,
                actions.bow_velocity);
    ears[m_st][m_dyn]->set_extra_params(
        m_st, actions.finger_position);

    actions_file->bow(m_total_samples*dt, actions.string_number,
                      actions.bow_bridge_distance, actions.bow_force,
                      actions.bow_velocity,
                      m_bow_pos_along);
    short *buf = wavfile->request_fill(num_samples);
    violin->wait_samples(buf, num_samples);
    // before processing
    m_total_samples += num_samples;
    m_note_samples  += num_samples;

    m_bow_pos_along += num_samples*dt*actions.bow_velocity;

    // don't bother listening to a too-short note snippet, or if
    // we don't care about adjusting the force
    if ((num_samples < HOPSIZE) || (m_feedback_adjust_force==false)) {
        cats_file->category(m_total_samples*dt, CATEGORY_NULL);
        return;
    }
    ears[m_st][m_dyn]->listenShort(buf);
    double cat = ears[m_st][m_dyn]->getClass();
    /*
    // write cat to file if speed is enough
    // don't write if note hasn't settled yet
    if (m_note_samples < MIN_SETTLE_HOPS * HOPSIZE) {
        cats_file->category(m_total_samples*dt, CATEGORY_NULL);
    } else {
        if (m_velocity_cutoff_force_adj > 0) {
            if (actions.bow_velocity > m_velocity_cutoff_force_adj) {
                cats_file->category(m_total_samples*dt, cat);
            } else {
                cats_file->category(m_total_samples*dt, CATEGORY_NULL);
            }
        } else {
            if (actions.bow_velocity < m_velocity_cutoff_force_adj) {
                cats_file->category(m_total_samples*dt, cat);
            } else {
                cats_file->category(m_total_samples*dt, CATEGORY_NULL);
            }
        }
    }
    */
    // write to file
    cats_file->category(m_total_samples*dt, cat);
    if (cat == CATEGORY_NULL) {
        //cout<<0<<'\t'<<0<<'\t'<<actions.bow_force;
        return;
    }
    // record cat, calculate cat_avg
    cats[cats_index] = cat;
    cats_index++;
    if (cats_index == CATS_MEAN_LENGTH) {
        cats_index = 0;
    }
    // adjust based on average
    double cat_avg = 0.0;
    for (int i=0; i<CATS_MEAN_LENGTH; i++) {
        cat_avg += cats[i];
    }
    cat_avg /= CATS_MEAN_LENGTH;
    // adjust bow force
    //cout<<cat<<'\t'<<cat_avg<<'\t'<<actions.bow_force;
    actions.bow_force *= pow(m_K[m_st][m_dyn], -cat_avg);
    //cout<<'\t'<<m_K[m_st][m_dyn]<<'\t'<<actions.bow_force<<endl;

}

void ViviController::comment(const char *text) {
    assert(actions_file != NULL);
    actions_file->comment(text);
    // we don't have a cats_file when doing basic training
    //assert(cats_file != NULL);
    if (cats_file != NULL) {
        cats_file->comment(text);
    }
}

/*
 I haven't thought about it; this just comes from:
 http://en.wikipedia.org/wiki/Linear_interpolation
*/
inline double ViviController::interpolate(const double x,
        const double x0, const double y0,
        const double x1, const double y1)
{
    if ((x1-x0) == 0) {
        return y0;
    } else {
        return y0 + (x-x0)*(y1-y0)/(x1-x0);
    }
}


void ViviController::make_dampen(NoteBeginning begin,
                                 double damp, int hops_settle, int hops_reduce, int hops_wait,
                                 const char *filename)
{
    NoteEnding end;
    end.keep_bow_velocity = true;
    filesNew(filename);
    // get note going
    note(begin, hops_settle*dh, end);

    m_velocity_target = 0.0;
    m_feedback_adjust_force = false;
    for (int i=0; i<hops_reduce; i++) {
        actions.bow_force *= damp;
        hop();
    }
    actions.bow_force = 0.0;
    for (int i=0; i<hops_wait; i++) {
        hop();
    }

    filesClose();
}


