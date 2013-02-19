
#include "ears.h"
#include <string.h>
#include "artifastring/actions_file.h"
#include "artifastring/artifastring_defines.h"

//#define PRINT_DEBUG
#define FIDDLE_CLASS

//#define AVOID_UNCERTAIN

//#define ALL_COMBO
//#define ALL_STRINGS
//
//#define FEATURE_POWERS

#include <pthread.h>
static pthread_mutex_t aubio_mutex;


#ifdef ALL_COMBO
#define PHYSICAL_PARAMETERS "pitch,finger,bow-bridge-distance,force,velocity,st0,st1,st2,st3,violin,viola,cello"
#define PHYSICAL_PARAMETERS_SIZE 12
#else
#ifdef ALL_STRINGS
#define PHYSICAL_PARAMETERS "pitch,finger,bow-bridge-distance,force,velocity,st0,st1,st2,st3"
#define PHYSICAL_PARAMETERS_SIZE 9
#else
//#define PHYSICAL_PARAMETERS "finger,bow-bridge-distance,velocity,force"
//#define PHYSICAL_PARAMETERS_SIZE 4
//#define PHYSICAL_PARAMETERS "finger,bow-bridge-distance,velocity,inst_num"
#define PHYSICAL_PARAMETERS "finger,bow-bridge-distance,velocity"
#define PHYSICAL_PARAMETERS_SIZE 3
#endif
#endif

#include "marsyas/Series.h"
#include "marsyas/SoundFileSource.h"
#include "marsyas/SoundFileSink.h"
#include "marsyas/WekaSink.h"
#include "marsyas/Inject.h"
#include "marsyas/Parallel.h"
#include "marsyas/SVMClassifier.h"
#include "marsyas/RealvecSource.h"
#include "marsyas/ShiftInput.h"
#include "marsyas/Gain.h"
#include "marsyas/Fanout.h"
#include "marsyas/Yin.h"
#include "marsyas/PitchDiff.h"
#include "marsyas/ZeroCrossings.h"
#include "marsyas/Clip.h"
#include "marsyas/Fanout.h"
#include "marsyas/Centroid.h"
#include "marsyas/Rolloff.h"
#include "marsyas/SCF.h"
#include "marsyas/RemoveObservations.h"
#include "marsyas/SFM.h"
#include "marsyas/Sum.h"
#include "marsyas/SpectralFlatnessAllBands.h"
#include "marsyas/PowerToAverageRatio.h"
#include "marsyas/MathPower.h"
#include "marsyas/Windowing.h"
#include "marsyas/PowerSpectrum.h"
#include "marsyas/Transposer.h"
#include "marsyas/Rms.h"
#include "marsyas/Annotator.h"
#include "marsyas/HarmonicStrength.h"
#include "marsyas/CsvFileSource.h"
#include "marsyas/Spectrum.h"
#include "marsyas/AbsMax.h"
#include "marsyas/Mean.h"
#include "marsyas/Flux.h"
#include "marsyas/SpectralCentroidBandNorm.h"


using namespace Marsyas;
#include <iostream>
using namespace std;

#include <limits.h>

#include "artifastring/midi_pos.h"
//#include <boost/algorithm/string/split.hpp>
//#include <boost/algorithm/string.hpp>
//#include <boost/lexical_cast.hpp>


Ears::Ears(int inst_type, int inst_num, bool classification) {
    m_classification = classification;

    m_inst_type = inst_type;
    m_inst_num = inst_num;
    if (m_inst_type == 0) {
        m_base_midi = 55;
    }
    if (m_inst_type == 1) {
        m_base_midi = 48;
    }
    if (m_inst_type == 2) {
        m_base_midi = 36;
    }

    audio_input_realvec.create(EARS_HOPSIZE);
    force_input_realvec.create(EARS_HOPSIZE/2);
    parameters_input_realvec.create(PHYSICAL_PARAMETERS_SIZE,1);

    // needed to avoid a segfault
    audio_stuff = NULL;
    force_stuff = NULL;
    learning = NULL;
    classifier = NULL;
    harmonicsa = NULL;
    harmonicsh = NULL;
    scna = NULL;
    scnh = NULL;
    audio_input = NULL;
    force_input = NULL;
    parameters_input = NULL;
    csvFileSource = NULL;
    reset();
    mode = NONE;

    // ick!
    hopsize_array = new short[EARS_HOPSIZE];

    // critical section --------------
    pthread_mutex_lock(&aubio_mutex);
    aubio_pitch_object = new_aubio_pitchdetection(
                             EARS_WINDOWSIZE, EARS_HOPSIZE, 1, SAMPLE_RATE,
                             aubio_pitch_yinfft,
                             aubio_pitchm_midi
                         );
    fvec = new_fvec(EARS_HOPSIZE, 1);
    pthread_mutex_unlock(&aubio_mutex);
    // ------------- critical section end
}

Ears::~Ears() {
    remove_previous_ears();
    // automatically deals with children
    delete [] hopsize_array;
    // critical section --------------
    pthread_mutex_lock(&aubio_mutex);
    del_aubio_pitchdetection(aubio_pitch_object);
    del_fvec(fvec);
    aubio_cleanup();
    pthread_mutex_unlock(&aubio_mutex);
    // ------------- critical section end
}

void Ears::remove_previous_ears() {
    if (audio_stuff != NULL) delete audio_stuff;
    audio_stuff = NULL;
    if (force_stuff != NULL) delete force_stuff;
    force_stuff = NULL;
    if (learning != NULL) delete learning;
    learning = NULL;
    //if (classifier != NULL) delete classifier;
    classifier = NULL;
    if (csvFileSource != NULL) delete csvFileSource;
    csvFileSource = NULL;
    harmonicsa = NULL;
    harmonicsh = NULL;
    scna = NULL;
    scnh = NULL;
    audio_input = NULL;
    force_input = NULL;
    if (parameters_input != NULL) delete parameters_input;
    parameters_input = NULL;
}

void Ears::reset()
{
    arff_out_filename = "";
    in_filename = "";
    ticks_count = 0;
}


bool Ears::set_training(const char *mf_in_filename,
                        const char *arff_out_filename_get)
{
    reset();
    arff_out_filename.assign(arff_out_filename_get);
    in_filename.assign(mf_in_filename);
    if (mode != TRAIN_FILE) {
        remove_previous_ears();
        mode = TRAIN_FILE;
        make_features();
        make_force_features();
        make_learning();
        make_input();
        make_nets();
    }
    learning->updControl("SVMClassifier/svm_cl/mrs_natural/nClasses",
                         audio_stuff->getControl("Series/audio_input/SoundFileSource/audio_src/mrs_natural/nLabels")->to<mrs_natural>());

    learning->updControl("WekaSink/wekasink/mrs_natural/nLabels",
                         audio_stuff->getControl("Series/audio_input/SoundFileSource/audio_src/mrs_natural/nLabels")->to<mrs_natural>());
    learning->updControl("WekaSink/wekasink/mrs_string/labelNames",
                         audio_stuff->getControl("Series/audio_input/SoundFileSource/audio_src/mrs_string/labelNames")->to<mrs_string>());
    // MUST be done after linking this with the main network!
    // but after getting the names
    learning->updControl("WekaSink/wekasink/mrs_string/filename",
                         arff_out_filename);
    learning_output_realvec.create(
        learning->getctrl("mrs_natural/onObservations")->to<mrs_natural>(),
        learning->getctrl("mrs_natural/onSamples")->to<mrs_natural>()
    );

    return true;
}

