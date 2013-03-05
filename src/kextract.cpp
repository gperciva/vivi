
#include "ears.h"
#include <string>
#include <sstream>

std::string get_training_file(int distinct_instrument_number, int st)
{
    std::string inst_text;
    if (distinct_instrument_number == 0) {
        inst_text = "violin";
    }
    else if (distinct_instrument_number == 1) {
        inst_text = "viola";
    } else {
        inst_text = "cello";
    }

    std::ostringstream out;
    out << "final/" << inst_text << "/" << st << ".mpl";
    //std::cout<< out.str() <<std::endl;
    return out.str();
}

int main(int argc, char **argv) {
    // filename setup
    if (argc < 3) {
        std::cout<<"Usage: kextract filename.wav instrument_number string_number";
        std::cout<<std::endl;
        exit(1);
    }
    std::string wav_filename = argv[1];
    int distinct_instrument_number = atoi(argv[2]);
    int st = atoi(argv[3]);

    std::cout<<"Processing "<<wav_filename<<std::endl;
    std::string cats_out_filename = wav_filename;
    size_t suffix_position = cats_out_filename.find(".wav");
    cats_out_filename.replace(suffix_position, 4, ".cats"); 

    Ears *ears;
    // use classification
    ears = new Ears(distinct_instrument_number, 0, true);

    std::string mpl_filename = get_training_file(
        distinct_instrument_number, st);

    std::cout << "reading from "<<mpl_filename << std::endl;
    ears->set_predict_wavfile(mpl_filename.c_str());
    ears->predict_wavfile(wav_filename.c_str(), cats_out_filename.c_str());


    delete(ears);
}

