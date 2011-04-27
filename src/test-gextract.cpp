
#include "ears.h"
#include <string>

// used for quick testing, with a normal violin.
#define CAT_2_FILE "train/audio_0_0.000_0.080_2.000_0.400.wav"

int main(int argc, char **argv) {
    // filename setup
    if (argc == 1) {
        std::cout<<"Usage: gextract COLLECTION_NAME.mf [extra tests]";
        std::cout<<std::endl;
        exit(1);
    }
    std::string mf_filename = argv[1];
    std::cout<<"Processing "<<mf_filename<<std::endl;

    std::string arff_filename = mf_filename;
    size_t suffix_position = mf_filename.find(".mf");
    arff_filename.replace(suffix_position, 3, ".arff");

    std::string mpl_filename = arff_filename;
    suffix_position = arff_filename.find(".arff");
    mpl_filename.replace(suffix_position, 5, ".mpl");

    // actual processing
    Ears *ears = new Ears();

    ears->set_training(mf_filename.c_str(), arff_filename.c_str());
    ears->processFile();
    ears->saveTraining(mpl_filename.c_str());

    if (argc > 2) {
        // extra memory tests, if requested
        std::cout<<"Performing extra tests"<<std::endl;
        std::cout<<"  resetting and retraining"<<std::endl;

        ears->reset();
        ears->set_training(mf_filename.c_str(), arff_filename.c_str());
        ears->processFile();
        ears->saveTraining(mpl_filename.c_str());

        // test file prediction
        std::cout<<"  predicting file (should be 2)"<<std::endl;
        ears->reset();
        ears->set_predict_wavfile(mpl_filename.c_str());
        // should be category 2
        // TODO: display this somehow?
        ears->predict_wavfile(CAT_2_FILE, "cat_2_file.cat");
        /*
                while (ears->tick_file()) {
                    std::cout << ears->getClass() << " ";
                }
        */
        std::cout << std::endl;

        // test buffer prediction
        std::cout<<"  predicting buffer (may be fairly random)"<<std::endl;
        ears->reset();
        ears->set_predict_buffer(mpl_filename.c_str());
        short* buf = new short[EARS_HOPSIZE];
        for (unsigned int j=0; j<10; j++) {
            for (unsigned int i=0; i<EARS_HOPSIZE; i++) {
                buf[i] = i % EARS_HOPSIZE;
            }
            ears->listenShort(buf);
            std::cout << ears->getClass() << " ";
        }
        delete [] buf;
        std::cout<<std::endl;
    }

    delete(ears);
}

