
#include "vivi_controller.h"
#include "dynamics.h"

const double PLAY = 0.5;

int main() {
    ViviController *viviController = new ViviController();
    Dynamics *dynamics = new Dynamics();

    PhysicalActions params;
    params.string_number = 0;
    params.dynamic = 0;
    params.finger_position = 0.0;
    params.bow_force = 1.0;
    params.bow_bridge_distance = dynamics->get_distance(0);
    params.bow_velocity = dynamics->get_velocity(0);

    double K = 1.05;
    unsigned int dyn = 0;

    viviController->filesNew("stable-test");
    viviController->comment("Stable test, 0 0");
    viviController->load_ears_training(params.string_number, dyn,
                                       "cache/final/0_0.mpl");
    viviController->note(params, K, PLAY);
    //}

    delete dynamics;
    delete viviController;
}
