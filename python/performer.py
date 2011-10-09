#!/usr/bin/env python

DEBUG_PARAMS = 1

import sys
# TODO: hack for current build system.
sys.path.append('python/')
sys.path.append('build/python/')
sys.path.append('build/swig/')

from PyQt4 import QtCore
import os.path

import vivi_controller
import music_events
import dynamics
import dirs
import utils

import style_simple
import shared

EXTRA_FINAL_REST = 0.5

BOW_TO_PIZZ_FORCE_MULTIPLIER = 1.0

class Performer(QtCore.QObject):
    process_step = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.notation = music_events.MusicEvents()
        self.style = style_simple.StyleSimple()
        self.controller = None
        if not dirs.files:
            dirs.files = dirs.ViviDirs(
                "train/", "/tmp/vivi-cache/", "final/")
        self.current_st = None
        self.arco = False

    def set_instrument(self, instrument_number=0):
        self.controller = vivi_controller.ViviController(instrument_number)

    def _setup_controller(self):
        if not self.controller:
            self.set_instrument()
        for st in range(4):
            for dyn in range(4):
                mpl_filename = dirs.files.get_mpl_filename(st, dyn)
                if not os.path.exists(mpl_filename):
                    mpl_filename = None
                self.controller.load_ears_training(st, dyn,
                    mpl_filename)
                self.controller.set_stable_K(st, dyn,
                    self.style.controller_params[st][dyn].stable_K)
                self.controller.set_dampen(st, dyn,
                    self.style.controller_params[st][dyn].dampen)

    def play(self):
        utils.play(self.audio_filename + ".wav")

    def load_file(self, filename):
        self.notation.load_file(filename)
        self.style.plan_perform(self.notation.events)
        self.audio_filename = filename.replace(".notes", "")

    def load_wav(self, filename):
        self.audio_filename = filename

    def steps(self):
        return len(self.style.notes)

    def play_music(self):
        self._setup_controller()
        self.controller.filesNew(self.audio_filename)

        for note in self.style.notes:
            if self.style.is_note(note):
                self._render_note(note)
            else:
                self._render_rest(note)
            self.process_step.emit()
        self.controller.rest(EXTRA_FINAL_REST)

        self.controller.filesClose()

    def _render_note(self, note):
        if note.pizz:
            if self.arco:
                self.controller.bowStop()
                self.arco = False
            if DEBUG_PARAMS:
                print '---- pizz'
                note.begin.print_params()
                note.end.print_params()
            if note.begin.physical.dynamic < 0:
                print "CRITICAL ERROR: dynamic below 0!"
            note.begin.physical.bow_force *= BOW_TO_PIZZ_FORCE_MULTIPLIER
            self.controller.pizz(note.begin, note.duration)
        else:
            if DEBUG_PARAMS:
                print '---- note'
                note.begin.print_params()
                note.end.print_params()
            self.arco = True
            self.controller.note(note.begin, note.duration,
                note.end,
                note.point_and_click)

    def _render_rest(self, note):
        if DEBUG_PARAMS:
                print '---- rest'
        if self.arco:
            self.controller.bowStop()
            self.arco = False
        self.controller.rest(note.duration)

    def get_duration(self):
        return self.style.last_seconds