bool Ears::set_predict_wavfile(const char *training_filename)
{
    reset();
    bool make_new = false;
    if (mode != PREDICT_FILE) {
        make_new = true;
    }
    if (m_training_filename.compare(training_filename) != 0) {
        make_new = true;
    }
    if (make_new) {
        remove_previous_ears();
        mode = PREDICT_FILE;

        classifier = load_classifier(training_filename);
        if (classifier != NULL) {
            make_features();
            make_force_features();
            make_learning();
            make_input();
            make_nets();
            return true;
        } else {
            printf("ERROR: controller set_predict_wavfile cannot load file\n");
            return false;
        }
    }
    return true;
//classifier->updControl("WekaSink/wekasink/mrs_string/filename", m_filename);
}

bool Ears::set_predict_buffer(const char *training_filename)
{
    reset();
    bool make_new = false;
    if (mode != PREDICT_BUFFER) {
        make_new = true;
    }
    if (m_training_filename.compare(training_filename) != 0) {
        make_new = true;
    }
    if (make_new) {
        remove_previous_ears();
        mode = PREDICT_BUFFER;
        classifier = load_classifier(training_filename);
        if (classifier != NULL) {
            make_features();
            make_force_features();
            make_learning();
            make_input();
            make_nets();
            return true;
        } else {
            printf("ERROR: controller set_predict_buffer cannot load file\n");
            return false;
        }
    }
    return true;
}

void Ears::predict_wavfile(const char *wav_in_filename,
                           const char *cats_out_filename)
{
    //in_filename.assign(wav_in_filename);
    audio_input->updControl("SoundFileSource/audio_src/mrs_string/filename",
                            wav_in_filename);
    std::string force_filename;
    force_filename.assign(wav_in_filename);
    force_filename.replace(strlen(wav_in_filename)-4, 4, ".forces.wav");
    force_input->updControl("SoundFileSource/force_src/mrs_string/filename",
                            force_filename);
    //force_input->updControl("SoundFileSource/force_src/mrs_string/onObsNames",
    //                        "force_input");
    // must be done after setting the filename!
    stabilizingDelay = audio_stuff->getctrl("mrs_natural/onStabilizingDelay")->to<mrs_natural>();

    //get_info_file(wav_in_filename);
    string csv_filename = wav_in_filename;
    csv_filename.replace(csv_filename.length()-4, 4, ".csv");
#ifdef PRINT_DEBUG
    cout<<"reading from: "<<csv_filename<<endl;
#endif
    csvFileSource->updControl("mrs_string/filename", csv_filename);

    ActionsFile *cats_out = new ActionsFile(cats_out_filename);
    cats_out->comment(wav_in_filename);

    ticks_count = 0;
    // assume that force_input has the same length as audio_input
    while (audio_stuff->getctrl("mrs_bool/hasData")->isTrue())
    {
        get_info_csv_file();
        hop();
        cats_out->category(ticks_count*dh, getClass());
    }
    delete cats_out;
}

void Ears::saveTraining(const char *out_mpl_filename)
{
    ofstream clout;
    clout.open(out_mpl_filename);
    learning->updControl("SVMClassifier/svm_cl/mrs_string/mode", "predict");
    learning->update();
    //clout << *net << endl;
    clout << *classifier << endl;
    clout.close();
}



void Ears::set_extra_params(int st, double finger_position,
                            double bbd, double force, double velocity,
                            int inst) {
    m_inst_type = inst;
    mrs_real expected_pitch = string_finger_freq(st, finger_position);
    //cout<<"expected pitch: "<<expected_pitch<<endl;
#ifdef PRINT_DEBUG
    cout<<st<<' '<<finger_position<<'\t'<<expected_pitch;
    cout<<'\t'<<bbd<<'\t'<<force<<'\t'<<velocity;
    cout<<endl;
#endif

    //parameters_input_realvec(0,0) = expected_pitch;
    parameters_input_realvec(0,0) = finger_position;
    parameters_input_realvec(1,0) = bbd;
    parameters_input_realvec(2,0) = fabs(velocity);
    //parameters_input_realvec(3,0) = inst_num;
    //parameters_input_realvec(3,0) = force;
    (void) force;
#ifdef ALL_STRINGS
    // clear out strings
    for (int i=5; i<9; i++) {
        parameters_input_realvec(i,0) = 0;
    }
    // set string
    parameters_input_realvec(5+st) = 1;
#endif

#ifdef ALL_COMBO
    // clear instrument
    for (int i=9; i<12; i++) {
        parameters_input_realvec(i,0) = 0;
    }
    // set instrument
    parameters_input_realvec(9+m_inst_type) = 1;
#endif

    /*
        if (parameters_input != NULL) {
            parameters_input->updControl("mrs_realvec/inject", parameters_input_realvec);
        } else {
            cout<<"we need inject"<<endl;
        }
    */
    /*
    if (pitchdiff != NULL) {
        //pitchdiff->updControl("mrs_real/expectedPitch", expected_pitch);
        //pitchdiff_force->updControl("mrs_real/expectedPitch", expected_pitch);
    } else {
        //cout<<"we need pitchdiff"<<endl;
    }
    */
    harmonicsa->updControl("mrs_real/base_frequency", expected_pitch);
    harmonicsh->updControl("mrs_real/base_frequency", expected_pitch);
    scna->updControl("mrs_real/expected_peak", expected_pitch);
    scnh->updControl("mrs_real/expected_peak", expected_pitch);
}

void Ears::get_info_csv_file() {
//cout<<"get_info_csv_file"<<endl;
    if (! csvFileSource->getctrl("mrs_bool/hasData")->isTrue()) {
        // don't change the parameters
        //return;
        // FIXME: do something more sophisticated
        cout<<"Panic!  no data to read: ";
        cout<<csvFileSource->getctrl("mrs_string/filename")->to<mrs_string>();
        cout<<endl;
    } else {
        //cout<<"ok"<<endl;
    }
    // definitely want to tick before getting data!
    csvFileSource->tick();
    mrs_realvec v = csvFileSource->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
    double st = v(0);
    double finger_position = v(1);
    double bbd = v(2);
    double force = v(3);
    double velocity = v(4);
    //cout<<st<<" "<<finger_position<<" "<<bbd<<" "<<velocity<<endl;
    set_extra_params(st, finger_position, bbd, force, velocity,
                     m_inst_type);
}

