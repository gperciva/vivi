#include "vivi_note_params.h"
#include <stdio.h>

void PhysicalActions::print() {
    printf("st: %i\tdyn: %.3f\tfinger_position: %.3f\n",
           string_number, dynamic, finger_position);
    printf("\tbbd: %.3f\tbow_force: %.3f\tbow_velocity:%.3f\n",
           bow_bridge_distance, bow_force, bow_velocity);
}

