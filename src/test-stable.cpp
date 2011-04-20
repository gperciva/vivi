
#include "vivi_controller.h"

const double PLAY = 0.5;

int main() {
    ViviController *viviController = new ViviController();

	//for (int i=0; i < 3; i++) {
    NoteParams params;
    params.string_number = 1;
    params.dynamic = 0;
    params.finger_position = 0.25;
    params.bow_force = 1.0;

	double K = 1.1;
	unsigned int dyn = 0;

    viviController->filesNew("stable-test");
	viviController->load_ears_training(params.string_number, dyn,
		"train/0_0.mpl");
    viviController->note(params, dyn, K, PLAY);
	//}

    delete viviController;
}
