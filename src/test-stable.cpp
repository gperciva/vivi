
#include "vivi_controller.h"
#include "dynamics.h"

const double PLAY = 0.25;

#define E 0
#define CELLO 0
#define NOTES 1
#define MULTI 0

int main() {
    int dyn = 0;
#if CELLO
    int inst = 2;
#else
    int inst = 0;
#endif
    ViviController *viviController = new ViviController(inst);

    NoteBeginning begin;
    begin.physical.dynamic = dyn;
#if CELLO
    int st = 0;
#else
#if E
    int st = 3;
#else
    int st = 0;
#endif
#endif
    begin.physical.string_number = st;
    begin.physical.finger_position = 0.0;
    //begin.physical.finger_position = 0.056;
    //begin.physical.finger_position = 0.109;
    //begin.physical.finger_position = 0.86;
    //begin.physical.finger_position = 0.10;
    //begin.physical.finger_position = 0.0;
    //begin.physical.finger_position = 0.204;
    //begin.physical.finger_position = 0.109;
    //begin.midi_target = 55 + 1;
    //begin.midi_target = 55 + 7*st + 2;
    begin.midi_target = 55 + 7*st + 0;
    //begin.midi_target = -1;
#if CELLO
    begin.midi_target = -1;
    begin.midi_target = 36+2;
#else
    //begin.midi_target = 55 + 7*st + 0;
#endif

#if CELLO
    begin.physical.bow_force = 12.0;
#else
    begin.physical.bow_force = 1.0;
#endif
    //begin.physical.bow_force = 5.5;
    //begin.physical.bow_force = 7.284050;
    begin.physical.bow_bridge_distance = get_distance(inst, dyn);
    begin.physical.bow_velocity = get_velocity(inst, dyn);
    NoteEnding end;

#if CELLO
    double K = 0.15;
#else
    double K = 0.1;
    double K_main = 0.05;
    //double K = 0.0;
#endif

    viviController->filesNew("test-stable");
    viviController->comment("Stable test, 0 0");
#if MULTI
    viviController->load_ears_training(0,
                                       "final/violin/0.mpl");
    viviController->load_ears_training(1,
                                       "final/violin/1.mpl");
    viviController->load_ears_training(2,
                                       "final/violin/2.mpl");
    viviController->load_ears_training(3,
                                       "final/violin/3.mpl");
    for (int ast=0; ast < 4; ast++) {
        for (int adyn=0; adyn<4; adyn++) {
    viviController->set_stable_K(ast, adyn, 0, K);
    viviController->set_stable_K(ast, adyn, 1, K);
    viviController->set_stable_K(ast, adyn, 2, K);
        }
    }
#else
    viviController->set_stable_K(st, dyn, 0, K);
    viviController->set_stable_K(st, dyn, 1, K);
    viviController->set_stable_K(st, dyn, 2, K);

    viviController->set_stable_K_main(st, dyn, 0, K_main);
    viviController->set_stable_K_main(st, dyn, 1, K_main);
    viviController->set_stable_K_main(st, dyn, 2, K_main);
#if E
    viviController->load_ears_training(begin.physical.string_number,
                                       "final/violin/3.mpl");
#else
    viviController->load_ears_training(begin.physical.string_number,
                                       "final/violin/0.mpl");
#endif
#endif

#if CELLO
    viviController->load_ears_training(begin.physical.string_number,
                                       "final/cello/0.mpl");
#endif

    //end.keep_bow_velocity = true;
    //end.lighten_bow_force = true;
#if NOTES
#if MULTI
    for (int i=0; i<120; i++) {
        begin.physical.string_number = (i / 15) % 4;
        //std::cout<<begin.physical.string_number<<std::endl;
        viviController->note(begin, 0.5, end);
        begin.physical.bow_velocity *= -1;
        //viviController->note(begin, PLAY, end);
    }
#else
    viviController->note(begin, PLAY, end);
    //begin.physical.bow_velocity *= -1;
    //viviController->note(begin, PLAY, end);
#endif
#else
    short array[HOPSIZE];
    viviController->continuous(array, begin.physical, 0.0);
#endif

    //viviController->rest(0.5);
    delete viviController;
}
