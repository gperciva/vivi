
#include "vivi_controller.h"
#include <time.h>
#include <math.h>

//#include "artifastring/violin_instrument.h"
#include "artifastring/monowav.h"
#include "actions_file.h"

// used in normal hops
const double VELOCITY_STDDEV = 0.01;
const double FORCE_STDDEV = 0.01;
const double MAX_HAND_ACCEL = 5.0; // m/s
const double DH = EARS_HOPSIZE * dt;

// used in basic
const double BASIC_VELOCITY_STDDEV = 0.02;
const double BASIC_FORCE_STDDEV = 0.02;

// used elsewhere
const double MIN_VELOCITY_FACTOR = 0.5;


const double LIGHTEN_FACTOR = 0.5;
const int LIGHTEN_NOTE_HOPS = 8; // FIXME: fix

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
        cats[i] = -1;
    }
    cats_index = 0;

    m_bow_pos_along = 0.1; // default near frog?
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
        actions_file->wait(total_samples*dt);
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
    total_samples = 0;
    return true;
}

void ViviController::basic(PhysicalActions actions_get, double seconds,
                           double skip_seconds, const char *filenames_base)
{
    // must do this first, otherwise actions.bow_velocity gets overwritten!
    filesNew(filenames_base);

    actions.string_number = actions_get.string_number;
    actions.finger_position = actions_get.finger_position;
    actions.bow_force = actions_get.bow_force;
    actions.bow_bridge_distance = actions_get.bow_bridge_distance;
    // ok to copy bow_velocity here.
    actions.bow_velocity = actions_get.bow_velocity;

    int dyn = round(actions_get.dynamic);
    char note_search_params[MAX_LINE_LENGTH];
    sprintf(note_search_params, "basic\tst %i\tdyn %i\tfinger_midi %.3f",
            actions.string_number, dyn, actions.finger_position);
    actions_file->comment(note_search_params);

    const double orig_force = actions.bow_force;
    const double orig_velocity = actions.bow_velocity;

    actions_file->finger(total_samples*dt, actions.string_number,
                         actions.finger_position);
    violin->finger(actions.string_number, actions.finger_position);

    // skip, maybe going slightly over given time
    actions_file->skipStart(total_samples*dt);
    short mem_buf[EARS_HOPSIZE];
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
        actions_file->bow(total_samples*dt, actions.string_number,
                          actions.bow_bridge_distance, actions.bow_force,
                          actions.bow_velocity,
                          m_bow_pos_along);
        violin->wait_samples(mem_buf, EARS_HOPSIZE);
        total_samples += EARS_HOPSIZE;
    }
    actions_file->skipStop(total_samples*dt);

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
        actions_file->bow(total_samples*dt, actions.string_number,
                          actions.bow_bridge_distance, actions.bow_force,
                          actions.bow_velocity,
                          m_bow_pos_along);
        short *buf = wavfile->request_fill(EARS_HOPSIZE);
        violin->wait_samples(buf, EARS_HOPSIZE);
        total_samples += EARS_HOPSIZE;
    }
    filesClose();
}

void ViviController::rest(double seconds)
{
    actions_file->comment("rest");
    cats_file->comment("rest");
    bowStop();

    actions_file->wait(total_samples*dt);

    note_samples = 0;
    for (int i = 0; i < seconds/DH-1; i++) {
        hop_passive();
    }
    // finish final "half hop"
    int remaining_samples = seconds*44100.0 - note_samples;
    // finish final "half hop"
    if (remaining_samples > 0) {
        hop_passive(remaining_samples);
    }
}

void ViviController::pizz(PhysicalActions actions_get, double seconds)
{
    actions_file->comment("rest");
    cats_file->comment("rest");
    bowStop();

    // set up note parameters
    actions.string_number = actions_get.string_number;
    actions.finger_position = actions_get.finger_position;
    actions.bow_force = actions_get.bow_force;
    actions.bow_bridge_distance = actions_get.bow_bridge_distance;

    actions_file->finger(total_samples*dt, actions.string_number,
                         actions.finger_position);
    violin->finger(actions.string_number, actions.finger_position);
    actions_file->pluck(total_samples*dt, actions.string_number,
                        actions.bow_bridge_distance, actions.bow_force);
    violin->pluck(actions.string_number, actions.bow_bridge_distance,
                  actions.bow_force);

    note_samples = 0;
    for (int i = 0; i < seconds/DH-1; i++) {
        hop_passive();
    }
    // finish final "half hop"
    int remaining_samples = seconds*44100.0 - note_samples;
    // finish final "half hop"
    if (remaining_samples > 0) {
        hop_passive(remaining_samples);
    }

}

