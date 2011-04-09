
#include "vivi_controller.h"
#include <time.h>

// used in normal hops
const double VELOCITY_STDDEV = 0.01;
const double FORCE_STDDEV = 0.01;
const double MAX_HAND_ACCEL = 5.0; // m/s
const double DH = EARS_HOPSIZE * dt;

// used in basic
const double BASIC_VELOCITY_STDDEV = 0.02;
const double BASIC_FORCE_STDDEV = 0.02;


ViviController::ViviController(const char *train_dir) {
    strncpy(m_train_dir, train_dir, 255);

    // setup random generator
    const gsl_rng_type * T = gsl_rng_default;
    random = gsl_rng_alloc (T);

    violin = new ViolinInstrument();
    wavfile = NULL;
    actions_file = NULL;
    for (int i=0; i<NUM_STRINGS; i++) {
        for (int j=0; j<NUM_STRINGS; j++) {
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
        for (int j=0; j<NUM_STRINGS; j++) {
            if (ears[i][j] != NULL) {
                delete ears[i][j];
            }
        }
    }
}

void ViviController::reset() {
    const long seed = time(NULL) * getpid();
    gsl_rng_set(random, seed);
    violin->reset();
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
    }
    if (actions_file != NULL) {
        delete actions_file;
    }
}


bool ViviController::filesNew(const char *filenames_base) {
    filesClose();
    // wav file
    char filename[512];
    strncpy(filename, filenames_base, 511);
    strncat(filename, ".wav", 511);
    wavfile = new MonoWav(filename);
    // actions file
    strncpy(filename, filenames_base, 511);
    strncat(filename, ".actions", 511);
    actions_file = new ActionsFile(filename);
    return true;
}

void ViviController::basic(PhysicalActions actions_get, double seconds,
                           double skip_seconds)
{
    actions = actions_get;
    actions_file->finger(total_samples*dt, actions.string_number,
                         actions.finger_position);

    // skip, maybe going slightly over given time
    actions_file->skipStart(total_samples*dt);
    short mem_buf[EARS_HOPSIZE];
    for (int i=0; i<seconds*44100.0/EARS_HOPSIZE; i++) {
        actions.bow_force = norm_bounded(actions.bow_force,
                                         BASIC_FORCE_STDDEV * actions.bow_force);
        actions.bow_velocity = norm_bounded(actions.bow_velocity,
                                            BASIC_VELOCITY_STDDEV * actions.bow_velocity);

        violin->bow(actions.string_number,
                    actions.bow_bridge_distance,
                    actions.bow_force,
                    actions.bow_velocity);
        actions_file->bow(total_samples*dt, actions.string_number,
                          actions.bow_bridge_distance, actions.bow_force,
                          actions.bow_velocity);
        violin->wait_samples(mem_buf, EARS_HOPSIZE);
    }
    actions_file->skipStop(total_samples*dt);

    // actual note, maybe going slightly over given time
    for (int i=0; i<seconds*44100.0/EARS_HOPSIZE; i++) {
        actions.bow_force = norm_bounded(actions.bow_force,
                                         BASIC_FORCE_STDDEV * actions.bow_force);
        actions.bow_velocity = norm_bounded(actions.bow_velocity,
                                            BASIC_VELOCITY_STDDEV * actions.bow_velocity);

        violin->bow(actions.string_number,
                    actions.bow_bridge_distance,
                    actions.bow_force,
                    actions.bow_velocity);
        actions_file->bow(total_samples*dt, actions.string_number,
                          actions.bow_bridge_distance, actions.bow_force,
                          actions.bow_velocity);
        short *buf = wavfile->request_fill(EARS_HOPSIZE);
        violin->wait_samples(buf, EARS_HOPSIZE);
    }
}

void ViviController::note(PhysicalActions actions_get, double seconds)
{
    printf("STUB for note()\n");
    actions = actions_get;

    note_samples = 0;

    actions_file->finger(total_samples*dt, actions.string_number,
                         actions.finger_position);

    for (int i=0; i<seconds*44100.0/EARS_HOPSIZE; i++) {
        hop();
    }
}

inline void ViviController::hop(unsigned int num_samples) {
    printf("STUB for hop()\n");
    // approach target velocity
    const double dv = target_vel - actions.bow_velocity;
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
    actions.bow_velocity += norm_bounded(0,
                                         fabs(actions.bow_velocity) * VELOCITY_STDDEV);
    actions.bow_force += norm_bounded(0,
                                      actions.bow_force * FORCE_STDDEV);
    violin->bow(actions.string_number,
                actions.bow_bridge_distance,
                actions.bow_force,
                actions.bow_velocity);
//    ears[dyn]->set_extra_params(bow_st, finger);

    actions_file->bow(total_samples*dt, actions.string_number,
                      actions.bow_bridge_distance, actions.bow_force,
                      actions.bow_velocity);
    short *buf = wavfile->request_fill(num_samples);
    violin->wait_samples(buf, num_samples);
    total_samples += num_samples;
    note_samples += num_samples;

    //ears[dyn]->listenShort(buf);
    //cat = ears[dyn]->getClass();
}


