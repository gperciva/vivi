
#ifndef VIVI_CONTROLLER
#define VIVI_CONTROLLER

#include "violin_instrument.h"
#include "monowav.h"
#include "ears.h"
#include "actions_file.h"

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
    ViviController(const char *train_dir);
    ~ViviController();
    void reset();

    void filesClose();
    bool filesNew(const char *filenames_base);
    void note(PhysicalActions actions_get, double seconds);
    void basic(PhysicalActions actions_get, double seconds,
               double seconds_skip);

private:
    ViolinInstrument *violin;
    MonoWav *wavfile;
    ActionsFile *actions_file;
    Ears *ears[NUM_STRINGS][NUM_DYNAMICS];

    gsl_rng *random;
    char m_train_dir[256];

    PhysicalActions actions;
    double target_vel;

    // ASSUME: we play for a maximum of 27 hours per file
    unsigned int total_samples;
    unsigned int note_samples;

    inline void hop(unsigned int num_samples = EARS_HOPSIZE);
    inline double norm_bounded(double mu, double sigma);

};
#endif