// ick, this doens't really belong here!
short* Ears::get_hopsize_array() {
    return hopsize_array;
}




void Ears::listen(double *audio) {
    for (int i=0; i<EARS_HOPSIZE; i++) {
        audio_input_realvec(0,i) = audio[i];
        //listen_buffer->data[0][i] = audio[i];
    }
    audio_input->updControl("RealvecSource/audio_src/mrs_realvec/data", audio_input);
    hop();
    ticks_count++;
}

void Ears::listen_forces(double *audio, double *forces) {
    for (int i=0; i<EARS_HOPSIZE; i++) {
        audio_input_realvec(0,i) = audio[i];
    }
    for (int i=0; i<EARS_HOPSIZE/2; i++) {
        force_input_realvec(0,i) = forces[i];
    }
    audio_input->updControl("RealvecSource/audio_src/mrs_realvec/data",
                            audio_input_realvec);
    force_input->updControl("RealvecSource/force_src/mrs_realvec/data",
                            force_input_realvec);
    hop();
    ticks_count++;
}

void Ears::listenShort(short *audio) {
    for (int i=0; i<EARS_HOPSIZE; i++) {
        audio_input_realvec(0,i) = ((mrs_real) audio[i]) / SHRT_MAX;
    }
    audio_input->updControl("RealvecSource/audio_src/mrs_realvec/data",
                            audio_input_realvec);
    hop();
    ticks_count++;
}

void Ears::listenShort_forces(short *audio, short *force) {
    for (int i=0; i<EARS_HOPSIZE; i++) {
        audio_input_realvec(0,i) = ((mrs_real) audio[i]) / SHRT_MAX;
        fvec->data[0][i] = ((smpl_t) audio[i]) / SHRT_MAX;
    }
    for (int i=0; i<EARS_HOPSIZE/2; i++) {
        force_input_realvec(0,i) = ((mrs_real) force[i]) / SHRT_MAX;
    }
    pitch = aubio_pitchdetection(aubio_pitch_object, fvec);
    if ((pitch != pitch) || (isinf(pitch))) {
        //cout<<"bingo"<<endl;
        pitch = PITCH_NULL;
    }
    if (ticks_count < stabilizingDelay) {
        pitch = 0.0;
    }
    audio_input->updControl("RealvecSource/audio_src/mrs_realvec/data",
                            audio_input_realvec);
    force_input->updControl("RealvecSource/force_src/mrs_realvec/data",
                            force_input_realvec);
    hop();
    ticks_count++;
}


double Ears::getClass() {
    if (ticks_count > stabilizingDelay) {
        //realvec data = learning->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
        realvec data = learning_output_realvec;
        double svm_classified = data(0,0);
        double value = svm_classified;
        //printf("SVM_CLASSIFIED: %g\n", svm_classified);

        /*
        // note the lack of -1 here!
        if (svm_classified == CATEGORIES_NUMBER) {
            printf("Panic! how does this happen?  CATEGORIES_NUMBER\n");
            return CATEGORY_WEIRD;
        }
        */

#ifdef FIDDLE_CLASS
        //realvec classPerms = net->getctrl("Series/learning/SVMClassifier/svm_cl/mrs_realvec/classPerms")->to<mrs_realvec>();
        //cout<<"---------"<<endl;
        /*
        mrs_string labels = net->getctrl(
                "Series/learning/WekaSink/wekasink/mrs_string/labelNames"
                )->to<mrs_string>();
        cout<<"---------"<<endl;
        cout<<labels<<endl;
        */
        //cout<<"\t\t";
        /*
        for (int i=0; i < classPerms.getCols(); i++) {
            cout<<classPerms(0,i)<<"\t";
        }
        cout<<endl;
        */

        int HALF = CATEGORIES_NUMBER/2;
        double weighted_mean = 0;
        // ASSUME: labels appear in order
        /*
        for (int i=2; i < data.getRows(); i++) {
            printf("%.3f\t", data(i,0));
        }
        cout<<endl;
        */
        
        double lower_mean = 0;
        for (int i=2; i < 2+HALF; i++) {
            lower_mean += data(i,0);
            weighted_mean += data(i,0)*(i-2);
        }
        weighted_mean += data(2+HALF,0)*HALF;
        //double middle_mean = data(2+HALF,0);

        double upper_mean = 0;
        for (int i=2+HALF+1; i < 2+CATEGORIES_NUMBER; i++) {
            //upper_mean += data(i,0) * i;
            upper_mean += data(i,0);
            weighted_mean += data(i,0)*(i-2);
        }

        /*
                printf("\t");
                printf("%.3f\t%.3f\t%.3f", lower_mean,
                   data(2+CATEGORIES_NUMBER/2,0), upper_mean);
                cout<<"\tsvm:\t"<<svm_classified<<"\t";
                cout<<"weighted:\t"<<weighted_mean;
                printf("\n");
        */
        value = weighted_mean;

#ifdef AVOID_UNCERTAIN
        const double MIN_PROBABILITY_FORCE_CHANGE = 0.75;
        if (value > HALF+0.5) {
            if (upper_mean < MIN_PROBABILITY_FORCE_CHANGE) {
                //value = CATEGORY_WEIRD;
                //cout<<endl;
                //return CATEGORY_WEIRD;
                cout<<"bail 1"<<endl;
                return 0;
            }
        }
        else {
            if (value < HALF-0.5) {
                if (lower_mean < MIN_PROBABILITY_FORCE_CHANGE) {
                    //value = CATEGORY_WEIRD;
                    //cout<<endl;
                //    return CATEGORY_WEIRD;
                cout<<"bail -1"<<endl;
                    return 0;
                }
            } else {
                //if (middle_mean < MIN_PROBABILITY_FORCE_CHANGE) {
                //    return CATEGORY_WEIRD;
                //cout<<"bail 0"<<endl;
                //    return 0;
               // }

            }
        }
        /*
        cout<<"\tnew:\t"<<value;
        //printf("\n");
        printf("\n");
        */
        //cout<<value<<"\t"<<weighted_mean;
        //cout<<endl;

#endif
#endif
        //printf("svm_classified: %g\tvalue: %g\n",
        //printf("%g\t%g\n", data(0,0)+1, value+1);
        
        //printf("%g %g\n",
        //    data(0,0)+1, value+1);

        if (value != value) { // is a NaN
            return CATEGORY_NULL;
        }
        if (value < 0) {
            return CATEGORY_NULL;
        }
        //value = svm_classified; // disable fancy probabilities
        if (!m_classification) {
            value -= CATEGORY_POSITIVE_OFFSET;
        } else {
            value -= (CATEGORIES_CENTER_OFFSET-1);
        }
        return value;
    } else {
        return CATEGORY_NULL;
    }
}

