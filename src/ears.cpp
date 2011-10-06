
#include "ears.h"
#include <string.h>
#include "actions_file.h"

#define REGRESSION

#define FULL_VIOLIN_PARAMS // actually does not include string
#define PER_DYNS_PARAMS

#ifndef LEAN
#else
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
//#include "marsyas/.h"
#endif


using namespace Marsyas;
#include <iostream>
using namespace std;

#include <limits.h>

#include "midi_pos.h"
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

// C++ requires an external definition of static member variables!
//MarSystemManager Ears::mng;


Ears::Ears() {
    audio_input_realvec.create(EARS_HOPSIZE);

    // needed to avoid a segfault
    net = NULL;
    csvFileSource = NULL;
    reset();

    // ick!
    hopsize_array = new short[EARS_HOPSIZE];

    // temp workaround for single-dyn and marsyas "I get confused
    // when I have all attributes being the same" bug
}

Ears::~Ears() {
    if (net != NULL) delete net; // automatically deals with children
    delete [] hopsize_array;
    if (csvFileSource != NULL) delete csvFileSource;
}

void Ears::reset()
{
    if (net != NULL) delete net; // automatically deals with children
    if (csvFileSource != NULL) delete csvFileSource;

    net = NULL;
    learning = NULL;
    classifier = NULL;
    pitchdiff = NULL;
    harmonics = NULL;
    audio_input = NULL;
    csvFileSource = NULL;

    mode = NONE;
    arff_out_filename = "";
    in_filename = "";

    audio_input_realvec.create(EARS_HOPSIZE);
#ifdef FULL_VIOLIN_PARAMS
    parameters_input_realvec.create(5,1);
#else
    parameters_input_realvec.create(1,1);
#endif

    parameters_input = NULL;

    ticks_count = 0;
}

void Ears::resetTicksCount() {
    ticks_count = 0;
}


bool Ears::set_training(const char *mf_in_filename,
                        const char *arff_out_filename_get)
{
    reset();
    mode = TRAIN_FILE;
    arff_out_filename.assign(arff_out_filename_get);
    in_filename.assign(mf_in_filename);
    make_features();
    make_learning();
    make_input();
    make_net();
    return true;
}

bool Ears::set_predict_wavfile(const char *training_filename)
{
    reset();
    mode = PREDICT_FILE;

    ifstream pluginStream(training_filename);
    if (pluginStream.good()) {
        classifier = mng.getMarSystem(pluginStream);
        make_features();
        make_learning();
        make_input();
        make_net();
        return true;
    } else {
        printf("ERROR: controller set_predict_wavfile cannot load file\n");
        return false;
    }
    //classifier->updControl("WekaSink/wekasink/mrs_string/filename", m_filename);
}

bool Ears::set_predict_buffer(const char *training_filename)
{
    reset();
    mode = PREDICT_BUFFER;
    ifstream pluginStream(training_filename);
    if (pluginStream.good()) {
        classifier = mng.getMarSystem(pluginStream);
        make_features();
        make_learning();
        make_input();
        make_net();
        return true;
    } else {
        printf("ERROR: controller set_predict_buffer cannot load file\n");
        return false;
    }
}

void Ears::predict_wavfile(const char *wav_in_filename,
                           const char *cats_out_filename)
{
    in_filename.assign(wav_in_filename);
    audio_input->updControl("SoundFileSource/gextract_src/mrs_string/filename", in_filename);
    // must be done after setting the filename!
    stabilizingDelay = net->getctrl("mrs_natural/onStabilizingDelay")->to<mrs_natural>();

    //get_info_file(wav_in_filename);
    //cout<<"aaa " <<wav_in_filename<<endl;
    string csv_filename = wav_in_filename;
    csv_filename.replace(csv_filename.length()-4, 4, ".csv");
    //cout<<"reading from: "<<csv_filename<<endl;
    csvFileSource->updControl("mrs_string/filename", csv_filename);

    ActionsFile *cats_out = new ActionsFile(cats_out_filename);
    cats_out->comment(wav_in_filename);

    ticks_count = 0;
    while (audio_input->getctrl("SoundFileSource/gextract_src/mrs_bool/hasData")->isTrue())
    {
        get_info_csv_file();
        net->tick();
        cats_out->category(ticks_count*dh, getClass());
        ticks_count++;
    }
    delete cats_out;
//zz
}

