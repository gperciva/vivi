
#include "ears.h"
#include <string>

//#define TEST_REDO
//#define TEST_FILE
//#define TEST_MEMORY

// used for quick testing, with a normal violin.
//#define CAT_2_FILE "train/cello/cello5_0_0.000_0.133_2.853_0.260_1.wav"
//#define CAT_2_FILE "train/violin/violin0_3_0.000_0.133_0.239_0.330_1.wav"
//#define CAT_2_FILE "train/violin/violin-0_0_0.000_0.092_0.909_0.400_1.wav"


int main(int argc, char **argv) {
    // filename setup
    if (argc < 3) {
        std::cout<<"Usage: gextract COLLECTION_NAME.mf instrument_number [extra tests]";
        std::cout<<std::endl;
        exit(1);
    }
    std::string mf_filename = argv[1];
    std::cout<<"Processing "<<mf_filename<<std::endl;
    int distinct_instrument_number = atoi(argv[2]);

    std::string arff_filename = mf_filename;
    size_t suffix_position = mf_filename.find(".mf");
    arff_filename.replace(suffix_position, 3, ".arff");

    std::string mpl_filename = arff_filename;
    suffix_position = arff_filename.find(".arff");
    mpl_filename.replace(suffix_position, 5, ".mpl");

    Ears *ears;
    if (argc > 3) {
        // use classification
        ears = new Ears(distinct_instrument_number, 0, true);
    } else {
        ears = new Ears(distinct_instrument_number, 0);
    }

    // actual processing
    ears->set_training(mf_filename.c_str(), arff_filename.c_str());
    ears->processFile();
    ears->saveTraining(mpl_filename.c_str());

#ifdef TEST_REDO
    ears->reset();
    ears->set_training(mf_filename.c_str(), arff_filename.c_str());
    ears->processFile();
    ears->saveTraining(mpl_filename.c_str());
#endif

#ifdef TEST_FILE
    ears->set_predict_wavfile(mpl_filename.c_str());
    ears->predict_wavfile(CAT_2_FILE, "cat_2_file.cat");
#endif

#ifdef TEST_MEMORY
    // extra memory tests, if requested
    std::cout<<"Performing extra tests"<<std::endl;
    std::cout<<"  resetting and retraining"<<std::endl;

    ears->set_training(mf_filename.c_str(), arff_filename.c_str());
    ears->processFile();
    ears->saveTraining(mpl_filename.c_str());

    // test file prediction
    std::cout<<"  predicting file (should be 2)"<<std::endl;
    ears->set_predict_wavfile(mpl_filename.c_str());
    // should be category 2
    // TODO: display this somehow?
    ears->predict_wavfile(CAT_2_FILE, "cat_2_file.cat");
    std::cout << std::endl;

    // test buffer prediction
    std::cout<<"  predicting buffer (may be fairly random)"<<std::endl;
    ears->set_predict_buffer(mpl_filename.c_str());
    short* buf = new short[EARS_HOPSIZE];
    for (int j=0; j<10; j++) {
        for (int i=0; i<EARS_HOPSIZE; i++) {
            buf[i] = i % EARS_HOPSIZE;
        }
        ears->listenShort(buf);
        std::cout << ears->getClass() << " ";
    }
    delete [] buf;
    std::cout<<std::endl;
#endif

    delete(ears);
}

