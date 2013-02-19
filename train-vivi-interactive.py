#!/usr/bin/env python

import os
import sys
sys.path.append('python/')
sys.path.append('build/python/')
sys.path.append('build/swig/')
import curses
import time

import dynamics
import vivi_defines
import midi_pos

import artifastring_process
import artifastring_interactive
artifastring_interactive.HOPSIZE = vivi_defines.HOPSIZE

from artifastring_process import COMMANDS

ACTIONS2CSV = True
#ACTIONS2CSV = False


class ViviTrainer(artifastring_interactive.InteractiveViolin):
    def __init__(self, *args):
        artifastring_interactive.InteractiveViolin.__init__(self, *args)
        self.instrument_type = self.artifastring_init.instrument_type
        self.instrument_number = self.artifastring_init.instrument_number

    def actions2csv(self):
        import actions2csv
        actions2csv.main_inst_dir("train-data/", self.instrument_type)

    def keypress_extra(self, c):
        if c == 'b':
            self.dyn += 1
            if self.dyn >= 4:
                self.dyn = 0
            self.params.bow_position = dynamics.get_distance(
                self.instrument_type, self.dyn)
            self.params.velocity = dynamics.get_velocity(
                self.instrument_type, self.dyn)
            self.stdscr.addstr(23, 20, str("dyn: %i  " % self.dyn))

    #def snapshot_post(self, filename):
    #    actions_filename = filename.replace(".wav", ".actions")
        #cmd = "python/actions2csv.py %s" % actions_filename
        #os.system(cmd)


def main(stdscr):
    artifastring_interactive.GAUSSIAN_FORCE = 0.01
    artifastring_interactive.GAUSSIAN_VELOCITY = 0.01

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


    artifastring_init = artifastring_process.ArtifastringInit(
        instrument_type, instrument_number)

    vln = ViviTrainer(artifastring_init, stdscr, "train-data")
    vln.turn_off_current_string()
    vln.params.violin_string = st
    vln.params.finger_position = midi_pos.midi2pos(finger)
    vln.params.bow_position = dynamics.get_distance(instrument_type,dyn)
    vln.params.velocity = dynamics.get_velocity(instrument_type,dyn)
    vln.commands_pipe_master.send( (COMMANDS.BOW, vln.params) )

    vln.dyn = dyn

    if stdscr is not None:
        vln.set_message(text_message)

    time.sleep(0.5)
    vln.main_loop()
    curses.endwin()
    if ACTIONS2CSV:
        vln.actions2csv()

if __name__ == "__main__":
    curses.wrapper(main)
    #main(None)


