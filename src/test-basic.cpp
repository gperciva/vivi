
#include "vivi_controller.h"
#include "dynamics.h"

const double SKIP = 0.5;
const double PLAY = 0.3;

int main() {
    ViviController *viviController = new ViviController();
    viviController->filesNew("basic_note");

    NoteBeginning begin;
    begin.physical.string_number = 1;
    begin.physical.dynamic = 0;
    begin.physical.finger_position = 0.25;
    begin.physical.bow_force = 1.0;
    begin.physical.bow_bridge_distance = get_distance(0);
    begin.physical.bow_velocity = get_velocity(0);

    viviController->basic(begin, PLAY, SKIP);

    delete viviController;
}
