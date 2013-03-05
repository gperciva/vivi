
#include "vivi_controller.h"
#include "dynamics.h"

const double PLAY = 1.0;

int main() {
    int inst = 0;
    ViviController *viviController = new ViviController(inst);

    NoteBeginning begin;
    begin.physical.string_number = 0;
    begin.physical.dynamic = 0;
    begin.physical.finger_position = 0.0;
    begin.physical.bow_force = 2.0;
    begin.physical.bow_bridge_distance = get_distance(inst, 0);
    begin.physical.bow_velocity = get_velocity(inst, 0);
    NoteEnding end;
    //end.lighten_bow_force = true;
    //end.keep_bow_velocity = true;

    double K = 1.10;
    double dampen = 0.5;

    viviController->filesNew("test-dampen");
    viviController->load_ears_training(begin.physical.string_number,
                                       "final/violin/0.mpl");
    viviController->set_stable_K(0, 0, 0, K);
    viviController->set_dampen(0, 0, dampen);
    viviController->note(begin, PLAY, end);
    viviController->rest(1.0);

    delete viviController;
}