void Ears::saveTraining(const char *out_mpl_filename)
{
    ofstream clout;
    clout.open(out_mpl_filename);
    net->updControl("Series/learning/SVMClassifier/svm_cl/mrs_string/mode", "predict");
    // I don't know what I was thinking?  -April 13, cleanup.
    //net->updControl("Series/learning/WekaSink/wekasink/mrs_string/filename", "null.arff");
    //net->updControl("Series/learning/WekaSink/wekasink/mrs_string/currentlyPlaying", "null.wav");
    net->update();
    //clout << *net << endl;
    clout << *classifier << endl;
    clout.close();
}

/*
void Ears::loadTraining(const char *input_filename, bool inner)
{
    //printf("gextract:\t%s\t%i\n", input_filename, inner);
    ifstream pluginStream(input_filename);
    //net = mng.getMarSystem(pluginStream);
    classifier = mng.getMarSystem(pluginStream);
    //classifier->updControl("WekaSink/wekasink/mrs_string/filename", m_filename);
    prepTraining(inner);
}
*/

/*
void Ears::prepNet() {
    make_net();
}
*/


void Ears::set_extra_params(int st, double finger_position,
                            double bbd, double force, double velocity) {
    mrs_real pitch = string_finger_freq(st, finger_position);
    //cout<<"expected pitch: "<<pitch<<endl;

/*
    cout<<st<<' '<<finger_position<<'\t'<<pitch;
    cout<<'\t'<<bbd<<'\t'<<force<<'\t'<<velocity;
    cout<<endl;
    */
#ifdef FULL_VIOLIN_PARAMS
    parameters_input_realvec(0,0) = finger_position;
    parameters_input_realvec(1,0) = bbd;
    //parameters_input_realvec(2,0) = force;
    parameters_input_realvec(2,0) = velocity;
#else
    parameters_input_realvec(0,0) = finger_position;
#endif

    if (parameters_input != NULL) {
        parameters_input->updControl("mrs_realvec/inject", parameters_input_realvec);
    } else {
        cout<<"we need inject"<<endl;
    }
    if (pitchdiff != NULL) {
        pitchdiff->updControl("mrs_real/expectedPitch", pitch);
    } else {
        cout<<"we need pitchdiff"<<endl;
    }
    if (harmonics != NULL) {
        harmonics->updControl("mrs_real/base_frequency", pitch);
    }
}

void Ears::get_info_file(string filename) {
cout<<"Ears error: get_info_file() NOW UNUSED"<<endl;
/*
    // assume that we use '_' as the separator
    vector<string> SplitVec;
    boost::split(SplitVec, filename, boost::is_any_of("_"));

    int st = boost::lexical_cast<int>(SplitVec[1]);
    double finger_midi = boost::lexical_cast<double>(SplitVec[2]);
    double finger_position = midi2pos(finger_midi);
    double bbd = boost::lexical_cast<double>(SplitVec[3]);
    double force = boost::lexical_cast<double>(SplitVec[4]);
    double velocity = boost::lexical_cast<double>(SplitVec[5]);

    set_extra_params(st, finger_position, bbd, force, velocity);
    */
}

void Ears::get_info_csv_file() {
    csvFileSource->tick();
    mrs_realvec v = csvFileSource->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
    double st = v(0);
    double finger_position = v(1);
    double bbd = v(2);
    //double force = v(2);
    double force = 0.0;
    double velocity = v(3);
#ifdef PER_DYNS_PARAMS
    double epsilon;
    epsilon = (rand()/(RAND_MAX+1.0))*1.0e-6;
    bbd += epsilon;
    epsilon = (rand()/(RAND_MAX+1.0))*1.0e-6;
    velocity += epsilon;
#endif
    //cout<<st<<" "<<finger_position<<" "<<bbd<<" "<<velocity<<endl;
    set_extra_params(st, finger_position, bbd, force, velocity);
}

