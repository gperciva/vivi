
#ifndef VIVI_CONTROLLER
#define VIVI_CONTROLLER

class MonoWav;
class ActionsFile;
class Ears;
#include "ears.h"
#include "artifastring/violin_instrument.h"
#include "dynamics.h" // for NUM_DYNAMICS
#include "vivi_note_params.h"
#include "controller_params.h"

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
    // TODO: rename for params too
    bool load_ears_training(int st, int dyn,
                            const char *training_file);
    void set_stable_K(int st, int dyn, double K);
    void set_dampen(int st, int dyn, double dampen);

    // per-file prepare
    void filesClose();
    bool filesNew(const char *filenames_base);

    // special
    void comment(const char *text);
    void basic(PhysicalActions actions_get, double seconds,
               double seconds_skip);
    void make_dampen(PhysicalActions actions_get,
                     double damp, int hops_settle, int hops_reduce, int hops_wait,
                     const char *filename=NULL);

    // normal "everytime" stuff
    void rest(double seconds);
    void pizz(PhysicalActions actions_get, double seconds);
    void note(PhysicalActions actions_get, double seconds,
              NoteBeginning begin, NoteEnding end,
              const char *point_and_click=NULL);

private:
    // always used
    ViolinInstrument *violin;
    gsl_rng *random;

    // optional (maybe?  TODO: check)
    MonoWav *wavfile;
    ActionsFile *actions_file;
    ActionsFile *cats_file;
    Ears *ears[NUM_STRINGS][NUM_DYNAMICS];
    double m_K[NUM_STRINGS][NUM_DYNAMICS];
    double m_dampen[NUM_STRINGS][NUM_DYNAMICS];

    int cats[CATS_MEAN_LENGTH]; // TODO: to test mean
    int cats_index;

    void note_setup_actions(PhysicalActions actions_get,
                            NoteBeginning begin);
    void note_write_actions(const char *point_and_click);
    void finger();


    PhysicalActions actions;
    int m_st;
    int m_dyn;
    double m_velocity_target;
    double m_velocity_cutoff_force_adj;
    double m_bow_pos_along;
    bool m_feedback_adjust_force;

    // ASSUME: we play for a maximum of 13 hours per file
    int m_total_samples;
    int m_note_samples;

    inline void hop(int num_samples = EARS_HOPSIZE);
    inline void hop_passive(int num_samples = EARS_HOPSIZE);

    inline double norm_bounded(double mu, double sigma);

    inline double interpolate(const double x,
                              const double x0, const double y0,
                              const double x1, const double y1);

    inline void bowStop();

};
#endif

