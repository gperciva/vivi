
#include "vivi_controller.h"
#include "dynamics.h"

const double PLAY = 0.5;

int main() {
    ViviController *viviController = new ViviController();

    NoteBeginning begin;
    begin.physical.string_number = 0;
    begin.physical.dynamic = 0;
    begin.physical.finger_position = 0.0;
    begin.physical.bow_force = 1.0;
    begin.physical.bow_bridge_distance = get_distance(0);
    begin.physical.bow_velocity = get_velocity(0);
    NoteEnding end;

    double K = 1.05;
    int dyn = 0;

    viviController->filesNew("stable-test");
    viviController->comment("Stable test, 0 0");
    viviController->load_ears_training(begin.physical.string_number, dyn,
                                       "final/0_0.mpl");
    viviController->set_stable_K(0, 0, K);
    viviController->note(begin, PLAY, end);

    delete viviController;
}