// ick, this doens't really belong here!
short* Ears::get_hopsize_array() {
    return hopsize_array;
}




//void Ears::listen(double *audio, double *bow_forces) {
void Ears::listen(double *audio) {
    for (int i=0; i<EARS_HOPSIZE; i++) {
        audio_input_realvec(0,i) = audio[i];
        //listen_buffer->data[0][i] = audio[i];
    }
    audio_input->updControl("RealvecSource/gextract_src/mrs_realvec/data", audio_input);
    net->tick();
    ticks_count++;
}

void Ears::listenShort(short *audio) {
    //cout<<"listenShort"<<endl;
    for (int i=0; i<EARS_HOPSIZE; i++) {
        audio_input_realvec(0,i) = ((mrs_real) audio[i]) / SHRT_MAX;
    }
    //cout<<"going to load"<<endl;
    audio_input->updControl("RealvecSource/gextract_src/mrs_realvec/data",
                            audio_input_realvec);
    //cout<<audio_input_realvec<<endl;
    //cout<<(*audio_input)<<endl;
    //cout<<audio_input->getControl("mrs_natural/onSamples")->to<mrs_natural>()<<endl;
    //cout<<"going to tick"<<endl;
    net->tick();
    ticks_count++;
    //cout<<"ticked"<<endl;

    /*
    if (pitchdiff != NULL) {
        realvec data =
            pitchdiff->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
        mrs_real pitch =
            pitchdiff->getctrl("mrs_real/expectedPitch")->to<mrs_real>();
        cout << data(0,0) << '\t' << pitch <<endl;
      }
    */
}


double Ears::getClass() {
    if (ticks_count > stabilizingDelay) {
        realvec data = net->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
        double value = data(0,0) - CATEGORY_POSITIVE_OFFSET;
        if (value != value) { // is a NaN
            value = CATEGORY_NULL;
        }
        return value;
    } else {
        return CATEGORY_NULL;
    }
}

double Ears::string_finger_freq(double st, double finger_position) {
    // FIXME: simplify this in maxima?
    double finger_midi = 12.0 * log(1.0/(1.0-finger_position))/log(2.0);
    double midi = 55 + 7*st + finger_midi;
    return 440.0 * pow(2, (midi-69)/12.0);
}


bool Ears::tick_file() {
    if (audio_input->getctrl("SoundFileSource/gextract_src/mrs_bool/hasData")->isTrue())
    {
        string currentlyPlaying =
            audio_input->getControl("SoundFileSource/gextract_src/mrs_string/currentlyPlaying")->to<mrs_string>();

        if (currentlyPlaying != oldfile) {
            //get_info_file(currentlyPlaying);
            string csv_filename = currentlyPlaying;
            csv_filename.replace(csv_filename.length()-4, 4, ".csv");
            csvFileSource->updControl("mrs_string/filename", csv_filename);
            oldfile = currentlyPlaying;
        }

        get_info_csv_file();
        net->tick();
        ticks_count++;
        return true;
    } else {
        return false;
    }
}

void Ears::processFile() {
    ticks_count = 0;
    while (audio_input->getctrl("SoundFileSource/gextract_src/mrs_bool/hasData")->isTrue())
    {
        string currentlyPlaying =
            audio_input->getControl("SoundFileSource/gextract_src/mrs_string/currentlyPlaying")->to<mrs_string>();

        if (currentlyPlaying != oldfile) {
            //get_info_file(currentlyPlaying);
            string csv_filename = currentlyPlaying;
            csv_filename.replace(csv_filename.length()-4, 4, ".csv");
            //cout<<csv_filename<<endl;
            csvFileSource->updControl("mrs_string/filename", csv_filename);
            oldfile = currentlyPlaying;
        }
        /*
        if (pitchdiff != NULL) {
            realvec data =
                pitchdiff->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
            mrs_real pitch =
                pitchdiff->getctrl("mrs_real/expectedPitch")->to<mrs_real>();
            cout << currentlyPlaying << '\t' << data(0,0) << '\t' << pitch <<endl;
        }
        */

        get_info_csv_file();
        net->tick();
        ticks_count++;
    }
}


