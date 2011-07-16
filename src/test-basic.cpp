
#include "vivi_controller.h"
#include "dynamics.h"

const double SKIP = 0.5;
const double PLAY = 0.3;

int main() {
    ViviController *viviController = new ViviController();
    viviController->filesNew("basic_note");

    PhysicalActions params;
    params.string_number = 1;
    params.dynamic = 0;
    params.finger_position = 0.25;
    params.bow_force = 1.0;
    params.bow_bridge_distance = get_distance(0);
    params.bow_velocity = get_velocity(0);

    viviController->basic(params, PLAY, SKIP);

    delete viviController;
}