double Ears::string_finger_freq(double st, double finger_position) {
    // FIXME: simplify this in maxima?
    double finger_midi = 12.0 * log(1.0/(1.0-finger_position))/log(2.0);
    double midi = m_base_midi + 7*st + finger_midi;
    return 440.0 * pow(2, (midi-69)/12.0);
}


#if 0
bool Ears::tick_file() {
    if (audio_input->getctrl("SoundFileSource/audio_src/mrs_bool/hasData")->isTrue())
    {
        string currentlyPlaying =
            audio_input->getControl("SoundFileSource/audio_src/mrs_string/currentlyPlaying")->to<mrs_string>();

        if (currentlyPlaying != oldfile) {
            //get_info_file(currentlyPlaying);
            string csv_filename = currentlyPlaying;
            csv_filename.replace(csv_filename.length()-4, 4, ".csv");
            csvFileSource->updControl("mrs_string/filename", csv_filename);
            oldfile = currentlyPlaying;
        }

        get_info_csv_file();
        hop();
        ticks_count++;
        return true;
    } else {
        return false;
    }
}
#endif

void Ears::advanceFile() {
    string currentlyPlaying = audio_input->getControl("SoundFileSource/audio_src/mrs_string/currentlyPlaying")->to<mrs_string>();
    //get_info_file(currentlyPlaying);
    string csv_filename = currentlyPlaying;
    csv_filename.replace(csv_filename.length()-4, 4, ".csv");
#ifdef PRINT_DEBUG
    cout<<"---- ProcessFile new csv: "<<csv_filename<<endl;
#endif
    csvFileSource->updControl("mrs_string/filename", csv_filename);
    oldfile = currentlyPlaying;

    size_t found;
    // ASSUME: only one of each
    found = currentlyPlaying.find("violin");
    if (found != string::npos) {
        m_inst_type = 0;
    }
    found = currentlyPlaying.find("viola");
    if (found != string::npos) {
        m_inst_type = 1;
    }
    found = currentlyPlaying.find("cello");
    if (found != string::npos) {
        m_inst_type = 2;
    }


    std::string force_filename = csv_filename;
    force_filename.replace(csv_filename.length()-4, 4, ".forces.wav");
    force_input->updControl(
        "SoundFileSource/force_src/mrs_string/filename",
        force_filename);
    //cout<<force_filename<<endl;

    //cout<<"--------"<<currentlyPlaying<<endl;

}

void Ears::processFile() {
    //cout<<"processFile"<<endl;
    advanceFile();
    ticks_count = 0;
    while (audio_stuff->getctrl("mrs_bool/hasData")->isTrue())
    {
    /*
        bool last = audio_input->getControl(
            "SoundFileSource/audio_src/mrs_bool/currentLastTickWithData"
            //"SoundFileSource/audio_src/mrs_bool/startStable"
            )->isTrue();
        //cout<<is<<endl;
        if (last) {
            break;
        }
        */
        get_info_csv_file();
        hop();
        realvec a = audio_stuff->getctrl("mrs_realvec/processedData")->to<realvec>();
        if (a(0) == 0.0) {
            string currentlyPlaying = audio_input->getControl("SoundFileSource/audio_src/mrs_string/currentlyPlaying")->to<mrs_string>();
            cout<<"Warning: 0 amplitude in: "<<currentlyPlaying<<endl;
        }
    }
}


void Ears::make_input() {
    audio_input = new Series ("audio_input");
    force_input = new Series ("force_input");

    if (mode == PREDICT_BUFFER) {
        audio_input->addMarSystem(new RealvecSource ("audio_src"));
        force_input->addMarSystem(new RealvecSource ("force_src"));
        force_input->updControl("RealvecSource/force_src/mrs_string/onObsNames",
                                "force_obs_,");
    }
    if (mode == TRAIN_FILE) {
        audio_input->addMarSystem(new SoundFileSource ("audio_src"));
        audio_input->updControl("SoundFileSource/audio_src/mrs_string/filename", in_filename);
        if (!m_classification) {
            audio_input->updControl("SoundFileSource/audio_src/mrs_bool/regression",true);
        }
        force_input->addMarSystem(new SoundFileSource ("force_src"));
        force_input->updControl("SoundFileSource/force_src/mrs_string/onObsNames",
                                "force_obs_,");
        // don't try to set force filename here
        if (!m_classification) {
            force_input->updControl("SoundFileSource/force_src/mrs_bool/regression",true);
        }
    }
    if (mode == PREDICT_FILE) {
        audio_input->addMarSystem(new SoundFileSource ("audio_src"));
        force_input->addMarSystem(new SoundFileSource ("force_src"));
        force_input->updControl("SoundFileSource/force_src/mrs_string/onObsNames",
                                "force_obs_,");
    }
    audio_input->addMarSystem(new ShiftInput ("shift_input"));
    audio_input->updControl("ShiftInput/shift_input/mrs_natural/winSize",
                            EARS_WINDOWSIZE);
    force_input->addMarSystem(new ShiftInput ("shift_input"));
    force_input->updControl("ShiftInput/shift_input/mrs_natural/winSize",
                            EARS_WINDOWSIZE/2);
}

Marsyas::MarSystem *Ears::timeDomain()
{
    MarSystem *net = new Fanout ("td");

    net->addMarSystem(
        power_system(new Rms("rms"), "rms",
                                   1.0/4.0));
    net->addMarSystem(new PowerToAverageRatio ("par"));
    //net->addMarSystem(new MeanAbsoluteDeviation ("mad"));
    //net->addMarSystem(new AbsMax("absmax"));

    net->addMarSystem(new ZeroCrossings ("orig_zero"));

    /*
        MarSystem *yinseries = new Series ("yin_series");
        net->addMarSystem(yinseries);
        yin_pitch = new Yin ("yin");
        yinseries->addMarSystem(yin_pitch);
        pitchdiff = new PitchDiff ("pitchdiff");
        yinseries->addMarSystem(pitchdiff);
        MarSystem *yinfan =  new Fanout ("yin_fan");
        yinseries->addMarSystem(yinfan);
    */
    //pitchdiff->updControl("mrs_bool/ignoreOctaves", true);
    //pitchdiff->updControl("mrs_bool/absoluteValue", true);
    /*
    yinfan->addMarSystem(new Clip ("clip1"));
    yinfan->updControl("Clip/clip1/mrs_real/range", 0.3);
    yinfan->addMarSystem(new Clip ("clip2"));
    yinfan->updControl("Clip/clip2/mrs_real/range", 3.0);
    */

    /*
    yinfan->addMarSystem(new Clip ("clip3"));
    yinfan->updControl("Clip/clip3/mrs_real/range", 12.0);
    */
    return net;
}

