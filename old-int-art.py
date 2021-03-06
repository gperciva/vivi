#!/usr/bin/env python

##
# Copyright 2010--2011 Graham Percival
# This file is part of Artifastring.
#
# Artifastring is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Artifastring is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with Artifastring.  If not, see
# <http://www.gnu.org/licenses/>.
##

import os
import sys
import violin_instrument
import monowav
import curses
import numpy
import math

import multiprocessing
import time
import scipy.io.wavfile

import pyaudio
import aubio.aubiowrapper

# TODO: hack for current build system.
sys.path.append('python/')
sys.path.append('build/python/')
sys.path.append('build/swig/')
import actions_file
import vivi_defines
import dynamics
import midi_pos
HOPSIZE = vivi_defines.HOPSIZE

NUM_AUDIO_BUFFERS = 4

# for pitch and buffers
PRINT_EXTRA_DISPLAY = 1

TRAIN_DIR = "train/"

class Parameters():
    def __init__(self, st=0, fp=0, bp=.08, f=1.0, v=0.4, T=1.0):
        self.violin_string = st
        self.finger_position = fp
        self.bow_position = bp
        self.force = f
        self.velocity = v
        # HACK: kind-of.  Tension isn't really a normal "playing
        # parameter", but it _is_ still something under a
        # musician's control.
        self.tension_relative = T

def violin_process(instrument_type, instrument_number, params_queue, input_audio_queue,
        output_audio_queue, tension_queue):
    violin = violin_instrument.ViolinInstrument(instrument_type, instrument_number)
    buf = violin_instrument.shortArray(HOPSIZE)
    forces = violin_instrument.shortArray(HOPSIZE)

    params = params_queue.get()
    pc = violin.get_physical_constants(params.violin_string)
    tension_queue.put(pc.T)
    violin.finger(params.violin_string, params.finger_position)
    violin.bow(params.violin_string, params.bow_position,
               params.force, params.velocity)

    while True:
        while not params_queue.empty():
            params = params_queue.get()
            if params.tension_relative != 1.0:
                pc = violin.get_physical_constants(params.violin_string)
                pc.T *= params.tension_relative
                tension_queue.put(pc.T)
                violin.set_physical_constants(params.violin_string, pc)
            violin.finger(params.violin_string, params.finger_position)
            violin.bow(params.violin_string, params.bow_position,
                params.force, params.velocity)
        arr_audio, arr_forces = input_audio_queue.get()
        arr_audio = numpy.empty(HOPSIZE, dtype=numpy.int16)
        arr_forces = numpy.empty(HOPSIZE, dtype=numpy.int16)
        violin.wait_samples_forces_python(arr_audio, arr_forces)
        output_audio_queue.put( (arr_audio, arr_forces) )

