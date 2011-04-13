
#ifndef VIVI_CONTROLLER
#define VIVI_CONTROLLER

class ViolinInstrument;
class MonoWav;
class ActionsFile;
class Ears;
#include "ears.h"

extern "C" {
#include <gsl/gsl_randist.h>
}


typedef struct {
    unsigned int string_number;
    double finger_position;
    double bow_bridge_distance;
    double bow_force;
    double bow_velocity;
} PhysicalActions;

const unsigned int NUM_STRINGS = 4;
const unsigned int NUM_DYNAMICS = 4;

class ViviController {

public:
    ViviController();
    ~ViviController();
    void reset();

    Ears *getEars(unsigned int st, unsigned int dyn);

    void filesClose();
    bool filesNew(const char *filenames_base);
    void note(PhysicalActions actions_get, double seconds);
    void basic(PhysicalActions actions_get, double seconds,
               double seconds_skip, const char *filenames_base);

private:
    ViolinInstrument *violin;
    MonoWav *wavfile;
    ActionsFile *actions_file;
    Ears *ears[NUM_STRINGS][NUM_DYNAMICS];

    gsl_rng *random;

    PhysicalActions actions;
    double target_vel;

    // ASSUME: we play for a maximum of 27 hours per file
    unsigned int total_samples;
    unsigned int note_samples;

    inline void hop(unsigned int num_samples = EARS_HOPSIZE);
    inline double norm_bounded(double mu, double sigma);


};
#endif

