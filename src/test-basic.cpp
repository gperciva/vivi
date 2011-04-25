
#include "vivi_controller.h"
#include "dynamics.h"

//const double SKIP = 0.5;
//const double PLAY = 0.3;
const double SKIP = 0.01;
const double PLAY = 0.01;

int main() {
    ViviController *viviController = new ViviController();
    Dynamics *dynamics = new Dynamics();

    PhysicalActions params;
    params.string_number = 1;
    params.dynamic = 0;
    params.finger_position = 0.25;
    params.bow_force = 1.0;
    params.bow_bridge_distance = dynamics->get_distance(0);
    params.bow_velocity = dynamics->get_velocity(0);

    viviController->basic(params, PLAY, SKIP, "foo");

    delete dynamics;
    delete viviController;
}
