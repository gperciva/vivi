#ifndef VIVI_NOTE_PARAMS_H
#define VIVI_NOTE_PARAMS_H

class PhysicalActions {
public:
    // require user to specify manually
    PhysicalActions() {};
    // data
    int string_number;
    double dynamic; // to allow interpolation
    double finger_position;
    double bow_bridge_distance;
    double bow_force;
    double bow_velocity;
    // debug; must contain all above variables
    void print_params() {
        printf("PhysicalActions:\n");
        printf("\tst: %i\tdyn: %.3f\tfinger_position: %.3f\n",
               string_number, dynamic, finger_position);
        printf("\tbbd: %.3f\tbow_force: %.3f\tbow_velocity:%.3f\n",
               bow_bridge_distance, bow_force, bow_velocity);
    };
    // special access
    int get_dyn() {
        return dynamic + 0.5; // round
    }

};

class NoteBeginning {
public:
    // init to nothing
    NoteBeginning() {
        continue_previous_note = false;
        keep_force_without_trained = false;
        set_bow_position_along = -1; // this is "false"
    };
    // data
    bool continue_previous_note;
    bool keep_force_without_trained;
    double set_bow_position_along;
    // debug; must contain all above variables
    void print_params() {
        printf("NoteBeginning:\n");
        printf("\tcontinue_prev: %i\tkeep_force: %i\tset_bow_pos_along: %.3f\n",
               continue_previous_note,
               keep_force_without_trained,
               set_bow_position_along);
    };
};

class NoteEnding {
public:
    // init to nothing
    NoteEnding() {
        continue_next_note = false;
        lighten = false;
    };
    // data
    bool continue_next_note;
    bool lighten;
    // debug; must contain all above variables
    void print_params() {
        printf("NoteEnding:\n");
        printf("\tcontinue_next: %i\tlighten: %i\n",
               continue_next_note, lighten);
    };

};

#endif