class InteractiveViolin():

    def __init__(self, instrument_type, instrument_number, stdscr, audio_stream):
        self.instrument_type = instrument_type
        self.instrument_number = instrument_number
        self.stdscr = stdscr
        self.audio_stream = audio_stream
        self.params = Parameters()

        self.row = 5

        self.params_queue = multiprocessing.Queue()
        self.input_audio_queue = multiprocessing.Queue(
            maxsize=NUM_AUDIO_BUFFERS)
        self.output_audio_queue = multiprocessing.Queue(
            maxsize=NUM_AUDIO_BUFFERS)
        self.tension_queue = multiprocessing.Queue(maxsize=2)
        self.violin_process = multiprocessing.Process(
            target=violin_process,
            args=(instrument_type, instrument_number, self.params_queue,
                  self.input_audio_queue,self.output_audio_queue,
                  self.tension_queue)
            )
        self.violin_process.daemon = True

        if self.stdscr is not None:
            self.stdscr.nodelay(1)
            self.print_help()
        #self.stdscr.addstr(20, 50, str("%s" % audio_queue))

    def print_help(self):
        helpstr = [[
            "q: quit",
            "s: string++",
            "a: string--",
            "f: finger++",
            "d: finger--"
        ], [
            "t: pos++",
            "g: pos--",
            "y: force++",
            "h: force--",
        ], [
            "u: velocity++",
            "j: velocity--",
        ], [
            "z,x: tension+",
            "c,v: tension-",
        ]]
        for row, line in enumerate(helpstr):
            for i, text in enumerate(line):
                self.stdscr.addstr(row, 16*i, text)

    def copy_params(self):
        change = Parameters()
        change.violin_string = self.params.violin_string
        change.finger_position = self.params.finger_position
        change.bow_position = self.params.bow_position
        change.force = self.params.force
        change.velocity = self.params.velocity
        change.tension_relative = self.params.tension_relative
        return change

    def turn_off_current_string(self):
        string_off = self.copy_params()
        string_off.force = 0
        string_off.velocity = 0
        self.params_queue.put(string_off)

    def change_tension(self, alter):
        change = self.copy_params()
        change.tension_relative = alter
        self.params_queue.put(change)

    def keypress(self, c):
        if c == 'q':
            return False
        if c == 's':
            self.turn_off_current_string()
            # new
            self.params.violin_string += 1
            if self.params.violin_string > 3:
                self.params.violin_string = 0
        if c == 'a':
            self.turn_off_current_string()
            # new
            self.params.violin_string -= 1
            if self.params.violin_string < 0:
                self.params.violin_string = 3
        if c == 'f':
            if self.params.finger_position == 0.0:
                self.params.finger_position = 0.02
            else:
                self.params.finger_position *= 1.1
        if c == 'd':
            if self.params.finger_position < 0.02:
                self.params.finger_position = 0.00
            else:
                self.params.finger_position /= 1.1
        if c == 't':
            self.params.bow_position *= 1.01
        if c == 'g':
            self.params.bow_position /= 1.01
        if c == 'y':
            self.params.force *= 1.1
        if c == 'h':
            self.params.force /= 1.1
        if c == 'u':
            self.params.velocity *= 1.1
        if c == 'j':
            self.params.velocity /= 1.1

        skip_violin_print = False
        if c == 'z' or c == 'x' or c == 'c' or c == 'v':
            if c == 'z':
                alter = 1.0/1.1
            if c == 'x':
                alter = 1.0/1.01
            if c == 'c':
                alter = 1.01
            if c == 'v':
                alter = 1.1
            self.change_tension(alter)
            skip_violin_print = True
        if c >= '1' and c <= str(vivi_defines.CATEGORIES_NUMBER):
            skip_violin_print = True
            self.snapshot(int(c) - vivi_defines.CATEGORIES_CENTER_OFFSET)
            self.stdscr.addstr(self.row, 0, str("file written"))

        if c == 'l':
            if self.params.force > 0:
                self.store_force = self.params.force
                self.params.force = 0
            else:
                self.params.force = self.store_force

        if c == 'm':
            midi = midi_pos.pos2midi(self.params.finger_position)
            midi = round(midi)
            self.params.finger_position = midi_pos.midi2pos(midi)
            self.stdscr.addstr(23, 20, str("midi: %i" % midi))
        if c == 'b':
            self.dyn += 1
            if self.dyn >= 4:
                self.dyn = 0
            self.params.bow_position = dynamics.get_distance(self.dyn)
            self.params.velocity = dynamics.get_velocity(self.dyn)
            self.stdscr.addstr(23, 20, str("dyn: %i  " % self.dyn))
        if c == 'n':
            midi = midi_pos.pos2midi(self.params.finger_position)
            midi = round(midi) + 1
            if midi > 7:
                midi = 0
            self.params.finger_position = midi_pos.midi2pos(midi)
            self.stdscr.addstr(23, 20, str("midi: %i  " % midi))

        self.params_queue.put(self.params)
        if not skip_violin_print:
            self.stdscr.addstr(self.row, 0, str(
                "%i\t%.3f\t%.3f\t%.3f\t%.3f" % (
                self.params.violin_string, self.params.finger_position,
                self.params.bow_position, self.params.force, self.params.velocity)))
            # next line
            self.row += 1
            if self.row > 20:
                self.row = 5
            self.stdscr.addstr(self.row, 0, str(" "*40))
            self.stdscr.move(self.row, 0)
        return True

    def print_tension(self, tension):
        self.stdscr.addstr(23, 5, str("T=%.3f" % tension))

    def inst_name(self, instrument_type, instrument_number):
        if instrument_type == 0:
            return "violin/violin-%i" % instrument_number
        if instrument_type == 1:
            return "viola/viola-%i" % instrument_number
        if instrument_type == 2:
            return "cello/cello-%i" % instrument_number

    def snapshot(self, cat):
        finger_midi = 12.0*math.log(1.0 /
            (1.0 - self.params.finger_position)) / math.log(2.0)
        filename = TRAIN_DIR+"%s_%i_%.3f_%.3f_%.3f_%.3f_%i.wav" % (
            self.inst_name(self.instrument_type, self.instrument_number),
            self.params.violin_string,
            finger_midi,
            self.params.bow_position,
            self.params.force,
            self.params.velocity,
            1)
        actions_filename = filename.replace(".wav", ".actions")
        forces_filename = filename.replace(".wav", ".forces.wav")
        actions_out = actions_file.ActionsFile(actions_filename)
        actions_out.comment("basic\tst %i\tdyn %i\tfinger_midi %.3f" % (
                    self.params.violin_string, 0,
                    finger_midi))
        actions_out.finger(0, self.params.violin_string,
            self.params.finger_position)
        complete = numpy.empty(0, dtype=numpy.int16)
        complete_forces = numpy.empty(0, dtype=numpy.int16)
        seconds = 0.2
        bow_pos_along = 0.1
        for j in xrange( int(math.ceil(seconds * 44100.0 / HOPSIZE)) ):
            arr_audio, arr_forces = self.output_audio_queue.get()
            complete = numpy.append(complete, arr_audio)
            complete_forces = numpy.append(complete_forces, arr_forces)
            self.input_audio_queue.put( (arr_audio, arr_forces) )

            seconds = j*HOPSIZE/44100.0
            actions_out.bow(seconds, self.params.violin_string,
                self.params.bow_position,
                self.params.force,
                self.params.velocity,
                bow_pos_along
                )
            bow_pos_along += self.params.velocity/44100.0
        # do one more action for "good luck"
        seconds = (j+1)*HOPSIZE/44100.0
        actions_out.bow(seconds, self.params.violin_string,
            self.params.bow_position,
            self.params.force,
            self.params.velocity,
            bow_pos_along
            )

        scipy.io.wavfile.write(filename, 44100, complete)
        #downsample_factor = 8
        #scipy.signal.decimate(complete_forces, downsample_factor)
        #scipy.io.wavfile.write(forces_filename,
        #    int(44100.0/downsample_factor), complete_forces)
        scipy.io.wavfile.write(forces_filename, 44100, complete_forces)
        actions_out.close()

        #mf_filename = "train/%i_%i.mf" % (
        #    self.params.violin_string, self.dyn)
        subdir = filename.split('/')[1]
        mf_filename = "train/" + subdir+"/%i.mf" % (self.params.violin_string)
        mf_file = open(mf_filename, 'a')
        mf_file.write(str("%s\t%03i\n" % (filename,
            cat + vivi_defines.CATEGORY_POSITIVE_OFFSET)) )
        mf_file.close()
        cmd = "python/actions2csv.py %s" % actions_filename
        os.system(cmd)
        self.stdscr.addstr(22, 10, str("wrote to %s" %
                    mf_filename))

    def set_message(self, text):
        self.stdscr.addstr(23, 20, str("%s" % text))

    def main_loop(self):
        windowsize = 2048

        for i in range(NUM_AUDIO_BUFFERS):
            arr = numpy.zeros(HOPSIZE, dtype=numpy.int16)
            forces_arr = numpy.zeros(HOPSIZE, dtype=numpy.int16)
            self.input_audio_queue.put( (arr, forces_arr) )

        self.params_queue.put(self.params)

        pitch_obj = aubio.aubiowrapper.new_aubio_pitchdetection(
            windowsize, HOPSIZE, 1, 44100,
            aubio.aubiowrapper.aubio_pitch_yinfft,
            aubio.aubiowrapper.aubio_pitchm_freq,
            )
        fvec = aubio.aubiowrapper.new_fvec(HOPSIZE, 1)
        show_pitch = 0
        time_unit = 0.5*HOPSIZE/44100.0

        self.violin_process.start()
        # wait for a complete queue before progressing
        while not self.output_audio_queue.full():
            time.sleep(time_unit)

        while True:
            c = self.stdscr.getch()
            if c != -1:
                if not self.keypress( chr(c) ):
                    break
    
            while not self.tension_queue.empty():
                self.print_tension( self.tension_queue.get() )

            if not self.output_audio_queue.empty():
                arr_audio, arr_forces = self.output_audio_queue.get()
                self.audio_stream.write( arr_audio.tostring() )
            else:
                time.sleep(time_unit)

            if PRINT_EXTRA_DISPLAY:
                self.stdscr.addstr(20, 60, str("in %i" %
                    self.input_audio_queue.qsize()))
                self.stdscr.addstr(21, 60, str("out %i" %
                    self.output_audio_queue.qsize()))

                for i in xrange(HOPSIZE):
                    aubio.aubiowrapper.fvec_write_sample(
                       fvec, float(arr_audio[i]), 0, i)

                pitch = aubio.aubiowrapper.aubio_pitchdetection(
                        pitch_obj, fvec)
                show_pitch -= 1
                if show_pitch <= 0:
                    self.stdscr.addstr(23, 50, str("%.1f" % pitch))
                    show_pitch = 20
            self.input_audio_queue.put( (arr_audio, arr_forces) )

    