Marsyas::MarSystem *Ears::spectralDomain(int ah)
{
    MarSystem *net = new Fanout ("sd");

//    net->addMarSystem(new Centroid ("cntrd"));
//    net->addMarSystem(new Rolloff ("rlf"));
    net->addMarSystem(power_system(
                          new Centroid("centroid"), "centroid", 1.0/4.0));
    //net->addMarSystem(power_system(
    //                      new Rolloff("rolloff"), "rolloff", 1.0/8.0));

/*
    net->addMarSystem(power_system(
                          new Flux("flux"), "flux", 1.0/16.0));
#ifdef FEATURE_POWERS
    net->updControl("Series/flux/Flux/flux/mrs_string/mode",
        "Laroche2003");
#else
    net->updControl("Flux/flux/mrs_string/mode",
        "Laroche2003");
#endif
*/

    if (ah == 0) {
        scna = new SpectralCentroidBandNorm("SCN");
        net->addMarSystem( power_system(scna, "SCN", 1.0/8.0));
    } else {
        scnh = new SpectralCentroidBandNorm("SCN");
        net->addMarSystem( power_system(scnh, "SCN", 1.0/8.0));
    }

    
    if (ah == 0) {
    mrs_natural num_harmonics = 3;
    realvec harmonics_r(num_harmonics);
    harmonics_r(0) = 0.5;
    harmonics_r(1) = 1.0;
    harmonics_r(2) = 2.0;
    //harmonics_r(3) = 3.0;
    //harmonics_r(5) = 5.0;
        harmonicsa = new HarmonicStrength ("harm");
        net->addMarSystem(harmonicsa);
    harmonicsa->updControl("mrs_realvec/harmonics", harmonics_r);
    harmonicsa->updControl("mrs_natural/harmonicsSize", num_harmonics);
    harmonicsa->updControl("mrs_real/harmonicsWidth", 0.01);
    harmonicsa->updControl("mrs_real/inharmonicity_B", 1e-4);
    harmonicsa->updControl("mrs_natural/type", 2);
    } else {
    mrs_natural num_harmonics = 3;
    realvec harmonics_r(num_harmonics);
    harmonics_r(0) = 0.5;
    harmonics_r(1) = 1.0;
    harmonics_r(2) = 2.0;
    //harmonics_r(3) = 3.0;
        harmonicsh = new HarmonicStrength ("harm");
        net->addMarSystem(harmonicsh);
    harmonicsh->updControl("mrs_realvec/harmonics", harmonics_r);
    harmonicsh->updControl("mrs_natural/harmonicsSize", num_harmonics);
    harmonicsh->updControl("mrs_real/harmonicsWidth", 0.01);
    harmonicsh->updControl("mrs_real/inharmonicity_B", 1e-4);
    harmonicsh->updControl("mrs_natural/type", 2);
    }

#if 0
    //mrs_real max_S_obs = 20.0 / 24.0;
    mrs_real max_S_obs = 16.0 / 24.0;
    MarSystem *scf_trim = new Series ("scf_trim");
    //net->addMarSystem(scf_trim);
    scf_trim->addMarSystem(new SCF ("scf"));
    scf_trim->addMarSystem(new RemoveObservations ("rem_scf"));
    scf_trim->updControl("RemoveObservations/rem_scf/mrs_real/highCutoff",
                         max_S_obs);
    MarSystem *sfm_trim = new Series ("sfm_trim");
    //net->addMarSystem(sfm_trim);
    sfm_trim->addMarSystem(new SFM ("sfm"));
    sfm_trim->addMarSystem(new RemoveObservations ("rem_sfm"));
    sfm_trim->updControl("RemoveObservations/rem_sfm/mrs_real/highCutoff",
                         max_S_obs);
#endif

//    net->addMarSystem(new Sum ("sumspt"));
//    net->updControl("Sum/sumspt/mrs_string/mode", "sum_whole");
//    net->addMarSystem(power_system("Sum",1.0/8.0));

#if 0
    MarSystem *flatness = new Series ("flatness");
    net->addMarSystem(flatness);
    flatness->addMarSystem(new RemoveObservations ("filt_obs"));
//    flatness->updControl("RemoveObservations/filt_obs/mrs_real/lowCutoff",
//                         0.0/22050.0*2.0);
    flatness->updControl("RemoveObservations/filt_obs/mrs_real/highCutoff",
                         0.25);
                         ///(ARTIFASTRING_INSTRUMENT_SAMPLE_RATE/2));
#endif
    net->addMarSystem(power_system(
                               new SpectralFlatnessAllBands("SpectralFlatnessAllBands"),
                               "sfab",1.0/8.0));

    return net;
}

Marsyas::MarSystem *Ears::spectralDomainTrans()
{
    MarSystem *net = new Fanout ("sdt");

    net->addMarSystem(power_system(new Rms("rms"), "rms",
                                   1.0/8.0));
#if 0
    net->addMarSystem(power_system(new Mean("mean"), "mean",
                                   1.0/4.0));
    net->addMarSystem(power_system(new AbsMax("absmas"), "absmax",
                                   1.0/4.0));
#endif
    //net->addMarSystem(power_system(new PowerToAverageRatio("spectral_par"), "spectral_par",
    //                               1.0/8.0));
    net->addMarSystem(new PowerToAverageRatio ("specral_par"));
    return net;
}

MarSystem *Ears::power_system(MarSystem *mar, std::string name, double power) {
#ifdef FEATURE_POWERS
    MarSystem *net = new Series (name);
    net->addMarSystem(mar);
    net->addMarSystem(new MathPower ("mathpower"));
    net->updControl("MathPower/mathpower/mrs_real/exponent", power);
    return net;
#else
    (void) name;
    (void) power;
    return mar;
#endif
}


void Ears::make_force_features() {
    force_features = new Fanout ("force_features");

    force_features->addMarSystem(
        power_system(new Rms("rms"), "rms",
                                   1.0/4.0));
    force_features->addMarSystem(new PowerToAverageRatio ("par"));
    //force_features->addMarSystem(new AbsMax("absmax"));
// yin
    /*
        MarSystem *yinseries = new Series ("yin_series");
        force_features->addMarSystem(yinseries);
        yin_pitch_force = new Yin ("yin");
        yinseries->addMarSystem(yin_pitch_force);
        pitchdiff_force = new PitchDiff ("pitchdiff");
        yinseries->addMarSystem(pitchdiff_force);
        yinseries->addMarSystem(new Clip ("clip3"));
        yinseries->updControl("Clip/clip3/mrs_real/range", 12.0);
    */

//spectral
    MarSystem *spectral = new Series ("spectral");
    force_features->addMarSystem(spectral);
    spectral->addMarSystem(new Windowing ("hamming"));
    spectral->addMarSystem(new Spectrum ("spk"));
    spectral->updControl("Spectrum/spk/mrs_real/cutoff", 0.5);
    spectral->addMarSystem(new RemoveObservations ("ro"));
    spectral->updControl("RemoveObservations/ro/mrs_real/highCutoff",
                         0.5);
    spectral->addMarSystem(new PowerSpectrum ("pspk"));
    spectral->updControl("PowerSpectrum/pspk/mrs_string/spectrumType","power");
    spectral->linkControl("Spectrum/spk/mrs_real/cutoff", "mrs_real/cutoff");

// I /think/ that these are all "pure"
    MarSystem *spect_fan = new Fanout ("spectral_fanout");
    spectral->addMarSystem(spect_fan);

//    spect_fan->addMarSystem( noise );
    spect_fan->addMarSystem( spectralDomain(1) );

    MarSystem *trans = new Series ("spect_trans");
    spect_fan->addMarSystem(trans);
    trans->addMarSystem(new Transposer ("trans"));
    trans->addMarSystem( spectralDomainTrans() );
}