void Ears::make_input() {
#ifndef LEAN
    audio_input = mng.create("Series", "audio_input");
#else
    audio_input = new Series("audio_input");
#endif

    if (mode == PREDICT_BUFFER) {
        audio_input->addMarSystem(mng.create("RealvecSource", "gextract_src"));
    }
    if (mode == TRAIN_FILE) {
        audio_input->addMarSystem(mng.create("SoundFileSource", "gextract_src"));
        audio_input->updControl("SoundFileSource/gextract_src/mrs_string/filename", in_filename);
#ifdef REGRESSION
        audio_input->updControl("SoundFileSource/gextract_src/mrs_bool/regression",true);
#endif
    }
    if (mode == PREDICT_FILE) {
        audio_input->addMarSystem(mng.create("SoundFileSource", "gextract_src"));

        /*
                audio_input->linkControl("mrs_bool/startStable",
                                         "SoundFileSource/gextract_src/mrs_bool/startStable"
                                        );

                audio_input->linkControl("mrs_string/currentlyPlaying",
                                         "SoundFileSource/gextract_src/mrs_string/currentlyPlaying"
                                        );
                audio_input->linkControl("mrs_natural/currentLabel",
                                         "SoundFileSource/gextract_src/mrs_natural/currentLabel"
                                        );
        */
    }
    audio_input->addMarSystem(mng.create("ShiftInput", "shift_input"));
    audio_input->updControl("ShiftInput/shift_input/mrs_natural/winSize",
                            EARS_WINDOWSIZE);

//audio_input->addMarSystem(mng.create("SoundFileSink", "dest"));
//audio_input->updControl("SoundFileSink/dest/mrs_string/filename", "marsyas.wav");

}

Marsyas::MarSystem *Ears::marPitch(string type, string name) {
    string series_name = name;
    series_name.append("_gain_series");
    string gain_pitch = "Gain/";
    gain_pitch.append(name);
    gain_pitch.append("/mrs_real/gain");

    MarSystem *net = mng.create("Series", series_name);
    net->addMarSystem(mng.create(type, name));
    net->addMarSystem(mng.create("Gain", name));
    net->linkControl(gain_pitch, "mrs_real/pitch_mult");

    return net;
}


Marsyas::MarSystem *Ears::timeDomain()
{
    MarSystem *net = mng.create("Fanout", "td");

//    net->addMarSystem(mng.create("Rms", "rms")); // better than mean!
//    net->addMarSystem(mng.create("PowerToAverageRatio", "par"));
//    net->addMarSystem(mng.create("MeanAbsoluteDeviation", "mad"));

    net->addMarSystem(mng.create("ZeroCrossings", "orig_zero"));

    MarSystem *yinseries = mng.create("Series", "yin_series");
    net->addMarSystem(yinseries);
    yin_pitch = mng.create("Yin", "yin");
    yinseries->addMarSystem(yin_pitch);
    pitchdiff = mng.create("PitchDiff", "pitchdiff");
    yinseries->addMarSystem(pitchdiff);
    //pitchdiff->updControl("mrs_bool/ignoreOctaves", true);
    //pitchdiff->updControl("mrs_bool/absoluteValue", true);
    yinseries->addMarSystem(mng.create("Clip", "clip"));
    yinseries->updControl("Clip/clip/mrs_real/range", 3.0);

    return net;
}

