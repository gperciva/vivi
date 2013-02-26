#ifndef VIVI_DEFINES_H
#define VIVI_DEFINES_H

const int HOPSIZE = 441;
const int SAMPLE_RATE = 44100;
const double DH = ((double) HOPSIZE) / SAMPLE_RATE;

const bool REGRESSION = false;

//const int FINGERS = 5;
const int BASIC_FINGER_MIDIS_SIZE = 3;
const int BASIC_FINGER_MIDIS[] = {0, 1, 6};

const double SVM_C = 1.0;

const int CATEGORIES_NUMBER = 5;
// rounding down is correct
const int CATEGORIES_EXTREME = CATEGORIES_NUMBER / 2;
const int CATEGORIES_CENTER_OFFSET = CATEGORIES_EXTREME + 1;
const int CATEGORY_NULL = -99999;
const int CATEGORY_WAIT = 99999;
//const int CATEGORY_WEIRD = 123;
// marsyas can't handle negative values in regression
const int CATEGORY_POSITIVE_OFFSET = 100;

const int ATTACK_HARSH_HOPS = 2;
//const double MIN_ATTACK_TIME = 0.02; // don't give force judgements before this time
const double MIN_ATTACK_TIME = 0.00; // don't give force judgements before this time
const int CATS_LENGTH = 4; // in controller
//const int PITCH_MEANS = 4;
const int PITCH_MEANS = 3;
const double PITCH_NULL = -1;

const int NUM_DISTINCT_INSTRUMENTS = 3;


const double VIDEO_FPS = 25;

// is there a good way to export this with swig?  :(
const int TASK_IDLE = 0;
// string stuff
const int TASK_TRAINING = 1;
const int TASK_ACCURACY = 2;
// dyn stuff
const int TASK_VERIFY = 3;
const int TASK_STABLE = 4;
const int TASK_ATTACK = 5;
const int TASK_DAMPEN = 6;
// other
const int TASK_LILYPOND = 7;
const int TASK_RENDER_AUDIO = 8;
const int TASK_MIX_AUDIO = 9;
const int TASK_PLAY_AUDIO = 10;
const int TASK_HILL_CLIMBING = 11;
const int TASK_MIX_HILL = 12;

const int TASK_RENDER_VIDEO_PREVIEW = 13;
const int TASK_MIX_VIDEO = 14;
const int TASK_PLAY_VIDEO_PREVIEW = 15;
const int TASK_RENDER_VIDEO = 16;
const int TASK_PLAY_VIDEO = 17;

#endif