void ViviController::note(PhysicalActions actions_get, double seconds,
                          NoteBeginning begin, NoteEnding end,
                        const char *point_and_click)
{
    //actions_get.print();

    // set up note parameters
    actions.string_number = actions_get.string_number;
    actions.bow_bridge_distance = actions_get.bow_bridge_distance;
    if (!begin.ignore_finger) {
        actions.finger_position = actions_get.finger_position;
    }
    if (!begin.keep_bow_force) {
        actions.bow_force = actions_get.bow_force;
    }
    if (begin.set_bow_position_along >= 0) {
        m_bow_pos_along= begin.set_bow_position_along;
    }

    // don't copy bow_velocity!
    m_velocity_target = actions_get.bow_velocity;
    m_velocity_cutoff_force_adj = m_velocity_target * MIN_VELOCITY_FACTOR;
    // other setup
    m_st = actions.string_number;
    m_dyn = round(actions_get.dynamic);

    // write (some) parameters to file
    char note_search_params[MAX_LINE_LENGTH];
    if (point_and_click == NULL) {
    sprintf(note_search_params, "note\tst %i\tdyn %i\tfinger_midi %.3f",
            m_st, m_dyn, actions.finger_position);
            } else {
    sprintf(note_search_params, "note\tst %i\tdyn %i\tfinger_midi %.3f %s",
            m_st, m_dyn, actions.finger_position, point_and_click);
        }
    actions_file->comment(note_search_params);
    cats_file->comment(note_search_params);

    if (!begin.ignore_finger) {
        actions_file->finger(total_samples*dt, actions.string_number,
                             actions.finger_position);
        violin->finger(actions.string_number, actions.finger_position);
    }

    int lighten_hop = seconds/DH;
    if (end.lighten_bow_force) {
        lighten_hop = seconds/DH - LIGHTEN_NOTE_HOPS;
    }

    note_samples = 0;
    int accel_hops = ceil(fabs(
                              m_velocity_target
                              / (MAX_HAND_ACCEL*DH)));
    int decel_hop;
    if (!end.keep_bow_velocity) {
        decel_hop = seconds/DH - accel_hops;
    } else {
        decel_hop = seconds/DH; // don't decelerate?
    }

    for (int i = 0; i < seconds/DH-1; i++) {
        hop();
        // start deceleration
        if (i > decel_hop) {
            m_velocity_target = 0.0;
        }
        if (i > lighten_hop) {
            actions.bow_force *= LIGHTEN_FACTOR;
        }
    }
    // finish final "half hop"
    int remaining_samples = seconds*44100.0 - note_samples;
    // finish final "half hop"
    if (remaining_samples > 0) {
        hop(remaining_samples);
    }

    if (!end.keep_bow_velocity) {
        bowStop();
    }
//zz
}

inline void ViviController::bowStop() {
    actions.bow_force = 0.0;
    actions.bow_velocity = 0.0;
    violin->bow(actions.string_number,
                actions.bow_bridge_distance,
                actions.bow_force,
                actions.bow_velocity);
    actions_file->bow(total_samples*dt, actions.string_number,
                      actions.bow_bridge_distance, actions.bow_force,
                      actions.bow_velocity,
                      m_bow_pos_along);
}

inline void ViviController::hop_passive(int num_samples)
{
    short *buf = wavfile->request_fill(num_samples);
    violin->wait_samples(buf, num_samples);
    total_samples += num_samples;
    note_samples  += num_samples;
    // TODO: what else do I need?
}

inline void ViviController::hop(int num_samples) {
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

    actions_file->bow(total_samples*dt, actions.string_number,
                      actions.bow_bridge_distance, actions.bow_force,
                      actions.bow_velocity,
                      m_bow_pos_along);
    short *buf = wavfile->request_fill(num_samples);
    violin->wait_samples(buf, num_samples);

    m_bow_pos_along += num_samples*dt*actions.bow_velocity;

    ears[m_st][m_dyn]->listenShort(buf);
    int cat = ears[m_st][m_dyn]->getClass();
    // TODO: sort this out as well
    if (num_samples < EARS_HOPSIZE) {
        total_samples += num_samples;
        note_samples  += num_samples;
        return;
    }
    // write cat to file if speed is enough
    if (m_velocity_cutoff_force_adj > 0) {
        if (actions.bow_velocity > m_velocity_cutoff_force_adj) {
            cats_file->category(total_samples*dt, cat);
        } else {
            cats_file->category(total_samples*dt, CATEGORY_NULL);
        }
    } else {
        if (actions.bow_velocity < m_velocity_cutoff_force_adj) {
            cats_file->category(total_samples*dt, cat);
        } else {
            cats_file->category(total_samples*dt, CATEGORY_NULL);
        }
    }
    // record cat, calculate cat_avg
    cats[cats_index] = cat;
    cats_index++;
    if (cats_index == CATS_MEAN_LENGTH) {
        cats_index = 0;
    }
    double cat_avg = 0.0;
    int cat_ok = 1;
    for (int i=0; i<CATS_MEAN_LENGTH; i++) {
        if (cats[i] < 0) {
            cat_ok = 0;
        }
        cat_avg += cats[i];
    }
    cat_avg /= CATS_MEAN_LENGTH;
    // TODO: sort out this conditional
    if (cat_ok == 1) {
        if (m_velocity_cutoff_force_adj > 0) {
            if (actions.bow_velocity > m_velocity_cutoff_force_adj) {
                // adjust bow force
                actions.bow_force *= pow(m_K[m_st][m_dyn], 2-cat_avg);
            }
        } else {
            if (actions.bow_velocity < m_velocity_cutoff_force_adj) {
                actions.bow_force *= pow(m_K[m_st][m_dyn], 2-cat_avg);
            }
        }
    }

    // after processing
    total_samples += num_samples;
    note_samples  += num_samples;
}

void ViviController::comment(const char *text) {
    if (actions_file != NULL) {
        actions_file->comment(text);
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