Marsyas::MarSystem *Ears::spectralDomain()
{
    MarSystem *net = mng.create("Fanout", "sd");

//    net->addMarSystem(mng.create("Centroid", "cntrd"));
//    net->addMarSystem(mng.create("Rolloff", "rlf"));
    net->addMarSystem(power_system("Centroid", 1.0/8.0));
    net->addMarSystem(power_system("Rolloff", 1.0/8.0));

    net->addMarSystem(power_system("Flux",1.0/2.0));

    harmonics = mng.create("HarmonicStrength", "harm");
    net->addMarSystem(harmonics);
    mrs_natural num_harmonics = 15;
    realvec harmonics_r(num_harmonics);
    for (int i=0; i<num_harmonics; i++) {
        harmonics_r(i) = i+1;
    }
    harmonics_r(num_harmonics-1) = 0.5;
    /*
    for (int i=0; i<num_harmonics; i++) {
        cout<<i<<"\t"<<harmonics_r(i)<<endl;
    }
    */
    harmonics->updControl("mrs_realvec/harmonics", harmonics_r);
    harmonics->updControl("mrs_natural/harmonicsSize", num_harmonics);
    harmonics->updControl("mrs_real/harmonicsWidth", 0.01);
    harmonics->updControl("mrs_natural/type", 2);

    mrs_real max_S_obs = 20.0 / 24.0;
    MarSystem *scf_trim = mng.create("Series", "scf_trim");
    net->addMarSystem(scf_trim);
    scf_trim->addMarSystem(mng.create("SCF", "scf"));
    scf_trim->addMarSystem(mng.create("RemoveObservations", "rem_scf"));
    scf_trim->updControl("RemoveObservations/rem_scf/mrs_real/highCutoff",
                         max_S_obs);
    MarSystem *sfm_trim = mng.create("Series", "sfm_trim");
    net->addMarSystem(sfm_trim);
    sfm_trim->addMarSystem(mng.create("SFM", "sfm"));
    sfm_trim->addMarSystem(mng.create("RemoveObservations", "rem_sfm"));
    sfm_trim->updControl("RemoveObservations/rem_sfm/mrs_real/highCutoff",
                         max_S_obs);

//    net->addMarSystem(mng.create("Sum", "sumspt"));
//    net->updControl("Sum/sumspt/mrs_string/mode", "sum_whole");
//    net->addMarSystem(power_system("Sum",1.0/8.0));

    MarSystem *flatness = mng.create("Series", "flatness");
    net->addMarSystem(flatness);
    flatness->addMarSystem(mng.create("RemoveObservations", "filt_obs"));
//    flatness->updControl("RemoveObservations/filt_obs/mrs_real/lowCutoff",
//                         0.0/44100.0*2.0);
    flatness->updControl("RemoveObservations/filt_obs/mrs_real/highCutoff",
                         10000.0/44100.0*2.0);
    flatness->addMarSystem(power_system("SpectralFlatnessAllBands",1.0/8.0));
    //flatness->addMarSystem(mng.create("SpectralFlatnessAllBands","sfab"));

    return net;
}

Marsyas::MarSystem *Ears::spectralDomainTrans()
{
    MarSystem *net = mng.create("Fanout", "sdt");

    net->addMarSystem(power_system("Rms",1.0/8.0));
    net->addMarSystem(power_system("AbsMax", 1.0/2.0));
    net->addMarSystem(mng.create("PowerToAverageRatio", "specral_par"));
    net->addMarSystem(power_system("Mean", 1.0/2.0));
    return net;
}

MarSystem *Ears::power_system(string name, double power) {
    MarSystem *net = mng.create("Series", name);
    net->addMarSystem(mng.create(name, name));
    net->addMarSystem(mng.create("MathPower", "mathpower"));
    net->updControl("MathPower/mathpower/mrs_real/exponent", power);
    return net;
}