def main(stdscr):
    try:
        instrument_type = int(sys.argv[1])
    except:
        instrument_type = 0
    try:
        instrument_number = int(sys.argv[2])
    except:
        instrument_number = 0
    try:
        st = int(sys.argv[3])
    except:
        st = 0
    try:
        dyn = int(sys.argv[4])
    except:
        dyn = 0
    try:
        finger = int(sys.argv[5])
    except:
        finger = 0
    try:
        text_message = " ".join(sys.argv[6:])
    except:
        text_message = ""

    p = pyaudio.PyAudio()
    audio_stream = p.open(
        rate = 44100,
        channels = 1,
        format = pyaudio.paInt16,
        output = True,
        frames_per_buffer=HOPSIZE,
    )

    vln = InteractiveViolin(instrument_type, instrument_number, stdscr, audio_stream)
    vln.turn_off_current_string()
    vln.params.violin_string = st
    vln.params.finger_position = midi_pos.midi2pos(finger)
    vln.params.bow_position = dynamics.get_distance(dyn)
    vln.params.velocity = dynamics.get_velocity(dyn)
    vln.params_queue.put(vln.params)

    vln.dyn = dyn

    if stdscr is not None:
        vln.set_message(text_message)
    vln.main_loop()

    audio_stream.close()
    p.terminate()

if __name__ == "__main__":
    curses.wrapper(main)
    #main(None)