void Ears::make_features() {
    audio_features = new Fanout ("audio_features");
    audio_features->addMarSystem( timeDomain() );
    //mar->linkControl("Fanout/main_fanout/Fanout/td/mrs_real/pitch_mult",
    //"mrs_real/pitch_mult");

    MarSystem *spectral = new Series ("spectral");
    audio_features->addMarSystem(spectral);
    spectral->addMarSystem(new Windowing ("hamming"));
    spectral->addMarSystem(new Spectrum ("spk"));
    spectral->updControl("Spectrum/spk/mrs_real/cutoff", 0.5);
    spectral->addMarSystem(new RemoveObservations ("ro"));
    spectral->updControl("RemoveObservations/ro/mrs_real/highCutoff",
                         0.5);
    spectral->addMarSystem(new PowerSpectrum ("pspk"));
    spectral->updControl("PowerSpectrum/pspk/mrs_string/spectrumType","power");
    spectral->linkControl("Spectrum/spk/mrs_real/cutoff", "mrs_real/cutoff");
//            spectral->addMarSystem(new RemoveObservations ("filt_obs"));
//            spectral->updControl("RemoveObservations/filt_obs/mrs_real/lowCutoff",
//                                 0.0/22050.0*2.0);
//            spectral->updControl("RemoveObservations/filt_obs/mrs_real/highCutoff",
//                                 10000.0/22050.0*2.0);

    /*
        MarSystem *noise = new Series ("noise");
        noise->addMarSystem(new RemoveObservations ("filt_obs"));
        noise->updControl("RemoveObservations/filt_obs/mrs_real/lowCutoff",
                             0.0/22050.0*2.0);
        noise->updControl("RemoveObservations/filt_obs/mrs_real/highCutoff",
                             180.0/22050.0*2.0);
        noise->addMarSystem(new Transposer ("trans"));
        noise->addMarSystem(new Rms ("rms_spect"));
        noise->addMarSystem(new MathPower ("mathpower"));
        noise->updControl("MathPower/mathpower/mrs_real/exponent", 1.0/8.0);
    */

    MarSystem *spect_fan = new Fanout ("spectral_fanout");
    spectral->addMarSystem(spect_fan);

//    spect_fan->addMarSystem( noise );
    spect_fan->addMarSystem( spectralDomain(0) );

    MarSystem *trans = new Series ("spect_trans");
    spect_fan->addMarSystem(trans);
    trans->addMarSystem(new Transposer ("trans"));
    trans->addMarSystem( spectralDomainTrans() );
}

void Ears::make_learning() {
    learning = new Series ("learning");

    learning->addMarSystem(new Annotator ("annotator"));
    if (mode == TRAIN_FILE) {
        learning->addMarSystem(new WekaSink ("wekasink"));

        learning->updControl("WekaSink/wekasink/mrs_bool/onlyStable",true);

        learning->updControl("WekaSink/wekasink/mrs_natural/precision",10);
        //bool all = true;
// try combination

        // use regression or classification?
        if (!m_classification) {
            learning->updControl("WekaSink/wekasink/mrs_bool/regression",true);
            //learning->updControl("WekaSink/wekasink/mrs_natural/nLabels",7);
        }
        // MUST be done after linking with main network, i.e. not here!
        //learning->updControl("WekaSink/wekasink/mrs_string/filename", m_filename);

        //learning->addMarSystem(new Classifier ("cl"));
//    learning->updControl("Classifier/cl/mrs_string/mode", "train");
//    learning->updControl("Classifier/cl/mrs_string/enableChild", "SVMClassifier/svmcl");
//    learning->updControl("Classifier/cl/mrs_natural/nClasses", 6);
    }

    if (classifier == NULL) {
        classifier = new SVMClassifier ("svm_cl");
        classifier->updControl("mrs_string/mode", "train");
        if (!m_classification) {
            classifier->updControl("mrs_string/svm", "NU_SVR");
            classifier->updControl("mrs_string/kernel", "LINEAR");
            classifier->updControl("mrs_bool/output_classPerms", false);
            classifier->updControl("mrs_natural/nClasses", 1);
        }
        classifier->updControl("mrs_real/C", SVM_C);
        classifier->updControl("mrs_string/kernel", "RBF");
        //learning->updControl("SVMClassifier/svm_cl/mrs_string/mode", "train");
    } else {
    }
    learning->addMarSystem(classifier);

    /*
        learning->linkControl(
                              "WekaSink/wekasink/mrs_bool/resetStable",
    "mrs_bool/resetStable"
    );
        learning->linkControl(
                              "WekaSink/wekasink/mrs_string/currentlyPlaying",
    "mrs_string/currentlyPlaying");
        learning->linkControl(
                              "Annotator/annotator/mrs_natural/label",
    "mrs_natural/currentLabel");
    */
    // start off neutral?
    //learning->updControl("Annotator/annotator/mrs_natural/label", 5);

}

