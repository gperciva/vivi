
#include "vivi_controller.h"
#include <time.h>
#include <math.h>

//#include "violin_instrument.h"
#include "monowav.h"
#include "actions_file.h"

// used in normal hops
const double VELOCITY_STDDEV = 0.01;
const double FORCE_STDDEV = 0.01;
const double MAX_HAND_ACCEL = 5.0; // m/s
const double DH = EARS_HOPSIZE * dt;

// used in basic
const double BASIC_VELOCITY_STDDEV = 0.02;
const double BASIC_FORCE_STDDEV = 0.02;


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
    for (unsigned int i=0; i<NUM_STRINGS; i++) {
        for (unsigned int j=0; j<NUM_DYNAMICS; j++) {
            ears[i][j] = NULL;
        }
    }
    reset();
}


ViviController::~ViviController() {
    gsl_rng_free(random);
    filesClose();
    delete violin;
    for (unsigned int i=0; i<NUM_STRINGS; i++) {
        for (unsigned int j=0; j<NUM_DYNAMICS; j++) {
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
}

Ears* ViviController::getEars(unsigned int st, unsigned int dyn) {
	if (ears[st][dyn] == NULL) {
		ears[st][dyn] = new Ears();
	}
	return ears[st][dyn];
}

bool ViviController::load_ears_training(unsigned int st, unsigned int dyn,
		std::string training_file)
{
	if (ears[st][dyn] == NULL) {
		ears[st][dyn] = new Ears();
	}
	// TODO: replace with const char *
	ears[st][dyn]->set_predict_buffer(training_file);
	return true;
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
        delete actions_file;
		actions_file = NULL;
    }
}


bool ViviController::filesNew(const char *filenames_base) {
	reset();
    // wav file
    char filename[512];
    strncpy(filename, filenames_base, 511);
    strncat(filename, ".wav", 511);
    wavfile = new MonoWav(filename);
    // actions file
    strncpy(filename, filenames_base, 511);
    strncat(filename, ".actions", 511);
    actions_file = new ActionsFile(filename);
    // update positions
    total_samples = 0;
    return true;
}

void ViviController::basic(PhysicalActions actions_get, double seconds,
                           double skip_seconds, const char *filenames_base)
{
    filesClose();
    filesNew(filenames_base);

    actions.string_number = actions_get.string_number;
	actions.finger_position = actions_get.finger_position;
	actions.bow_force = actions_get.bow_force;
	actions.bow_bridge_distance = actions_get.bow_bridge_distance;
	// ok to copy bow_velocity here.
	actions.bow_velocity = actions_get.bow_velocity;


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
                          actions.bow_velocity);
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
                          actions.bow_velocity);
        short *buf = wavfile->request_fill(EARS_HOPSIZE);
        violin->wait_samples(buf, EARS_HOPSIZE);
        total_samples += EARS_HOPSIZE;
    }
    filesClose();
}

void ViviController::note(PhysicalActions actions_get,
	double K,
	double seconds)
{
    actions.string_number = actions_get.string_number;
	actions.finger_position = actions_get.finger_position;
	actions.bow_force = actions_get.bow_force;
	actions.bow_bridge_distance = actions_get.bow_bridge_distance;
	// don't copy bow_velocity!
	// target
	m_target_velocity = actions_get.bow_velocity;
	m_st = actions.string_number;
	m_dyn = round(actions_get.dynamic);
	m_K = K;

    note_samples = 0;

    actions_file->finger(total_samples*dt, actions.string_number,
                         actions.finger_position);
    violin->finger(actions.string_number, actions.finger_position);

    for (int i = 0; i < seconds/DH; i++) {
        hop();
    }
}

inline void ViviController::hop(unsigned int num_samples) {
    // approach target velocity
    const double dv = m_target_velocity - actions.bow_velocity;
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
                      actions.bow_velocity);
    short *buf = wavfile->request_fill(num_samples);
    violin->wait_samples(buf, num_samples);
    total_samples += num_samples;
    note_samples += num_samples;

    ears[m_st][m_dyn]->listenShort(buf);
    int cat = ears[m_st][m_dyn]->getClass();
	actions_file->category(total_samples*dt, cat);
	// adjust bow force
	actions.bow_force *= pow(m_K, 2-cat);

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


