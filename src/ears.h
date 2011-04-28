
#ifndef EARS
#define EARS

//#define LEAN
/*
#ifndef LEAN
#include "marsyas/MarSystemManager.h"
#else
#include "marsyas/MarSystem.h"
#endif
*/

#include "marsyas/MarSystemManager.h"
//using namespace std;

//const unsigned int EARS_HOPSIZE = 128;
const unsigned int EARS_HOPSIZE = 256;
//const unsigned int EARS_HOPSIZE = 512;
// needs to be at least 1024 for yin pitch
const unsigned int EARS_WINDOWSIZE = 1024;

const unsigned int CATEGORY_NULL = -1;


const unsigned int SAMPLE_RATE = 44100;
const double dh = (double) EARS_HOPSIZE / SAMPLE_RATE;


class Ears {
public:
    Ears();
    ~Ears();
    // additional "constructors"
    void set_training(const char *mf_in_filename,
                      const char *arff_out_filename_get);
    void set_predict_wavfile(const char *training_file);
    void set_predict_buffer(const char *training_file);

    void reset();
    void resetTicksCount();

    // usage
    // for set_training
    void processFile();
    // for predict_wavfile:
    void predict_wavfile(const char *wav_in_filename,
                         const char *cats_out_filename);
    bool tick_file();
    // for predict_audio
    void listen(double *audio);
    void listenShort(short *audio);

    // for extra params
    void set_extra_params(int st, double finger);

    // information
    int getClass();
    double getPitch();

    // end
    void saveTraining(const char *out_mpl_filename);

    short *get_hopsize_array();

private:
    typedef enum {
        NONE,
        TRAIN_FILE,
        PREDICT_FILE,
        PREDICT_BUFFER,
    } Mode;


    //void listen(double *audio, double *bow_forces);

    // other
    void get_info_file(std::string filename);

    std::string arff_out_filename;
    std::string in_filename;
    Mode mode;


    // don't use static -- it's not thread-safe!
    //static Marsyas::MarSystemManager mng;
    Marsyas::MarSystemManager mng;

    void make_net();
    Marsyas::MarSystem *net;

    void make_input();
    Marsyas::MarSystem *audio_input;
    //Marsyas::MarSystem *bow_input;


    void make_features();
    Marsyas::MarSystem *audio_features;
    //Marsyas::MarSystem *bow_features;

    Marsyas::MarSystem *timeDomain();
    Marsyas::MarSystem *spectralDomain();
    Marsyas::MarSystem *spectralDomainTrans();

    Marsyas::MarSystem *yin_pitch;
    Marsyas::MarSystem *pitchdiff;
    Marsyas::MarSystem *power_system(std::string basename, double power);

    void make_learning();
    Marsyas::MarSystem *learning;
    Marsyas::MarSystem *classifier;

    Marsyas::MarSystem *marPitch(std::string type, std::string name);

    double string_finger_freq(double st, double finger);

    Marsyas::realvec audio_input_realvec;
//    Marsyas::realvec bow_input_realvec;

    std::string oldfile;
    Marsyas::realvec parameters_input_realvec;
    Marsyas::MarSystem *parameters_input;

    Marsyas::mrs_natural ticks_count;
    Marsyas::mrs_natural stabilizingDelay;

    short *hopsize_array;
};
#endif

