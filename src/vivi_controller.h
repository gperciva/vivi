
#ifndef VIVI_CONTROLLER
#define VIVI_CONTROLLER

class MonoWav;
class ActionsFile;
class Ears;
#include "ears.h"
#include "artifastring/violin_instrument.h"
#include "dynamics.h" // for NUM_DYNAMICS
#include "vivi_note_params.h"

extern "C" {
#include <gsl/gsl_randist.h>
}

// TODO: move to artifastring?
const int NUM_STRINGS = 4;

const int CATS_MEAN_LENGTH = 4;

class ViviController {

public:
    ViviController();
    ~ViviController();
    void reset();

    // per-session prepare for action
    Ears *getEars(int st, int dyn);
    bool load_ears_training(int st, int dyn,
                            const char *training_file);
    void set_stable_K(double K);

    // per-file prepare
    void filesClose();
    bool filesNew(const char *filenames_base);

    // sppecial
    void comment(const char *text);
    void basic(PhysicalActions actions_get, double seconds,
               double seconds_skip, const char *filenames_base);

    // normal "everytime" stuff
    void note(PhysicalActions actions_get,
              double seconds);
private:
    // always used
    ViolinInstrument *violin;
    gsl_rng *random;

    // optional (maybe?  TODO: check)
    MonoWav *wavfile;
    ActionsFile *actions_file;
    ActionsFile *cats_file;
    Ears *ears[NUM_STRINGS][NUM_DYNAMICS];

    int cats[CATS_MEAN_LENGTH]; // TODO: to test mean
    int cats_index;


    PhysicalActions actions;
    int m_st;
    int m_dyn;
    double m_velocity_target;
    double m_velocity_cutoff_force_adj;

    double m_K;

    // ASSUME: we play for a maximum of 13 hours per file
    int total_samples;
    int note_samples;

    inline void hop(int num_samples = EARS_HOPSIZE);
    inline double norm_bounded(double mu, double sigma);

    inline double interpolate(const double x,
                              const double x0, const double y0,
                              const double x1, const double y1);

    inline void bowStop();

};
#endif

