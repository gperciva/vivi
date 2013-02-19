
#ifndef EARS
#define EARS

#include "vivi_defines.h"

//using namespace std;
namespace Marsyas {
class MarSystem;
}
#include "marsyas/marsyas_types.h"
#include "marsyas/realvec.h"

#include "aubio/aubio.h"

const int EARS_HOPSIZE = HOPSIZE;
// needs to be at least 1024 for two cycles of cello C 65 Hz
// at 22050
const int EARS_WINDOWSIZE = 1024;


const double dh = (double) EARS_HOPSIZE / SAMPLE_RATE;

class Ears {
public:
    Ears(int inst_type, int inst_num, bool classification=false);
    ~Ears();
    // additional "constructors"
    bool set_training(const char *mf_in_filename,
                      const char *arff_out_filename_get);
    bool set_predict_wavfile(const char *training_file);
    bool set_predict_buffer(const char *training_file);

    void reset();

    // usage
    // for set_training
    void processFile();
    // for predict_wavfile:
    void predict_wavfile(const char *wav_in_filename,
                         const char *cats_out_filename);
    //bool tick_file();

    void hop();

    // for predict_audio
    void listen(double *audio);
    void listenShort(short *audio);
    void listen_forces(double *audio, double *forces);
    void listenShort_forces(short *audio, short *force);


    // for extra params
    void set_extra_params(int st, double finger_position,
                          double bbd, double force, double velocity,
                          int inst);

    // information
    double getClass();
    double getPitch() {
        return pitch;
    };
    double get_stabilization_delay() {
        return stabilizingDelay;
    };

    // end
    void saveTraining(const char *out_mpl_filename);

    short *get_hopsize_array();

    // TODO: think about proper (?) integration for this; for train_dampen.py
    void get_rms_from_file(int num_frames, const char *filename,
                           double *rmss);

private:
    typedef enum {
        NONE,
        TRAIN_FILE,
        PREDICT_FILE,
        PREDICT_BUFFER,
    } Mode;

    void remove_previous_ears();

    int m_inst_type;
    int m_inst_num;
    int m_base_midi;

    std::string arff_out_filename;
    std::string in_filename;
    Mode mode;
    std::string m_training_filename;

    void make_nets();

    void make_input();
    Marsyas::MarSystem *audio_input;
    Marsyas::MarSystem *force_input;


    Marsyas::MarSystem *audio_stuff;
    Marsyas::MarSystem *force_stuff;
    void make_features();
    Marsyas::MarSystem *audio_features;
    void make_force_features();
    Marsyas::MarSystem *force_features;

    Marsyas::MarSystem *timeDomain();
    Marsyas::MarSystem *spectralDomain(int ah);
    Marsyas::MarSystem *spectralDomainTrans();

    Marsyas::MarSystem *yin_pitch;
    //Marsyas::MarSystem *yin_pitch_force;
    //Marsyas::MarSystem *pitchdiff;
    //Marsyas::MarSystem *pitchdiff_force;
    Marsyas::MarSystem *power_system(Marsyas::MarSystem *mar,
                                     std::string name, double power);

    void make_learning();
    Marsyas::MarSystem *learning;
    Marsyas::MarSystem *classifier;

    double string_finger_freq(double st, double finger_position);

    Marsyas::realvec audio_input_realvec;
    Marsyas::realvec force_input_realvec;

    Marsyas::mrs_natural learning_class;
    Marsyas::realvec learning_input_realvec;
    Marsyas::realvec learning_output_realvec;
    Marsyas::mrs_natural num_audio_observations;
    Marsyas::mrs_natural num_force_observations;

    std::string oldfile;
    Marsyas::realvec parameters_input_realvec;
    Marsyas::MarSystem *parameters_input;
    Marsyas::MarSystem *harmonicsa;
    Marsyas::MarSystem *harmonicsh;
    Marsyas::MarSystem *scna;
    Marsyas::MarSystem *scnh;
    Marsyas::MarSystem *csvFileSource;
    void get_info_csv_file();

    Marsyas::mrs_natural ticks_count;
    Marsyas::mrs_natural stabilizingDelay;

    short *hopsize_array;
    bool m_classification;

    Marsyas::MarSystem * load_classifier(std::string filename);

    aubio_pitchdetection_t *aubio_pitch_object;
    fvec_t *fvec;
    double pitch;

    void advanceFile();
};
#endif

