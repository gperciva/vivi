
#include "vivi_controller.h"

//const double SKIP = 0.5;
//const double PLAY = 0.3;
const double SKIP = 0.01;
const double PLAY = 0.01;

int main() {
    ViviController *viviController = new ViviController();

    PhysicalActions actions;
    actions.string_number = 1;
    actions.finger_position = 0.25;
    actions.bow_bridge_distance = 0.1;
    actions.bow_force = 1.0;
    actions.bow_velocity = 0.2;

    viviController->basic(actions, PLAY, SKIP, "foo");

    delete viviController;
}
