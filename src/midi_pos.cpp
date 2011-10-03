#include "midi_pos.h"

const double SEMITONE = pow(2, 1.0/12);

double midi2freq(double midi) {
    return 440.0 * pow(2, (midi-69)/12.0);
}

double midi2pos(double relative_midi) {
    return 1.0 - 1.0 / pow(SEMITONE, relative_midi);
}

double pos2midi(double position) {
    return 12.0 * log(1.0 / (1.0-position)) / log(2.0);
}


