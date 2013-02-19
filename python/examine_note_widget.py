#!/usr/bin/python

from PyQt4 import QtGui, QtCore

import utils
import shared

import os.path
import note_actions_cats

import plot_actions
import plot_main
import plot_stable
import plot_attack

import math
import instrument_numbers

PLOT_ACTIONS = 1
PLOT_MAIN = 2
PLOT_STABLE = 3
PLOT_ATTACK = 4

# TODO: make this instrument-specific?
CONVOLUTION_DELAY = 0.02322 # seconds (approximate value)

class ExamineNoteWidget():
    #def __init__(self, parent):
    def __init__(self, plot_type=PLOT_ACTIONS):
        #self.note_layout = note_layout
        #self.note_label = self.note_layout.itemAt(0).widget()
        self.plot_type = plot_type
        if plot_type == PLOT_MAIN:
            #self.plot_actions = plot_main.PlotMain()
            self.plot_actions = plot_actions.PlotActions()
        elif plot_type == PLOT_STABLE:
            self.plot_actions = plot_stable.PlotStable()
        elif plot_type == PLOT_ATTACK:
            self.plot_actions = plot_attack.PlotAttack()
        else:
            self.plot_actions = plot_actions.PlotActions()
        #parent.layout().addWidget(self.plot_actions, 1)
        #self.note_layout.addWidget(self.plot_actions, 1)

        self.examine_note = None
        self.got_zoom = False

    def reset(self):
        self.plot_actions.reset()

    def set_examine_note(self, nac):
        if self.plot_type == PLOT_STABLE:
            self.examine_note = nac[0]
            self.plot_actions.set_data(
                self.examine_note.note_forces,
                self.examine_note.note_cats,
                self.examine_note,
            )
            self.plot_actions.set_stability(nac[1],
                self.examine_note.note_cats_means)
        if self.plot_type == PLOT_ATTACK:
            self.examine_note = nac[0]
            self.plot_actions.set_data(
                self.examine_note.note_forces,
                self.examine_note.note_cats,
                self.examine_note,
            )
            self.plot_actions.set_stability(nac[1],
                self.examine_note.note_cats_means)
        # FIXME: oh god ick, how is this so bad?
        if self.plot_type == PLOT_ACTIONS:
            self.examine_note = nac[0]
            self.plot_actions.set_data(
                self.examine_note.note_forces,
                self.examine_note.note_cats,
                self.examine_note,
            )
            #self.plot_actions.set_stability(nac[1],
            #    self.examine_note.note_cats_means)

    def new_examine_note(self):
        self.examine_note = note_actions_cats.NoteActionsCats()

    def load_file(self, filename, files):
        print "Examine file:\t", os.path.basename(filename)
        self.files = files
        self.filename = filename
        self.examine_note.load_file(filename, files)

    def load_note(self, text, full=False):
        status = self.examine_note.load_note(text, full)
        if status:
            self.plot_actions.set_data(
                self.examine_note.note_forces,
                self.examine_note.note_cats,
                self.examine_note,
                )
#        else:
#            print "Not a rehearsed note!"
        return status


    def play(self):
        if not self.examine_note.basename:
            return
        if self.plot_actions.has_selection():
            start, dur = self.get_zoom_seconds()
            #print "play zoom in on: ", start, dur
            #utils.play(self.examine_note.wavfile,
            #    start, dur)
            #return
        else:
            start = self.examine_note.note_start
            dur = self.examine_note.note_length
            # to avoid icky blimps in the big grid display
            start += CONVOLUTION_DELAY
            dur -= CONVOLUTION_DELAY
            #print "play note: ", start, dur
        utils.play(self.examine_note.basename+'.wav',
            start, dur)

    def get_zoom_seconds(self):
        if self.plot_actions.has_selection():
            start, dur = self.plot_actions.get_selection()
            self.got_zoom = True
            return self.examine_note.get_seconds(start, dur)
        else:
            return self.examine_note.get_seconds(0, 1)

    def get_zoom(self):
        start, dur = self.get_zoom_seconds()
        st = self.examine_note.note_st
        dyn = int(round(self.examine_note.note_dyn))
        a, b, c = instrument_numbers.instrument_name_from_filename(self.filename)
        dist_inst_num = b
        filename = self.examine_note.make_zoom_file(start, dur, self.files)
        return st, dyn, filename, dist_inst_num

    def get_zoom_bare(self):
        start, dur = self.get_zoom_seconds()
        filename = self.examine_note.make_zoom_file(start, dur)
        return filename