void Ears::make_features() {
    audio_features = mng.create("Fanout", "audio_features");
    audio_features->addMarSystem( timeDomain() );
    //mar->linkControl("Fanout/main_fanout/Fanout/td/mrs_real/pitch_mult",
    //"mrs_real/pitch_mult");

    MarSystem *spectral = mng.create("Series", "spectral");
    audio_features->addMarSystem(spectral);
    spectral->addMarSystem(mng.create("Windowing", "hamming"));
    spectral->addMarSystem(mng.create("Spectrum","spk"));
    spectral->updControl("Spectrum/spk/mrs_real/cutoff", 1.0);
    spectral->addMarSystem(mng.create("PowerSpectrum", "pspk"));
    spectral->updControl("PowerSpectrum/pspk/mrs_string/spectrumType","power");
    spectral->linkControl("Spectrum/spk/mrs_real/cutoff", "mrs_real/cutoff");
//            spectral->addMarSystem(mng.create("RemoveObservations", "filt_obs"));
//            spectral->updControl("RemoveObservations/filt_obs/mrs_real/lowCutoff",
//                                 0.0/44100.0*2.0);
//            spectral->updControl("RemoveObservations/filt_obs/mrs_real/highCutoff",
//                                 10000.0/44100.0*2.0);

    /*
        MarSystem *noise = mng.create("Series", "noise");
        noise->addMarSystem(mng.create("RemoveObservations", "filt_obs"));
        noise->updControl("RemoveObservations/filt_obs/mrs_real/lowCutoff",
                             0.0/44100.0*2.0);
        noise->updControl("RemoveObservations/filt_obs/mrs_real/highCutoff",
                             180.0/44100.0*2.0);
        noise->addMarSystem(mng.create("Transposer", "trans"));
        noise->addMarSystem(mng.create("Rms", "rms_spect"));
        noise->addMarSystem(mng.create("MathPower", "mathpower"));
        noise->updControl("MathPower/mathpower/mrs_real/exponent", 1.0/8.0);
    */

    MarSystem *spect_fan = mng.create("Fanout", "spectral_fanout");
    spectral->addMarSystem(spect_fan);

//    spect_fan->addMarSystem( noise );
    spect_fan->addMarSystem( spectralDomain() );

    MarSystem *trans = mng.create("Series", "spect_trans");
    spect_fan->addMarSystem(trans);
    trans->addMarSystem(mng.create("Transposer", "trans"));
    trans->addMarSystem( spectralDomainTrans() );

}