void Ears::make_nets()
{
    audio_stuff = new Series ("audio_stuff");
    audio_stuff->addMarSystem(audio_input);
    audio_stuff->updControl("mrs_natural/inSamples", EARS_HOPSIZE);
    audio_stuff->updControl("mrs_real/israte",
                            (mrs_real) ARTIFASTRING_INSTRUMENT_SAMPLE_RATE);

    force_stuff = new Series ("force_stuff");
    force_stuff->addMarSystem(force_input);
    force_stuff->updControl("mrs_natural/inSamples", EARS_HOPSIZE/2);
    force_stuff->updControl("mrs_real/israte",
                            (mrs_real) HAPTIC_SAMPLE_RATE);

    if ((mode == PREDICT_FILE) || (mode == TRAIN_FILE)) {
        audio_stuff->linkControl(
            "mrs_string/audio_filename",
            "Series/audio_input/SoundFileSource/audio_src/mrs_string/filename"
        );
        force_stuff->linkControl(
            "mrs_string/force_filename",
            "Series/force_input/SoundFileSource/force_src/mrs_string/filename"
        );
        /*
        par->linkControl(
        "mrs_string/csv_filename",
        "Series/audio_stuff/Series/audio_source/mrs_string/csv_filename"
        );
        */
        audio_stuff->linkControl(
            "mrs_real/currentLabel",
            "Series/audio_input/SoundFileSource/audio_src/mrs_real/currentLabel"
        );
        audio_stuff->linkControl(
            "mrs_string/labelNames",
            "Series/audio_input/SoundFileSource/audio_src/mrs_string/labelNames"
        );
        audio_stuff->linkControl(
            "mrs_bool/hasData",
            "Series/audio_input/SoundFileSource/audio_src/mrs_bool/hasData"
        );
        audio_stuff->linkControl(
            "mrs_bool/startStable",
            "Series/audio_input/SoundFileSource/audio_src/mrs_bool/startStable"
        );
        audio_stuff->linkControl(
            "mrs_natural/nLabels",
            "Series/audio_input/SoundFileSource/audio_src/mrs_natural/nLabels");
    }

    /*
    net->addMarSystem(new SoundFileSink ("dest"));
    net->updControl("SoundFileSink/dest/mrs_string/filename", "marsyas.wav");
    */

    audio_stuff->addMarSystem(audio_features);
    force_stuff->addMarSystem(force_features);

    parameters_input = new Inject ("parameters_input");
    parameters_input->updControl("mrs_natural/injectSize",
                                 PHYSICAL_PARAMETERS_SIZE);
    parameters_input->updControl("mrs_string/injectNames",
                                 //                        "finger,bow-bridge-distance,velocity");
                                 // "pitch,finger,bow-bridge-distance,force,velocity");
                                 PHYSICAL_PARAMETERS);

    // get the onObservations correct!
    parameters_input->updControl("mrs_realvec/inject",
                                 parameters_input_realvec);

    // FIXME: has nothing to do with the rest of the network;
    // move somewhere else
    csvFileSource = new CsvFileSource ("csv");
    csvFileSource->updControl("mrs_natural/inSamples", 1);


    //MarSystem par = new Parallel ("overall_par");
    /*
    if (!m_classification) {
    } else {
        learning->updControl("SVMClassifier/svm_cl/mrs_natural/nClasses",
                             7);
        learning->updControl("WekaSink/wekasink/mrs_string/labelNames",
                             "97, 98, 99, 100, 101, 102, 103");
    }
    */


    //net->addMarSystem(overall_par);
    // FIXME FIXME FIXME
#if 0
    if ((mode == PREDICT_FILE) || (mode == TRAIN_FILE)) {
        net->linkControl("Series/learning/Annotator/annotator/mrs_real/label",
                         "Parallel/inputs/mrs_real/currentLabel");
    }
    if (mode == TRAIN_FILE) {
        net->linkControl(
            "Series/learning/WekaSink/wekasink/mrs_bool/resetStable",
            "Parallel/inputs/mrs_bool/startStable");
        if (!m_classification) {
        } else {
            net->linkControl(
                "Series/learning/WekaSink/wekasink/mrs_natural/nLabels",
                "Parallel/inputs/mrs_natural/nLabels");
            net->updControl(
                "Series/learning/SVMClassifier/svm_cl/mrs_natural/nClasses",
                net->getctrl("Parallel/inputs/mrs_natural/nLabels"));
            net->linkControl(
                "Series/learning/WekaSink/wekasink/mrs_string/labelNames",
                "Parallel/inputs/mrs_string/labelNames");
        }

//    net->linkControl(
//"Series/learning/mrs_string/currentlyPlaying",
//"Series/audio_input/mrs_string/currentlyPlaying"
//);
        net->linkControl(
            "Series/learning/WekaSink/wekasink/mrs_string/currentlyPlaying",
            "Parallel/inputs/mrs_string/currentlyPlaying");

        // MUST be done after linking this with the main network!
        // but after getting the names
        learning->updControl("WekaSink/wekasink/mrs_string/filename",
                             arff_out_filename);
    }

#endif
    //if (EARS_HOPSIZE == EARS_WINDOWSIZE) {
        // this is so that we ignore the last tick.
        //audio_stuff->updControl("mrs_natural/inStabilizingDelay", 1);
    //}

    // make sure everything is hooked up.
    mrs_natural numObservations = 0;
    mrs_string labelNames = "";

    audio_stuff->update();
    force_stuff->update();
    num_audio_observations = audio_stuff->getctrl("mrs_natural/onObservations")->to<mrs_natural>();
    num_force_observations = force_stuff->getctrl("mrs_natural/onObservations")->to<mrs_natural>();

    labelNames += audio_stuff->getctrl("mrs_string/onObsNames")->to<mrs_string>();
    labelNames += force_stuff->getctrl("mrs_string/onObsNames")->to<mrs_string>();
    labelNames += PHYSICAL_PARAMETERS;
    numObservations = num_audio_observations + num_force_observations
                      + PHYSICAL_PARAMETERS_SIZE;

    // debug info
#if 0
    cout<<audio_stuff->getctrl("mrs_natural/onObservations")->to<mrs_natural>()<<endl;
    cout<<force_stuff->getctrl("mrs_natural/onObservations")->to<mrs_natural>()<<endl;
    cout<<numObservations<<endl;
    cout<<labelNames<<endl;
#endif

    learning_input_realvec.create(numObservations, 1);
    learning->setctrl("mrs_natural/inObservations", numObservations);
    learning->setctrl("mrs_natural/inSamples", 1);
    learning->setctrl("mrs_real/israte", 22050.0/512.0);
    learning->setctrl("mrs_string/inObsNames", labelNames);
    learning->update();

    // not final for PREDICT_FILE, unfortunately.  ;(
    learning_output_realvec.create(
        learning->getctrl("mrs_natural/onObservations")->to<mrs_natural>(),
        learning->getctrl("mrs_natural/onSamples")->to<mrs_natural>()
    );

//    cout<<"---"<<endl;
//    cout<<learning->getctrl("mrs_natural/onObservations")->to<mrs_natural>()<<endl;
//    cout<<learning->getctrl("SVMClassifier/svm_cl/mrs_natural/nClasses")->to<mrs_natural>()<<endl;

    stabilizingDelay = audio_stuff->getctrl("mrs_natural/onStabilizingDelay")->to<mrs_natural>();
    //cout<<"stabiliz   "<<stabilizingDelay<<endl;
// for debug
    //net->put_html(std::cout);
    //audio_stuff->put_html(std::cout);
    //force_stuff->put_html(std::cout);
    //if (mode == PREDICT_FILE) {
    //  learning->put_html(std::cout);
    //}
}

/*
double Ears::getPitch()
{
    realvec data =
        yin_pitch->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
    return (double)data(0,0);
}
*/



