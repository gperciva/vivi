
#include "vivi_controller.h"
#include <time.h>
#include <math.h>

#include "artifastring/monowav.h"
#include "artifastring/actions_file.h"

//#define PRINT_DEBUG

#define PITCH_PID

//#define PRINT_PITCH

//#define NO_BOW_ACCEL


//#define NDEBUG
#include <assert.h>

#include <algorithm>

#define SSTR( x ) dynamic_cast< std::ostringstream & >( \
        ( std::ostringstream() << std::dec << x ) ).str()

using namespace std;

#include <pthread.h>
static pthread_mutex_t vivi_mutex;

// used in normal hops
//const double VELOCITY_STDDEV = 0.01;
//const double FORCE_STDDEV = 0.01;
const double VELOCITY_STDDEV = 0.0;
const double FORCE_STDDEV = 0.0;
//const double FINGER_STDDEV = 0.001;

const double ACCELS[3] = { 10.0, 7.5, 5.0 };
//const double ACCELS[3] = { 20.0, 7.5, 5.0 };
//const double MAX_HAND_ACCEL = 10.0; // m/s/s   // for violin
//const double MAX_HAND_ACCEL = 10.0; // m/s/s   // for violin
//const double MAX_HAND_ACCEL = 8.0; // m/s/s
const double dt = 1.0 / ARTIFASTRING_INSTRUMENT_SAMPLE_RATE;

//const int ATTACK_WAITS[3] = { 0, 2, 4 };
const int ATTACK_WAITS[3] = { 0, 0, 0 };

// used in basic
const double BASIC_VELOCITY_STDDEV = 0.02;
const double BASIC_FORCE_STDDEV = 0.02;

// don't listen to sound until this percent of speed is reached
const double MIN_VELOCITY_FACTOR = 0.90;

const double TOO_SMALL_TO_CARE_ABOUT = 1.0;

// don't listen to sound until this many hops have passed
//const int MIN_SETTLE_HOPS = 4;


const double LET_VIBRATE = 0.5;
const int DAMPEN_HOPS = 2; // magic number for hops

ViviController::ViviController(int instrument_type,
                               int instrument_number)
{
    assert(instrument_type >= 0);
    assert(instrument_type <= 2);

    m_inst_type = (int) instrument_type;
    m_inst_num = instrument_number;

    //printf("make inst %i\tnum%i\n", instrument_type, instrument_number);
    // critical section --------------
    pthread_mutex_lock(&vivi_mutex);
    // always used classes
    violin = new ArtifastringInstrument((InstrumentType) instrument_type, instrument_number);
    pthread_mutex_unlock(&vivi_mutex);
    // ------------- critical section end
    // setup random generator
    const gsl_rng_type * T = gsl_rng_default;
    random = gsl_rng_alloc (T);
    const long seed = time(NULL) * getpid();
    gsl_rng_set(random, seed);


    max_hand_accel = ACCELS[instrument_type];
    wavfile = NULL;
    force_file = NULL;
    actions_file = NULL;
    cats_file = NULL;
    for (int i=0; i<NUM_STRINGS; i++) {
        ears[i] = NULL;
        string_audio_file_int[i] = NULL;
        string_force_file_int[i] = NULL;
    }
    reset();
    pitch_integral = 0.0;
}


ViviController::~ViviController() {
    gsl_rng_free(random);
    filesClose();
    delete violin;
    for (int i=0; i<NUM_STRINGS; i++) {
        if (ears[i] != NULL) {
            delete ears[i];
        }
    }
}

void ViviController::reset(bool keep_files) {
//void ViviController::reset() {
    if (keep_files) {
    } else {
        filesClose();
    }
    //filesClose();

    violin->reset();

    actions.string_number = 0;
    actions.finger_position = 0;
    actions.bow_bridge_distance = 0;
    actions.bow_force = 0;
    actions.bow_velocity = 0;

    reset_arrays();

    m_bow_pos_along = 0.1; // default near frog?
    m_feedback_adjust_force = false;
    note_end = 0;
    m_note_samples = 0;
    m_cats_wait_hops = 0;

    note_first_alter_hop = 0;
    note_first_reduction = 0;
}

void ViviController::reset_arrays() {
    cats_index = 0;
    for (int i=0; i<CATS_LENGTH; i++) {
        cats[i] = CATEGORY_WAIT;
        //cats[i] = 0;
    }
    pitch_index = 0;
    for (int i=0; i<PITCH_MEANS; i++) {
        pitches[i] = PITCH_NULL; // neutral
    }
}

Ears* ViviController::getEars(int st) {
    if (ears[st] == NULL) {
        ears[st] = new Ears(m_inst_type, m_inst_num, !REGRESSION);
    }
    return ears[st];
}