void Ears::make_learning() {
    learning = mng.create("Series", "learning");

    learning->addMarSystem(mng.create("Annotator", "annotator"));
    if (mode == TRAIN_FILE) {
        learning->addMarSystem(mng.create("WekaSink", "wekasink"));

        learning->updControl("WekaSink/wekasink/mrs_bool/onlyStable",true);

        //learning->updControl("WekaSink/wekasink/mrs_natural/precision",10);
        learning->updControl("WekaSink/wekasink/mrs_natural/precision",20);
        learning->updControl("WekaSink/wekasink/mrs_natural/nLabels",7);
        //bool all = true;
// try combination

        // use regression or classification?
#ifdef REGRESSION
        learning->updControl("WekaSink/wekasink/mrs_bool/regression",true);
#endif
        // MUST be done after linking with main network, i.e. not here!
        //learning->updControl("WekaSink/wekasink/mrs_string/filename", m_filename);

        //learning->addMarSystem(mng.create("Classifier", "cl"));
//    learning->updControl("Classifier/cl/mrs_string/mode", "train");
//    learning->updControl("Classifier/cl/mrs_string/enableChild", "SVMClassifier/svmcl");
//    learning->updControl("Classifier/cl/mrs_natural/nClasses", 6);
    }

    if (classifier == NULL) {
        classifier = mng.create("SVMClassifier", "svm_cl");
        classifier->updControl("mrs_string/mode", "train");
        // FIXME: expriment with regression!
#ifdef REGRESSION
        classifier->updControl("mrs_string/svm", "NU_SVR");
        classifier->updControl("mrs_string/kernel", "LINEAR");
        classifier->updControl("mrs_bool/output_classPerms", false);
        classifier->updControl("mrs_natural/nClasses", 1);
#endif
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

void Ears::make_net() {
    net = mng.create("Series", "net");
    net->updControl("mrs_real/israte", 44100.0);
    net->updControl("mrs_natural/inSamples", EARS_HOPSIZE);

    net->addMarSystem(audio_input);
    /*
    net->addMarSystem(mng.create("SoundFileSink", "dest"));
    net->updControl("SoundFileSink/dest/mrs_string/filename", "marsyas.wav");
    */

    net->addMarSystem(audio_features);

    parameters_input = mng.create("Inject", "parameters_input");
#ifdef FULL_VIOLIN_PARAMS
    parameters_input->updControl("mrs_natural/injectSize", 3);
    parameters_input->updControl("mrs_string/injectNames",
                                 "finger,bow-bridge-distance,velocity");
    //"string,finger,bow-bridge-distance,force,velocity");
#else
    parameters_input->updControl("mrs_natural/injectSize", 1);
    parameters_input->updControl("mrs_string/injectNames",
                                 "finger");
#endif
    // get the onObservations correct!
    parameters_input->updControl("mrs_realvec/inject",
                                 parameters_input_realvec);
    net->addMarSystem(parameters_input);

    // FIXME: has nothing to do with the rest of the network;
    // move somewhere else
    csvFileSource = mng.create("CsvFileSource", "csv");
    csvFileSource->updControl("mrs_natural/inSamples", 1);


    net->addMarSystem(learning);

    //MarSystem par = mng.create("Parallel", "overall_par");


    //net->addMarSystem(overall_par);
    if ((mode == PREDICT_FILE) || (mode == TRAIN_FILE)) {
        /*
                 net->linkControl("Series/learning/mrs_natural/currentLabel",
                                 "Series/audio_input/mrs_natural/currentLabel");
        */
        net->linkControl("Series/learning/Annotator/annotator/mrs_real/label",
                         "Series/audio_input/SoundFileSource/gextract_src/mrs_real/currentLabel");
        /*
            net->linkControl(
        "Series/learning/mrs_bool/resetStable",
        "Series/audio_input/mrs_bool/startStable"
        );
        */
// temp?
    }
    if (mode == TRAIN_FILE) {
        net->linkControl(
            "Series/learning/WekaSink/wekasink/mrs_bool/resetStable",
            "Series/audio_input/SoundFileSource/gextract_src/mrs_bool/startStable"
        );

//    net->linkControl(
//"Series/learning/mrs_string/currentlyPlaying",
//"Series/audio_input/mrs_string/currentlyPlaying"
//);
        net->linkControl(
            "Series/learning/WekaSink/wekasink/mrs_string/currentlyPlaying",
            "Series/audio_input/SoundFileSource/gextract_src/mrs_string/currentlyPlaying"
        );

        // MUST be done after linking this with the main network!
        learning->updControl("WekaSink/wekasink/mrs_string/filename",
                             arff_out_filename);
    }

    if (EARS_HOPSIZE == EARS_WINDOWSIZE) {
        // this is so that we ignore the last tick.
        net->updControl("mrs_natural/inStabilizingDelay", 1);
    }
#ifdef REGRESSION
#else
    learning->updControl("SVMClassifier/svm_cl/mrs_natural/nClasses",
        7);
    learning->updControl("WekaSink/wekasink/mrs_string/labelNames",
        "97, 98, 99, 100, 101, 102, 103");
#endif

    // make sure everything is hooked up.
    net->update();

    stabilizingDelay = net->getctrl("mrs_natural/onStabilizingDelay")->to<mrs_natural>();
// for debug
    //net->put_html(std::cout);
}

double Ears::getPitch()
{
    realvec data =
        yin_pitch->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
    return (double)data(0,0);
}



// it's static
void Ears::get_rms_from_file(int num_frames, const char *in_filename,
                             double *rmss)
{
    MarSystem *pnet = mng.create("Series", "pnet");
    pnet->addMarSystem(mng.create("SoundFileSource", "src"));
    pnet->updControl("SoundFileSource/src/mrs_string/filename",
                     in_filename);
    pnet->addMarSystem(mng.create("ShiftInput", "shift_input"));
    pnet->updControl("ShiftInput/shift_input/mrs_natural/winSize",
                     EARS_WINDOWSIZE);
    pnet->addMarSystem(mng.create("Rms", "rms"));

    pnet->updControl("mrs_real/israte", 44100.0);
    pnet->updControl("mrs_natural/inSamples", EARS_HOPSIZE);
    for (int i=0; i<num_frames; i++)
    {
        pnet->tick();
        realvec data = pnet->getctrl("mrs_realvec/processedData")->to<mrs_realvec>();
        rmss[i] = (double)data(0,0);
    }
    delete pnet;
}

