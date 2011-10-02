#ifndef VIVI_DEFINES_H
#define VIVI_DEFINES_H

const int HOPSIZE = 256;
const int SAMPLE_RATE = 44100;

const int BASIC_FINGER_MIDIS_SIZE = 2;
const int BASIC_FINGER_MIDIS[] = {0, 6};

const int CATEGORIES_NUMBER = 7;
// rounding down is correct
const int CATEGORIES_EXTREME = CATEGORIES_NUMBER / 2;
const int CATEGORIES_CENTER_OFFSET = CATEGORIES_EXTREME + 1;
const int CATEGORY_NULL = -99999;
// marsyas can't handle negative values in regression
const int CATEGORY_POSITIVE_OFFSET = 100;


#endif