bool ViviController::load_ears_training(int st, const char *training_file)
{
    Ears *my_ears = getEars(st);
    if (training_file != NULL) {
        // TODO: replace with const char *
        my_ears->set_predict_buffer(training_file);
        int stabilization_delay = my_ears->get_stabilization_delay();
        ticks_attack = stabilization_delay + ceil(MIN_ATTACK_TIME * SAMPLE_RATE / HOPSIZE);
        ticks_attack = 1;
    }
    return true;
}

void ViviController::load_dyn_parameters(int st, int dyn,
        const char *vivi_filename)
{
    //cout<<"loading from: "<<vivi_filename<<endl;
    ControllerParams *dyn_params = new ControllerParams(vivi_filename);
    dyn_params->load_file();
    for (int i=0; i<3; i++) {
        m_K[st][dyn][i] = dyn_params->stable_K[i];
    }
    m_dampen_normal[st][dyn] = dyn_params->dampen_normal;
    //m_dampen_slur[st][dyn] = dyn_params->dampen_slur;
    delete dyn_params;
}

void ViviController::set_stable_K(int st, int dyn, int fmi, double K)
{
    m_K[st][dyn][fmi] = K;
}

void ViviController::set_dampen(int st, int dyn, double dampen_normal)
{
    m_dampen_normal[st][dyn] = dampen_normal;
    //m_dampen_slur[st][dyn] = dampen_slur;
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
    if (force_file != NULL) {
        delete force_file;
        force_file = NULL;
    }
    for (int st=0; st<NUM_STRINGS; st++) {
        delete string_audio_file_int[st];
        string_audio_file_int[st] = NULL;
        delete string_force_file_int[st];
        string_force_file_int[st] = NULL;
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
    wavfile = new MonoWav(filename.c_str(), SAMPLE_RATE, SAMPLE_RATE);
    filename.assign(filenames_base);
    filename.append(".forces.wav");
    force_file = new MonoWav(filename.c_str(), HAPTIC_SAMPLE_RATE, HAPTIC_SAMPLE_RATE);
    // string files
    for (int st=0; st<NUM_STRINGS; st++) {
        filename.assign(filenames_base);
        filename.append("-s");
        filename.append(SSTR(st));
        filename.append(".wav");
        string_audio_file_int[st] = new MonoWav(filename.c_str(),
            SAMPLE_RATE, SAMPLE_RATE, true);
        filename.assign(filenames_base);
        filename.append("-s");
        filename.append(SSTR(st));
        filename.append(".forces.wav");
        string_force_file_int[st] = new MonoWav(filename.c_str(),
            SAMPLE_RATE, SAMPLE_RATE, true);
    }
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

#if 0
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
        short *force_buf = force_file->request_fill(
                               HOPSIZE / HAPTIC_DOWNSAMPLE_FACTOR);
        violin->wait_samples_forces(buf, force_buf, HOPSIZE);
        m_total_samples += HOPSIZE;
    }
}
#endif

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
    int remaining_samples = seconds*ARTIFASTRING_INSTRUMENT_SAMPLE_RATE - m_note_samples;
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
    //violin->pluck(actions.string_number, actions.bow_bridge_distance,
    //             actions.bow_force*0.5);
    if (actions.finger_position == 0) {
        violin->pluck(actions.string_number, 0.37,
                  actions.bow_force*0.2);
    } else {
        violin->pluck(actions.string_number, 0.37,
                  actions.bow_force*0.3);
    }

    m_note_samples = 0;
    for (int i = 0; i < seconds/DH-1; i++) {
        hop_passive();
    }
    // finish final "half hop"
    int remaining_samples = seconds*ARTIFASTRING_INSTRUMENT_SAMPLE_RATE - m_note_samples;
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
        /*
        if (begin.physical.finger_position == 0) {
            actions.finger_position = 0;
        } else {
            actions.finger_position = norm_bounded(
                                        begin.physical.finger_position,
                                        FINGER_STDDEV);
        }
        */
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

    // FIXME: experiment
    actions.bow_velocity = 1.0*m_velocity_target;
    
    // other setup
    m_st = actions.string_number;
    m_dyn = round(begin.physical.dynamic);
}

