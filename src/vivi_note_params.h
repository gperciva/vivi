#ifndef VIVI_NOTE_PARAMS_H
#define VIVI_NOTE_PARAMS_H

typedef struct {
    int string_number;
    double dynamic; // to allow interpolation
    double finger_position;
    double bow_bridge_distance;
    double bow_force;
    double bow_velocity;
} PhysicalActions;


#endif
