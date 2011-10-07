
#include "ears.h"
#include <string>

int main(int argc, char **argv) {
    // filename setup
    if (argc == 1) {
        std::cout<<"Usage: gextract MPLFILENAME.mpl WAVFILE.wav";
        std::cout<<std::endl;
        exit(1);
    }
    std::string mpl_filename = argv[1];
    std::string wav_filename = argv[2];

    // actual processing
    Ears *ears = new Ears();

    ears->set_predict_wavfile(mpl_filename.c_str());
        // should be category 2
        // TODO: display this somehow?
    ears->predict_wavfile(wav_filename.c_str(), "test-predict-wavfile.cat");

    delete(ears);
}

