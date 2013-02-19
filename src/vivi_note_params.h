#ifndef VIVI_NOTE_PARAMS_H
#define VIVI_NOTE_PARAMS_H

#include <string>
//#include <boost/format.hpp>

#define MAX_LINE_LENGTH 2048

// to be used inside NoteBeginning and NoteEnding
class PhysicalActions {
public:
    // require user to specify manually
    PhysicalActions() {
        string_number = -1;
        dynamic = 0.0;
        finger_position = 0.0;
        bow_bridge_distance = 0.0;
        bow_force = 0.0;
        bow_velocity = 0.0;
    };
    // data
    int string_number;
    double dynamic; // to allow interpolation
    double finger_position;
    double bow_bridge_distance;
    double bow_force;
    double bow_velocity;
    // debug; must contain all above variables
    void print_params() {
        /*
            printf("PhysicalActions:\n");
            printf("\tst: %i\tdyn: %.3f\tfinger_position: %.3f\n",
                   string_number, dynamic, finger_position);
            printf("\tbbd: %.3f\tbow_force: %.3f\tbow_velocity:%.3f\n",
                   bow_bridge_distance, bow_force, bow_velocity);
        */
        printf("st: %i\td: %.1f\tfp: %.2f\t",
               string_number, dynamic, finger_position);
        printf("bbd: %.2f\tbf: %.2f\tbv: %.2f\n",
               bow_bridge_distance, bow_force, bow_velocity);
    };
    std::string params_text() {
        char textline[MAX_LINE_LENGTH];
        sprintf(textline,
                "st: %i\td: %.1f\tfp: %.2f\tbbd: %.2f\tbf: %.2f\tbv: %.2f\n",
                string_number, dynamic, finger_position,
                bow_bridge_distance, bow_force, bow_velocity);
        return std::string(textline);
    }
    // special access
    int get_dyn() {
        return dynamic + 0.5; // round
    }

};

class NoteBeginning {
public:
    // init to nothing
    NoteBeginning() {
        ignore_finger = false;
        keep_bow_force = false;
        keep_ears = false;
        set_bow_position_along = -1; // this is "false"
        midi_target = 0.0;
    };
    // data
    PhysicalActions physical;
    bool ignore_finger;
    bool keep_bow_force;
    bool keep_ears;
    double set_bow_position_along;
    double midi_target;
    // debug; must contain all above variables
    void print_params() {
        /*
            printf("NoteBeginning:\n");
            printf("\tignore_finger: %i\tkeep_bow_force: %i\tset_bow_pos_along: %.3f\n",
                    ignore_finger,
                    keep_bow_force,
                    set_bow_position_along);
        */
        printf("begin\n");
        printf("%s", physical.params_text().c_str());
        printf("if: %i\tkbf: %i\tke: %i\tsbpa: %.3f\tmidi: %.2f\n",
               ignore_finger,
               keep_bow_force,
               keep_ears,
               set_bow_position_along,
               midi_target);
    };
    std::string params_text() {
        // don't include final \n
        char textline[MAX_LINE_LENGTH];
        sprintf(textline,
                "begin\n#\t%s#\tif: %i\tkbf: %i\tke: %i\tsbpa: %.3f\tmidi: %.2f",
                physical.params_text().c_str()
                , ignore_finger, keep_bow_force, keep_ears,
                set_bow_position_along, midi_target);
        return std::string(textline);
    }
};

class NoteEnding {
public:
    // init to nothing
    NoteEnding() {
        lighten_bow_force = false;
        //let_string_vibrate = false;
        keep_bow_velocity = false;
        midi_target = 0.0;
    };
    // data
    PhysicalActions physical;
    bool lighten_bow_force;
    //bool let_string_vibrate;
    bool keep_bow_velocity;
    double midi_target;
    // debug; must contain all above variables
    void print_params() {
        /*
            printf("NoteEnding:\n");
            printf("\tlighten_bow_force: %i\tlet_string_vibrate %i\tkeep_bow_velocity: %i\n",
                   lighten_bow_force, let_string_vibrate, keep_bow_velocity);
        */
        printf("end\n");
        printf("%s", physical.params_text().c_str());
        printf("lbf: %i\tkbv: %i\tmidi: %.2f\n",
               lighten_bow_force, //let_string_vibrate,
               keep_bow_velocity, midi_target);
    };
    std::string params_text() {
        // don't include final \n
        char textline[MAX_LINE_LENGTH];
        sprintf(textline,
                "end\n#\t%s#\tlbf: %i\tkbv: %i\tmidi: %.2f",
                physical.params_text().c_str(),
                lighten_bow_force, //let_string_vibrate,
                keep_bow_velocity, midi_target);
        return std::string(textline);
    }

};

#endif