// it's static
void Ears::get_rms_from_file(int num_frames, const char *in_filename,
                             double *rmss)
{
    MarSystem *pnet = new Series ("pnet");
    pnet->addMarSystem(new SoundFileSource ("src"));
    pnet->updControl("SoundFileSource/src/mrs_string/filename",
                     in_filename);
    pnet->addMarSystem(new ShiftInput ("shift_input"));
    pnet->updControl("ShiftInput/shift_input/mrs_natural/winSize",
                     EARS_WINDOWSIZE);
    pnet->addMarSystem(new Rms ("rms"));

    pnet->updControl("mrs_real/israte", 22050.0);
    pnet->updControl("mrs_natural/inSamples", EARS_HOPSIZE);
    for (int i=0; i<num_frames; i++)
    {
        pnet->tick();
        realvec data = pnet->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
        rmss[i] = (double)data(0,0);
    }
    delete pnet;
}

Marsyas::MarSystem* Ears::load_classifier(std::string training_filename)
{
    // adapted from MarSystemManager::getMarSystem(std::istream& is)
    // "is" is "input stream".  Kept for similarity to original
    // file, even though it's a really sucky variable name.
    ifstream is(training_filename.c_str());
    if (is.good()) {
        mrs_string skipstr;
        mrs_string mcomposite;
        is >> skipstr;
        is >> mcomposite;
        /* next line looks like:
         * # Type = MarSystemSubclass
         */
        is >> skipstr >> skipstr >> skipstr;
        mrs_string mtype;
        is >> mtype;


        /* next line looks like:
         * # Name = mname
         */
        is >> skipstr >> skipstr >> skipstr;
        mrs_string mname;
        is >> mname;

        // we assume it's always this type
        MarSystem* msys = new SVMClassifier("svm_cl");

        msys->setName(mname);
        msys->setParent(NULL);

        //delete all children MarSystems in a (prototype) Composite
        //and read and link (as possible) local controls
        is >> *msys;

        msys->update();


        is.close();
        return msys;
    } else {
        return NULL;
    }
#if 0
    /* Create a MarSystem object from an input stream in .mpl format
     * ( this is the format created by MarSystem::put(ostream& o) )
     */
    mrs_string skipstr;
    mrs_string mcomposite;
    mrs_natural i;
    bool isComposite;
    mrs_string marSystem = "MarSystem";
    mrs_string marSystemComposite = "MarSystemComposite";

    /* first line looks like:
     * # marSystem(Composite)
     */
    is >> skipstr;
    is >> mcomposite;
    if (mcomposite == marSystem)
        isComposite = false;
    else if (mcomposite == marSystemComposite)
        isComposite = true;
    else
    {
        MRSERR("Unknown MarSystemType" << mcomposite);
        MRSERR("skipstr = " << skipstr);
        return 0;
    }

    /* next line looks like:
     * # Type = MarSystemSubclass
     */
    is >> skipstr >> skipstr >> skipstr;
    mrs_string mtype;
    is >> mtype;


    /* next line looks like:
     * # Name = mname
     */
    is >> skipstr >> skipstr >> skipstr;
    mrs_string mname;
    is >> mname;

    MarSystem* msys = getPrototype(mtype);

    if (msys == 0)
    {
        if (compositesMap_.find(mtype) == compositesMap_.end())
        {
            MRSERR("MarSystem::getMarSystem - MarSystem " << mtype << " is not yet part of Marsyas");
            return 0;
        }
        else
        {
            // lazy composite registration
            registerComposite(mtype);
            msys = getPrototype(mtype);
        }
    }

    msys->setName(mname);
    msys->setParent(NULL);

    //delete all children MarSystems in a (prototype) Composite
    //and read and link (as possible) local controls
    is >> *msys;

    msys->update();

    workingSet_[msys->getName()] = msys; // add to workingSet

    //recreate the Composite destroyed above, relinking all
    //linked controls in its way
    if (isComposite)
    {
        /* If this is a composite system, we may have subcomponents
         * the number of subcomponents will be listed like this:
         * (blank line)
         * # nComponents = 3
         * (blank line)
         * Here, we read in the nComponents, then instantiate each component
         */
        is >> skipstr >> skipstr >> skipstr;
        mrs_natural nComponents;
        is >> nComponents;
        for (i=0; i < nComponents; ++i)
        {
            MarSystem* cmsys = getMarSystem(is, msys);
            if (cmsys == 0)
                return 0;
            msys->addMarSystem(cmsys);
        }
        msys->update();
    }
    return msys;
#endif
}

void Ears::hop() {
    audio_stuff->tick();
    force_stuff->tick();

    if (mode == TRAIN_FILE) {
        string currentlyPlaying = audio_input->getControl("SoundFileSource/audio_src/mrs_string/currentlyPlaying")->to<mrs_string>();
        if (currentlyPlaying != oldfile) {
            advanceFile();
        }

        // get info about whether the data is trustworthy
        //bool out_of_data =
        //    audio_input->getControl("SoundFileSource/audio_src/mrs_bool/currentLastTickWithData")->to<mrs_bool>();
        //cout<<"\t"<<out_of_data<<"\t";
        bool startStable =
            audio_input->getControl("SoundFileSource/audio_src/mrs_bool/startStable")->to<mrs_bool>();
        //cout<<"\t"<<startStable<<"\t";
        if (startStable) {
            ticks_count = 0;
        }
    }

    if (ticks_count < stabilizingDelay) {
        //cout<<ticks_count<<"  "<<stabilizingDelay<<"--";
        //cout<<endl;
        ticks_count++;
        return;
    } else {
        //cout<<ticks_count<<"  "<<stabilizingDelay;
    }

    realvec audio = audio_stuff->getctrl("mrs_realvec/processedData")->to<realvec>();
    realvec force = force_stuff->getctrl("mrs_realvec/processedData")->to<realvec>();
    for (int i=0; i<num_audio_observations; i++) {
        //cout<<audio(i)<<endl;
        learning_input_realvec(i) = audio(i);
    }
    //cout<<"---"<<endl;
    for (int i=0; i<num_force_observations; i++) {
        //cout<<force(i)<<endl;
        learning_input_realvec(i+num_audio_observations) = force(i);
    }
    //cout<<"---"<<endl;

    for (int i=0; i<PHYSICAL_PARAMETERS_SIZE; i++) {
        learning_input_realvec(i+num_audio_observations+num_force_observations) =
            parameters_input_realvec(i);
    }
    // setup learning
    if (mode == TRAIN_FILE) {
        learning->updControl("WekaSink/wekasink/mrs_string/currentlyPlaying",
                             audio_stuff->getControl("Series/audio_input/SoundFileSource/audio_src/mrs_string/currentlyPlaying")->to<mrs_string>());
        learning->updControl("Annotator/annotator/mrs_real/label",
                             audio_stuff->getControl("Series/audio_input/SoundFileSource/audio_src/mrs_real/currentLabel")->to<mrs_real>());
    }

    learning->process(learning_input_realvec, learning_output_realvec);
    //exit(1);
    //cout<<"\t"<<audio(0)<<endl;
    //cout<<"\t"<<learning_output_realvec(0)<<endl;
    //cout<<learning_output_realvec<<endl;
    //exit(1);

    ticks_count++;
}

