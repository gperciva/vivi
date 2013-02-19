
#include "vivi_controller.h"
#include "dynamics.h"

const double PLAY = 4.0;

int main() {
    int inst = 0;
    ViviController *viviController = new ViviController(inst);

    NoteBeginning begin;
    begin.physical.string_number = 0;
    begin.physical.dynamic = 0;
    begin.physical.finger_position = 0.19;
    begin.physical.bow_force = 1.5;
    begin.physical.bow_bridge_distance = get_distance(inst, 0);
    begin.physical.bow_velocity = get_velocity(inst, 0);
    begin.midi_target = 59;
    NoteEnding end;

    double K = 1.05;

    viviController->filesNew("test-pitch");
    viviController->comment("pitch test, 0 0");
    viviController->load_ears_training(begin.physical.string_number,
                                       "final/violin/0.mpl");
    viviController->set_stable_K(0, 0, 0, K);
    viviController->note(begin, PLAY, end);

    delete viviController;
}
