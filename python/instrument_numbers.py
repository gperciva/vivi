#!/usr/bin/env python

import os.path

DISTINCT_INSTRUMENT_NUMBERS = [
    0,
    0,
    0,
    0,
    0,
    1,
    1,
    2,
    2,
    2,
    ]
INSTRUMENT_NAMES = [
  "violin 1",
  "violin 2",
  "violin 3",
  "violin 4",
  "violin 5",
  "viola 1",
  "viola 2",
  "cello 1",
  "cello 2",
  "cello 3",
    ]

DISTINCT_INSTRUMENT_NAMES = [
  "violin",
  "violin",
  "violin",
  "violin",
  "violin",
  "viola",
  "viola",
  "cello",
  "cello",
  "cello",
  ]
# no, don't expand this one!
INSTRUMENT_TYPE_STRING_PITCHES = [
  [55.0, 62.0, 69.0, 76.0],
  [48.0, 55.0, 62.0, 69.0],
  [36.0, 43.0, 50.0, 57.0],
  ]

def get_string(inst_type, midi_pitch):
    for st, pitch in enumerate(
            INSTRUMENT_TYPE_STRING_PITCHES[inst_type]):
        if midi_pitch < pitch:
            return st - 1
    return 3


def distinct_instrument_name(instrument_number):
    return DISTINCT_INSTRUMENT_NAMES[
        distinct_instrument_number(instrument_number) ]

def get_distinct_instrument_number(instrument_number):
    return DISTINCT_INSTRUMENT_NUMBERS[instrument_number]


def distinct_instrument_index(instrument_number):
    for i, distinct_instrument_number in enumerate(DISTINCT_INSTRUMENT_NUMBERS):
        if instrument_number < distinct_instrument_number:
            return i-1
    return len(DISTINCT_INSTRUMENT_NUMBERS)-1

def instrument_name_from_filename(filename):
    dirs = filename.split("/")
    instrument_name = None
    for i, portion in enumerate(dirs):
        try:
            distinct_instrument_number = DISTINCT_INSTRUMENT_NAMES.index(portion)
            instrument_name = portion
            filename_index = i
        except ValueError:
            continue
    if not instrument_name:
        basename = os.path.splitext(os.path.basename(filename))[0]
        splitbasename = basename.split("-")
        for i, portion in enumerate(splitbasename):
            try:
                distinct_instrument_number = DISTINCT_INSTRUMENT_NAMES.index(portion)
                instrument_name = portion
                filename_index = i
            except ValueError:
                continue
    try:
        part_number = int(splitbasename[filename_index + 1]) - 1
    except:
        part_number = 0
    #instrument_number = DISTINCT_INSTRUMENT_NUMBERS[distinct_instrument_number] + part_number
    return instrument_name, distinct_instrument_number, part_number


