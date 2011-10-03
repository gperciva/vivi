#ifndef MIDI_POS_H
#define MIDI_POS_H

// conversion utilities for midi, frequency, and position
#include <math.h>

double midi2freq(double midi);

double midi2pos(double relative_midi);

double pos2midi(double position);

#endif
