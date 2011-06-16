#ifndef VIVI_NOTE_PARAMS_H
#define VIVI_NOTE_PARAMS_H

class PhysicalActions {
public:
    PhysicalActions() {};

    int string_number;
    double dynamic; // to allow interpolation
    int get_dyn() {
        return dynamic + 0.5; // round
    }
    double finger_position;
    double bow_bridge_distance;
    double bow_force;
    double bow_velocity;

    void print();
};


#endif
