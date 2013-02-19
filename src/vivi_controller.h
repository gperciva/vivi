
#ifndef VIVI_CONTROLLER
#define VIVI_CONTROLLER

class MonoWav;
class ActionsFile;
class Ears;
#include "artifastring/artifastring_defines.h"
#include "ears.h"
#include "artifastring/artifastring_instrument.h"
#include "dynamics.h" // for NUM_DYNAMICS
#include "vivi_note_params.h"
#include "controller_params.h"
#include "artifastring/midi_pos.h"

#define RESEARCH

extern "C" {
#include <gsl/gsl_randist.h>
}

// TODO: move to artifastring?
const int NUM_STRINGS = 4;

class ViviController {

public:
    ViviController(int instrument_type=0,
                   int instrument_number=0);
    ~ViviController();
    void reset(bool keep_files=false);
    //void reset();

    // per-session prepare for action
    Ears *getEars(int st);
    // TODO: rename for params too
    bool load_ears_training(int st, const char *training_file);
    void load_dyn_parameters(int st, int dyn, const char *vivi_filename);
    void set_stable_K(int st, int dyn, int fmi, double K);
    void set_dampen(int st, int dyn, double dampen_normal);

    // per-file prepare
    void filesClose();
    bool filesNew(const char *filenames_base);

    // special
    void comment(const char *text);
#if 0
    void basic(NoteBeginning begin, double seconds,
               double seconds_skip);
#endif
#if 0
    void make_dampen(NoteBeginning begin,
                     double damp, int hops_settle, int hops_reduce, int hops_wait,
                     const char *filename=NULL);
#endif

    // normal "everytime" stuff
    void rest(double seconds);
    void pizz(NoteBeginning begin, double seconds);
    void note(NoteBeginning begin, double seconds,
              NoteEnding end,
              const char *point_and_click=NULL, double alter_force=1.0,
              short *audio_buffer=NULL);

    void continuous(short *audio_buffer, PhysicalActions physical,
                    double midi_target_get=0, bool run=false);
    // TODO: make private again?
    void bowStop();

#ifdef RESEARCH
    PhysicalActions actions;
    bool m_feedback_adjust_force;
    void hop(int num_samples = EARS_HOPSIZE, short *audio_buffer=NULL);
#endif

private:
    // always used
    ArtifastringInstrument *violin;
    gsl_rng *random;

    // optional (maybe?  TODO: check)
    MonoWav *wavfile;
    MonoWav *force_file;
    ActionsFile *actions_file;
    ActionsFile *cats_file;
    //Ears *ears[NUM_STRINGS][NUM_DYNAMICS];
    Ears *ears[NUM_STRINGS];
    double m_K[NUM_STRINGS][NUM_DYNAMICS][3];
    double hop_K;
    double m_dampen_normal[NUM_STRINGS][NUM_DYNAMICS];
    //double m_dampen_slur[NUM_STRINGS][NUM_DYNAMICS];

    double cats[CATS_LENGTH]; // TODO: to test mean
    int cats_index;
    int m_cats_wait_hops;

    void note_setup_actions(NoteBeginning begin);
    void note_write_actions(NoteBeginning begin, NoteEnding end,
                            const char *point_and_click);
    void finger();


    int m_inst_num;
    int m_inst_type;
    void pitch_pid();

    void reset_arrays();

#ifndef RESEARCH
    //PhysicalActions actions;
    //bool m_feedback_adjust_force;
    //inline void hop(int num_samples = EARS_HOPSIZE);
#endif

    int m_st;
    int m_dyn;
    double m_velocity_target;
    double m_velocity_cutoff_force_adj;
    double m_bow_pos_along;

    double cats_mean();
    double cats_median();
    double cats_std();
    double pitches_median(double midi_target);

    // ASSUME: we play for a maximum of 13 hours per file
    int m_total_samples;
    int m_note_samples;

    inline void hop_passive(int num_samples = EARS_HOPSIZE);

    inline double norm_bounded(double mu, double sigma);

    inline double interpolate(const double x,
                              const double x0, const double y0,
                              const double x1, const double y1);

    double pitches[PITCH_MEANS];
    int pitch_index;
    double midi_target;
    double pitch_integral;

    int ticks_attack;
    int note_first_alter_hop;
    float note_first_reduction;
    int note_end;
    double max_hand_accel;
};
#endif