void ViviController::note_write_actions(NoteBeginning begin,
                                        NoteEnding end, const char *point_and_click)
{
    char note_search_params[MAX_LINE_LENGTH];
    if (point_and_click == NULL) {
        sprintf(note_search_params, "note\tinst %i\tst %i\tdyn %i\tfinger_midi %.3f",
                m_inst_type,
                m_st, m_dyn,
                pos2midi(actions.finger_position));
    } else {
        sprintf(note_search_params, "note\tinst %i\tst %i\tdyn %i\tfinger_midi %.3f %s",
                m_inst_type,
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
                          double alter_force,
                          short *audio_buffer)
{
    //printf("--- note ----\n");
    assert((begin.physical.string_number >= 0) &&
           (begin.physical.string_number < NUM_STRINGS));
    assert((begin.physical.dynamic >= 0) &&
           (begin.physical.dynamic < NUM_DYNAMICS));

    note_setup_actions(begin);
    note_write_actions(begin, end, point_and_click);

    char alter_force_text[MAX_LINE_LENGTH];
    sprintf(alter_force_text, "alter bow force: %.3f", alter_force);
    actions_file->comment(alter_force_text);

    midi_target = begin.midi_target;
    //actions.bow_force *= pow(m_K[m_st][m_dyn], alter_force);
    actions.bow_force *= alter_force;
    //cout<<begin.physical.bow_force<<"\t"<<alter_force<<endl;

    if (!begin.keep_bow_force) {
        //double K = m_K[m_st][m_dyn];
        //note_first_alter_hop = 3;
        note_first_alter_hop = ATTACK_WAITS[m_inst_type];
        //note_first_reduction = actions.bow_force * (K-1.0)*0.2;
        reset_arrays();
    }

    // hop_K
    if (begin.physical.finger_position < 0.056) {
        hop_K = m_K[m_st][m_dyn][0];
    }
    else if (begin.physical.finger_position > 0.29) {
        hop_K = m_K[m_st][m_dyn][2];
    } else {
        double low = m_K[m_st][m_dyn][1];
        double high = m_K[m_st][m_dyn][2];
        hop_K = interpolate(begin.physical.finger_position,
            0.056, low, 0.29, high);
    }
    //cout<<hop_K<<endl;


    if (!begin.ignore_finger) {
        finger();
    }
    if (!begin.keep_ears) {
        ears[m_st]->reset();
    }

    // number of hops
    int main_hops = seconds/DH; // gets rounded down
    int accel_hops = ceil(fabs(m_velocity_target / (max_hand_accel*DH)));
    int decel_hop;
    if (!end.keep_bow_velocity) {
        decel_hop = main_hops - accel_hops+1;
    } else {
        decel_hop = main_hops; // don't decelerate?
    }

    double dampen_factor = 0.0;
    int lighten_hop = main_hops; // don't lighten?
    if (end.lighten_bow_force) {
        //decel_hop -= DAMPEN_HOPS;
        lighten_hop = main_hops - DAMPEN_HOPS;
        // we need to stop the bow before lightening the bow force
        dampen_factor = m_dampen_normal[m_st][m_dyn];
        if (!end.keep_bow_velocity) {
            decel_hop -= DAMPEN_HOPS;
        }
    }
    //if (end.let_string_vibrate) {
        //lighten_hop = main_hops - DAMPEN_HOPS;
    //}

    m_note_samples = 0;
    m_feedback_adjust_force = false;
    note_end = 0;
    m_cats_wait_hops = 0;

    // FIXME: experiment
    //m_feedback_adjust_force = true;

    for (int i = 0; i < main_hops; i++) {
        //printf("i: %i\n", i);
        hop(HOPSIZE, audio_buffer);

        // FIXME: experiment
        //if (i == 10) {
        //    actions.bow_velocity = m_velocity_target;
        //}

        //printf("bf: %g\n", actions.bow_force);
        if (end.midi_target > 0) {
            int GLISS_STEADY_BEGIN = 8;
            int GLISS_STEADY_END = 8;
            double gliss_along = double(i-GLISS_STEADY_BEGIN)
                / (main_hops - GLISS_STEADY_BEGIN - GLISS_STEADY_END);
            if (gliss_along < 0.0) {
                gliss_along = 0.0;
            }
            if (gliss_along > 1.0) {
                gliss_along = 1.0;
            }
            midi_target = interpolate(gliss_along,
                                      0.0, begin.midi_target,
                                      1.0, end.midi_target);
            /*
            printf("%.3g\t%.3g\t%.3g\t%.4g\n",
                begin.midi_target, end.midi_target,
                gliss_along, midi_target);
            */
        }

        // start listening to audio?
        if ((!m_feedback_adjust_force) && (m_velocity_target != 0)) {
            if (m_velocity_cutoff_force_adj > 0) {
                if (actions.bow_velocity > m_velocity_cutoff_force_adj) {
                    m_feedback_adjust_force = true;
                    if (!begin.keep_bow_force) {
                        m_cats_wait_hops = ticks_attack;
                        //note_first_alter_hop = 2;
                    }
                }
            } else {
                if (actions.bow_velocity < m_velocity_cutoff_force_adj) {
                    m_feedback_adjust_force = true;
                    if (!begin.keep_bow_force) {
                        m_cats_wait_hops = ticks_attack;
                        //note_first_alter_hop = 2;
                    }
                }
            }
        }
        if (i == decel_hop) {
            m_feedback_adjust_force = false;
            m_velocity_target = 0.0;
            note_end = 1;
        }
        if (i >= lighten_hop) {
            m_feedback_adjust_force = false;
            actions.bow_force *= dampen_factor;
        }
        // TODO: oh god ick
        //if (i > lighten_hop) {
        //    m_feedback_adjust_force = false;
        //    if (end.let_string_vibrate) {
        //        actions.bow_force *= LET_VIBRATE;
        //    } else {
        //        actions.bow_force *= m_dampen[m_st][m_dyn];
        //    }
        //}
        
        if (end.physical.string_number >= 0) {
            double x = m_note_samples / (
                           ARTIFASTRING_INSTRUMENT_SAMPLE_RATE * seconds);
            m_velocity_target = interpolate(x,
                                               0, begin.physical.bow_velocity,
                                               1, end.physical.bow_velocity);
            actions.bow_bridge_distance = interpolate(x,
                                          0, begin.physical.bow_bridge_distance,
                                          1, end.physical.bow_bridge_distance);
            actions.dynamic = interpolate(x,
                                          0, begin.physical.dynamic,
                                          1, end.physical.dynamic);
            m_dyn = actions.get_dyn();
            if (!end.keep_bow_velocity) {
                if (i > decel_hop) {
                    m_velocity_target = 0.0;
                }
            }
        }
    }
    // finish final "half hop"
    int remaining_samples = seconds*ARTIFASTRING_INSTRUMENT_SAMPLE_RATE - m_note_samples;
    if ((remaining_samples % 2 != 0)) {
        remaining_samples -= 1;
    }
    // finish final "half hop"
    if (remaining_samples > 0) {
        hop(remaining_samples, audio_buffer);
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

void ViviController::continuous(short *audio_buffer, PhysicalActions physical,
                                double midi_target_get, bool run)
{
    m_feedback_adjust_force = true;

    // ASSUME: the first call to this function will always contain
    // a valid physical (i.e. string_number >= 0)
    if (physical.string_number < 0) {
        hop(HOPSIZE, audio_buffer);
    } else {
        actions.string_number = physical.string_number;
        actions.bow_bridge_distance = physical.bow_bridge_distance;
        actions.bow_force = physical.bow_force;
        actions.finger_position = physical.finger_position;

        // don't copy bow_velocity; put it in m_velocity_target instead
        m_velocity_target = physical.bow_velocity;
        m_velocity_cutoff_force_adj = m_velocity_target * MIN_VELOCITY_FACTOR;

        // other setup
    m_st = physical.string_number;
    m_dyn = round(physical.dynamic);
    if (actions.finger_position < 0.056) {
        hop_K = m_K[m_st][m_dyn][0];
    }
    else if (actions.finger_position > 0.29) {
        hop_K = m_K[m_st][m_dyn][2];
    } else {
        double low = m_K[m_st][m_dyn][1];
        double high = m_K[m_st][m_dyn][2];
        hop_K = interpolate(actions.finger_position,
            0.056, low, 0.29, high);
    }


        midi_target = midi_target_get;
        finger();

        if (run) {
        // reset pitch detection
        int alter_pitch_index = (pitch_index-1 + PITCH_MEANS) % PITCH_MEANS;
        pitches[ alter_pitch_index ] = PITCH_NULL;
        hop(HOPSIZE, audio_buffer);
        } else {
        hop(0, audio_buffer);
        }
    }
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
    short *force_buf = force_file->request_fill(num_samples);
    violin->wait_samples_forces(buf, force_buf, num_samples);
    m_total_samples += num_samples;
    m_note_samples  += num_samples;
    // TODO: what else do I need?
}

inline void ViviController::pitch_pid()
{
    if (actions.finger_position == 0) {
        return;
    }
#if 0
    double working[PITCH_MEANS];
    for (int i=0; i<PITCH_MEANS; i++) {
        if ((pitches[i] == PITCH_NULL) || (pitches[i] == 0.0)) {
#ifdef PRINT_PITCH
        printf("nan\n");
#endif
            return;
        }
        double err = midi_target - pitches[i];
        //cout<<midi_target<<"\t"<<pitches[i]<<endl;
        // take care of octave errors?
        while (err > 6) {
            err -= 12;
        }
        while (err < -6) {
            err += 12;
        }
        working[i] = err;
        //printf("%.3f  ", err);
    }
    //printf("\n");

    // yes, this means it's less at the beginning
    double rel_pitch = 0.0;
    for (int i=0; i<PITCH_MEANS; i++) {
        rel_pitch += working[i];
    }
    rel_pitch /= PITCH_MEANS;
    //printf("---\n");
#else
    double rel_pitch = pitches_median(midi_target);
    if (rel_pitch == PITCH_NULL) {
#ifdef PRINT_PITCH
        printf("nan\n");
#endif
            return;
    }
    //double rel_pitch = midi_target - pitch;
        // take care of octave rel_pitchors?
        while (rel_pitch > 6) {
            rel_pitch -= 12;
        }
        while (rel_pitch < -6) {
            rel_pitch += 12;
        }


#endif
    /*
        double absolute_deviation = 0.0;
        for (int i=0; i<PITCH_MEANS; i++) {
            double err = pitches[i] - pitch;
            printf("%.3f  ", err);
            absolute_deviation += fabs(err);
        }
        printf("\n");
        double rel_dev = absolute_deviation / pitch;

        printf("%.2f\t%.2f\t%.3g\n", midi_target, pitch, rel_dev);
        if (rel_dev > 0.01) {
            cout<<"bail 1"<<endl;
            return;
        }
    */

#ifdef PRINT_PITCH
    printf("%g\n", -rel_pitch);
#endif

    //double rel_pitch = midi_target - pitch;
    if (fabs(rel_pitch) < 0.01) {
        //cout<<"bail 2"<<endl;
        return;
    }
    //printf("%.3f\t%.2g\t%.3f\n", pitch, rel_dev, rel_pitch);
    //if (abs(rel_pitch) < 0.01) {
    //    return;
    //}
    // pid part
    double e = rel_pitch;
    //pitch_integral += e; // measure these in hops
    double Kp = 1e-2;
    actions.finger_position += Kp*e;
    finger();
}

inline double ViviController::cats_mean()
{
    double cat_sum = 0.0;
    int cat_count = 0;
    for (int i=0; i<CATS_LENGTH; i++) {
        if ((cats[i] != CATEGORY_WAIT) and (cats[i] != CATEGORY_NULL)) {
            cat_sum += cats[i];
            cat_count++;
        }
    }
    double cat_mean = 0.0;
    if (cat_count > 0) {
        cat_mean = cat_sum / cat_count;
    }
    return cat_mean;
}

inline double ViviController::pitches_median(double midi_target)
{
    double to_sort[PITCH_MEANS];
#if 0
    for (int i=0; i<CATS_LENGTH; i++) {
        cout<<cats[i]<<"\t";
    }
    cout<<endl;
#endif
    for (int i=0; i<PITCH_MEANS; i++) {
        if ((pitches[i] != PITCH_NULL) and (pitches[i] != 0)) {
            double rel_pitch = midi_target - pitches[i];
        while (rel_pitch > 6) {
            rel_pitch -= 12;
        }
        while (rel_pitch < -6) {
            rel_pitch += 12;
        }
        to_sort[i] = rel_pitch;
        } else {
            return PITCH_NULL;
        }
    }
    sort(&to_sort[0], &to_sort[PITCH_MEANS]);
#if 0
    for (int i=0; i<PITCH_MEANS; i++) {
        cout<<to_sort[i]<<"\t";
    }
    cout<<endl;
#endif
    //double pitch_median = (to_sort[PITCH_MEANS/2]
    //    + to_sort[(PITCH_MEANS/2)-1])/2.0;
    double pitch_median = to_sort[PITCH_MEANS/2];
    //cout<<pitch_median<<endl;
    /*
    double rel_pitch = 0.0;
    for (int i=1; i<PITCH_MEANS-1; i++) {
        rel_pitch += to_sort[i];
        cout<<to_sort[i]<<"\t";
    }
    rel_pitch /= (PITCH_MEANS-2);
    cout<<endl<<rel_pitch<<endl;
    return rel_pitch;
    */
    return pitch_median;
}

inline double ViviController::cats_median()
{
    double to_sort[CATS_LENGTH];
#if 0
    for (int i=0; i<CATS_LENGTH; i++) {
        cout<<cats[i]<<"\t";
    }
    cout<<endl;
#endif
    for (int i=0; i<CATS_LENGTH; i++) {
        if ((cats[i] != CATEGORY_WAIT) and (cats[i] != CATEGORY_NULL)) {
            to_sort[i] = cats[i];
        } else {
            return CATEGORY_WAIT;
        }
    }
    sort(&to_sort[0], &to_sort[CATS_LENGTH]);
#if 0
    for (int i=0; i<CATS_LENGTH; i++) {
        cout<<to_sort[i]<<"\t";
    }
    cout<<endl;
#endif
    //double cat_median = (to_sort[1] + to_sort[2])/2.0;
    double cat_median = (to_sort[CATS_LENGTH/2] + to_sort[(CATS_LENGTH/2)+1])/2.0;
    //double cat_median = to_sort[CATS_LENGTH/2];
    return cat_median;
}



inline double ViviController::cats_std()
{
    double cat_mean = cats_mean();
    int cat_count = 0;
    double variance = 0.0;
    for (int i=0; i<CATS_LENGTH; i++) {
        if ((cats[i] != CATEGORY_WAIT) and (cats[i] != CATEGORY_NULL)) {
            double err = (cats[i] - cat_mean);
            cat_count++;
            variance += err*err;
        }
    }
    if (cat_count > 1) {
        return sqrt(variance / cat_count);
        //return sqrt(variance / (cat_count-1));
    } else {
        return 0.0;
    }
}


void ViviController::hop(int num_samples, short *audio_buffer)
{
    assert((m_st >= 0) && (m_st < NUM_STRINGS));
    assert((m_dyn >= 0) && (m_dyn < NUM_DYNAMICS));
    //assert( (num_samples % 2) == 0);


    if (actions.bow_force < 0) {
        actions.bow_force = 0;
    }

#if 0
    //cout<<"----"<<endl;
    //cout<<m_velocity_target<<"\t"<<actions.bow_velocity<<endl;
    // approach target velocity
    const double dv = m_velocity_target - actions.bow_velocity;
#ifdef NO_BOW_ACCEL
#else
    const double orig_vel = actions.bow_velocity;
#endif
    //cout<<dv<<endl;

        if (dv > max_hand_accel*DH) {
            actions.bow_velocity += max_hand_accel*DH;
        } else {
            if (dv < -max_hand_accel*DH) {
                actions.bow_velocity -= max_hand_accel*DH;
            } else {
                actions.bow_velocity += dv;
            }
        }
        /*
        // jitter
        const double vel_jitter = norm_bounded(0, fabs(actions.bow_velocity)
                                             * VELOCITY_STDDEV);
        actions.bow_velocity += vel_jitter;
        if (m_feedback_adjust_force) {
            actions.bow_force += norm_bounded(0, actions.bow_force * FORCE_STDDEV);
        }
        */
#ifdef NO_BOW_ACCEL
    violin->bow(actions.string_number,
                actions.bow_bridge_distance,
                actions.bow_force,
                actions.bow_velocity);
    actions_file->bow(m_total_samples*dt, actions.string_number,
                      actions.bow_bridge_distance, actions.bow_force,
                      actions.bow_velocity,
                      m_bow_pos_along);
#else
    const double dv2 = actions.bow_velocity - orig_vel;
    double ab = dv2 > 0 ? max_hand_accel : -max_hand_accel;
    /*
    if (m_feedback_adjust_force) {
        ab = dv2 > 0 ? max_hand_accel/100.0 : -max_hand_accel/100.0;
    } else {
        ab = dv2 > 0 ? max_hand_accel : -max_hand_accel;
    }
    if (fabs(dv2) < 0.001) {
        ab = 0.0;
    }
    */
#endif
#endif

    violin->bow(actions.string_number,
                actions.bow_bridge_distance,
                actions.bow_force,
                actions.bow_velocity);
    actions_file->bow(m_total_samples*dt, actions.string_number,
                      actions.bow_bridge_distance, actions.bow_force,
                      actions.bow_velocity,
                      m_bow_pos_along);
/*
    //cout<<m_velocity_target<<"\t"<<orig_vel<<"\t"<<ab<<endl;
    violin->bow_accel(actions.string_number,
                actions.bow_bridge_distance,
                actions.bow_force,
                actions.bow_velocity,
                ab);
    actions_file->accel(m_total_samples*dt, actions.string_number,
                      actions.bow_bridge_distance, actions.bow_force,
                      actions.bow_velocity,
                      m_bow_pos_along, ab);
*/
    ears[m_st]->set_extra_params(
        m_st,
        actions.finger_position,
        actions.bow_bridge_distance,
        actions.bow_force,
        actions.bow_velocity,
        m_inst_type);

    if (num_samples == 0) {
        return;
    }

    short *buf = wavfile->request_fill(num_samples);
    //short *force_buf = force_file->request_fill(
    //                      num_samples / HAPTIC_DOWNSAMPLE_FACTOR);
    //violin->wait_samples_forces(buf, force_buf, num_samples);
    violin->wait_samples_forces(buf, force_buf_ignore, num_samples);

    for (int st=0; st<NUM_STRINGS; st++) {
        audio_buf_int[st] = string_audio_file_int[st]->request_fill_int(num_samples);
        force_buf_int[st] = string_force_file_int[st]->request_fill_int(num_samples);
        violin->get_string_buffer_int(st,
            audio_buf_int[st], num_samples,
            force_buf_int[st], num_samples);
    }

    /*
    cout<<"# samples, m_st:\t"<<num_samples<<"\t"<<m_st<<endl;
    for (int i=0; i<num_samples; i++) {
        //cout<<audio_buf_int[i]<<endl;
        cout<<force_buf_int[i]<<endl;
    }
    */

    

    if (audio_buffer != NULL) {
        for (int i=0; i<num_samples; i++) {
            audio_buffer[i] = buf[i];
        }
    }
    // before processing
    m_total_samples += num_samples;
    m_note_samples  += num_samples;

    m_bow_pos_along += num_samples*dt*actions.bow_velocity;

    // don't bother listening to a too-short note snippet, or if
    // we don't care about adjusting the force
    if ((num_samples < HOPSIZE)) {
        cats_file->category(m_total_samples*dt, CATEGORY_NULL);
        //cout<<"bail 1\t"<<m_note_samples<<endl;
#ifdef PRINT_DEBUG
    cout<<m_note_samples<<"\t"<<"not complete HOPSIZE"<<endl;
#endif
        return;
    }
    if (m_feedback_adjust_force==false) {
        cats_file->category(m_total_samples*dt, CATEGORY_NULL);
        if (note_end == 0) {
            actions.bow_force = exp( log(actions.bow_force) - 1.0 * hop_K);
        //actions.bow_force -= note_first_reduction;
        }
#ifdef PRINT_PITCH
        printf("nan\n");
#endif
#ifdef PRINT_DEBUG
    cout<<m_note_samples<<"\t"<<"m_feedback_adjust_force"<<endl;
#endif
        return;
    }
    if (note_first_alter_hop > 0) {
        cats_file->category(m_total_samples*dt, CATEGORY_NULL);
        actions.bow_force = exp( log(actions.bow_force) - 1.0 * hop_K);
        //actions.bow_force -= note_first_reduction;
        note_first_alter_hop--;
#ifdef PRINT_PITCH
        printf("nan\n");
#endif
#ifdef PRINT_DEBUG
    cout<<m_note_samples<<"\t"<<"note_alter_first_hop"<<endl;
#endif
        return;
    }
    // TODO: if we divide a note into sub-notes, this can result
    // in a small (less than HOPSIZE) buffer being ignored.
    // I'm not using sub-notes yet, but this should still be
    // fixed.
    //ears[m_st]->listenShort_forces(buf, force_buf);
    ears[m_st]->listenInt_forces(audio_buf_int[m_st], force_buf_int[m_st]);
    double pitch = ears[m_st]->getPitch();
    /*
    if (m_cats_wait_hops > 0) {
        m_cats_wait_hops--;
        cats_file->category(m_total_samples*dt, CATEGORY_WAIT);
        //cout<<"bail 2\t"<<m_note_samples<<endl;
        return;
    }
    */
    /*
     else {
        if (m_inst_type == 1) {
            //m_cats_wait_hops = 1; // produces 2*HOPSIZE
        }
        if (m_inst_type == 2) {
            m_cats_wait_hops = 0; // produces 3*HOPSIZE
        }
    }
    */
    double cat = ears[m_st]->getClass();
    //cout<<cat<<endl;
    if (m_cats_wait_hops > 0) {
        m_cats_wait_hops--;
        cats_file->category(m_total_samples*dt, CATEGORY_WAIT);
        actions.bow_force = exp( log(actions.bow_force) - 1.0 * hop_K);
        //actions.bow_force *= pow(hop_K, -1.0);
#ifdef PRINT_PITCH
        printf("nan\n");
#endif
#ifdef PRINT_DEBUG
    cout<<m_note_samples<<"\t"<<"m_cats_wait_hops"<<endl;
#endif
        return;
        if (cat < 0) {
            cat = 0;
        }
    }
    
    /*
    double cat_orig = cat;
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

    // deal with weirdness
    //const int WEIRDNESS_WAIT = 16;
    //if (cat == CATEGORY_WEIRD) {
        // we want no change of force
            /*
                // instead we reduce the bow velocity
                actions.bow_velocity *= 0.9;
                actions.bow_force *= 1.05;
                cout<<"reduce speed"<<endl;
                for (int i=0; i<CATS_LENGTH; i++) {
                    cats[i] = 0;
                }
                */
    //}
    // write to file
    cats_file->category(m_total_samples*dt, cat);

    if (cat == CATEGORY_NULL) {
        //cout<<0<<'\t'<<0<<'\t'<<actions.bow_force;
#ifdef PRINT_PITCH
        printf("nan\n");
#endif
#ifdef PRINT_DEBUG
    cout<<m_note_samples<<"\t"<<"cat == CATEGORY_NULL"<<endl;
#endif
        return;
    }

    // limit extreme cat
    if (cat > 2*CATEGORIES_EXTREME) {
        cat = 2*CATEGORIES_EXTREME;
    }
    if (cat < -2*CATEGORIES_EXTREME) {
        cat = -2*CATEGORIES_EXTREME;
    }

    // record cat, calculate cat_avg

    //double cat_mean = cats_mean();
    /*
    for (int i=0; i<CATS_LENGTH; i++) {
        cout<<cats[i]<<"\t";
    }
    cout<<endl;
    */

/*
    cats[cats_index] = cat;
    cats_index++;
    if (cats_index == CATS_LENGTH) {
        cats_index = 0;
    }
*/
    //cat = cats_median();
    //double cat_std = cats_std();
/*
    double cat_median = cats_median();
    //cout<<cat<<endl;
    if ((cat_median == CATEGORY_NULL) || (cat_median == CATEGORY_WAIT)) {
        //cout<<0<<'\t'<<0<<'\t'<<actions.bow_force;
        //return;
    } else {
        cat = cat_median;
    }
*/
    /*
    if ((cat_std > 0) && (hop_K > 1.0)) {
        double adjust_K = (1.0 - cat_std);
        //adjust_K = 1.0;
        if (adjust_K < 0.0) {
            adjust_K = 0.0;
        }
        hop_K = 1.0 + (hop_K-1.0) * adjust_K;
        //hop_K = 1.0 + (K-1.0) * (1.0/(1.0+5*cat_std));
    }
    */
    
    
    //double cat_avg = cat;
    //double cat_avg = cat + 0.0*cat_mean;
    //cat_avg = cat_mean;
    //cat_avg = cat;
    
    
    //cout<<cat<<"\t"<<cat_mean<<"\t"<<cat_avg<<endl;
    //zzzzz
    // adjust bow force
#ifdef PRINT_DEBUG
    cout<<m_note_samples<<'\t'<<cat<<'\t'<<actions.bow_force;
    //cout<<cat_std<<'\t'<<hop_K<<"\t"<<actions.bow_force;
#endif

    if (fabs(cat) < TOO_SMALL_TO_CARE_ABOUT) {
        pitches[pitch_index] = pitch;
        pitch_index++;
        if (pitch_index >= PITCH_MEANS) {
            pitch_index = 0;
        }
        if (midi_target > 0) {
#ifdef PITCH_PID
            pitch_pid();
#endif
        }
    } else {
        pitches[pitch_index] = PITCH_NULL;
        pitch_index++;
        if (pitch_index >= PITCH_MEANS) {
            pitch_index = 0;
        }
        //printf("-1\t-1\n");
        //actions.bow_force *= pow(K, -cat_avg);
#ifdef PRINT_PITCH
        printf("nan\n");
#endif
    }
    //cout<<actions.bow_force<<"\t"<<hop_K<<"\t"<<-cat;
    //actions.bow_force *= pow(hop_K, -cat);
    actions.bow_force = exp( log(actions.bow_force) - cat * hop_K);

    //cout<<'\t'<<actions.bow_force<<endl;
#ifdef PRINT_DEBUG
    cout<<'\t'<<actions.bow_force<<"\tnormal";
#endif

    // FIXME: experimental
    //actions.bow_velocity *= (1.0 - 0.03*cat);

#ifdef PRINT_DEBUG
    cout<<"\t"<<actions.bow_velocity;
    cout<<endl;
#endif
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


#if 0
void ViviController::make_dampen(NoteBeginning begin,
                                 double damp, int hops_settle, int hops_reduce, int hops_wait,
                                 const char *filename)
{
    NoteEnding end;
    end.keep_bow_velocity = true;
    //end.keep_bow_velocity = false;
    filesNew(filename);
    // get note going
    const int PRE_STOP = 4;
    //begin.physical.finger_position = 0.123;
    //note(begin, (hops_settle - PRE_STOP)*dh, end);
//    cout<<"end note:\t"<<(0.5 - PRE_STOP*dh)<<endl;
    note(begin, 0.5 - PRE_STOP*dh, end);

    m_feedback_adjust_force = false;
    double stop_force = actions.bow_force;

    for (int i=0; i<PRE_STOP; i++) {
        //double factor = 1.0 - double(i)/PRE_STOP;
        //double factor = 0.0;
        double factor = 0.2;
        actions.bow_force *= factor;
        //actions.bow_force = stop_force * factor;
        //actions.bow_force -= stop_force / PRE_STOP;
//        cout<<factor<<'\t'<<actions.bow_force<<endl;
        hop();
    }
    /*
    stop_force = actions.bow_force;
    for (int i=0; i<PRE_STOP; i++) {
        actions.bow_force -= stop_force / PRE_STOP;
        hop();
    }
    */
    m_velocity_target = 0.0;
    actions.bow_force = 0.0;
    for (int i=0; i<hops_wait; i++) {
        hop();
    }

    filesClose();
}
#endif

