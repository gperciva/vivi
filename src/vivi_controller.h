
#ifndef VIVI_CONTROLLER
#define VIVI_CONTROLLER

class MonoWav;
class ActionsFile;
class Ears;
#include "ears.h"
#include "violin_instrument.h"
#include "dynamics.h" // for NUM_DYNAMICS

extern "C" {
#include <gsl/gsl_randist.h>
}


typedef struct {
    unsigned int string_number;
	double dynamic; // to allow interpolation
    double finger_position;
	double bow_bridge_distance;
    double bow_force;
	double bow_velocity;
} PhysicalActions;

class ViviController {

public:
    ViviController();
    ~ViviController();
    void reset();

    Ears *getEars(unsigned int st, unsigned int dyn);
	bool load_ears_training(unsigned int st, unsigned int dyn,
		std::string training_file);

    void filesClose();
    bool filesNew(const char *filenames_base);
    void note(PhysicalActions actions_get,
		double K,
		double seconds);
    void basic(PhysicalActions actions_get, double seconds,
               double seconds_skip, const char *filenames_base);

private:
	// always used
    ViolinInstrument *violin;
    gsl_rng *random;

	// optional (maybe?  TODO: check)
    MonoWav *wavfile;
    ActionsFile *actions_file;
    Ears *ears[NUM_STRINGS][NUM_DYNAMICS];


    PhysicalActions actions;
	unsigned int m_st;
	unsigned int m_dyn;
    double m_target_velocity;

	double m_K;

    // ASSUME: we play for a maximum of 27 hours per file
    unsigned int total_samples;
    unsigned int note_samples;

    inline void hop(unsigned int num_samples = EARS_HOPSIZE);
    inline double norm_bounded(double mu, double sigma);

	inline double interpolate(const double x,
		const double x0, const double y0,
		const double x1, const double y1);


};
#endif

