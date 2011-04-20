
#include "vivi_controller.h"

//const double SKIP = 0.5;
//const double PLAY = 0.3;
const double SKIP = 0.01;
const double PLAY = 0.01;

int main() {
    ViviController *viviController = new ViviController();

    NoteParams params;
    params.string_number = 1;
    params.dynamic = 0;
    params.finger_position = 0.25;
    params.bow_force = 1.0;

    viviController->basic(params, PLAY, SKIP, "foo");

    delete viviController;
}
