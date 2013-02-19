#!/usr/bin/env python

DEBUG_PARAMS = 0

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

class Performer(QtCore.QObject):
    process_step = QtCore.pyqtSignal()

    def __init__(self, inst_type, inst_num, files):
        QtCore.QObject.__init__(self)
        self.files = files
        self.notation = music_events.MusicEvents()
        self.style = style_simple.StyleSimple(inst_type, inst_num, self.files)
        self.controller = None

    def load_file(self, filename):
        self.notation.load_file(filename)
        self.style.plan_perform(self.notation.events)
        self.audio_filename = filename.replace(".notes", "")

    def get_duration(self):
        return self.style.last_seconds

