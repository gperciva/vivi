#!/usr/bin/env python
""" Owned by MainWindow, owner of violin strings."""

from PyQt4 import QtGui, QtCore
import string_instrument_gui

import string_train
import dirs

import instrument_numbers

import collection

NUM_STRINGS = 4

class StringInstrument(QtGui.QFrame):
    """ Class which distributes messages amongst the violin strings."""

    def __init__(self, parent, inst_main_num, instrument_name,
            training_dirname, cache_dirname, final_dirname,
            judge_layout, colls):
        QtGui.QFrame.__init__(self)

        self.inst_main_num = inst_main_num
        self.inst_type = instrument_numbers.DISTINCT_INSTRUMENT_NUMBERS[inst_main_num]
        if self.inst_type == 0:
            self.inst_num = self.inst_main_num - 0
        elif self.inst_type == 1:
            self.inst_num = self.inst_main_num - 5
        elif self.inst_type == 2:
            self.inst_num = self.inst_main_num - 7
        else:
            print "can't find inst num!"
        #print "string_instrument", self.inst_main_num, self.inst_type, self.inst_num


        self.instrument_name = instrument_name
        maininstname = instrument_name.split(" ")[0]
        self.files = dirs.ViviDirs(
            training_dirname, cache_dirname, final_dirname,
            maininstname)

        ### setup GUI
        self.ui = string_instrument_gui.Ui_string_instrument_gui()
        self.ui.setupUi(self)
        parent.addWidget(self)

        ### setup strings
        self.string_trains = []
        for st in range(NUM_STRINGS):
            if colls is None:
                coll = collection.Collection()
            else:
                coll = colls[st]
            st_train = string_train.StringTrain(self.layout(), st,
                self.inst_type, self.inst_num,
                self.files, judge_layout, coll)
            self.string_trains.append(st_train)


    def get_colls(self):
        colls = []
        for st in range(NUM_STRINGS):
            colls.append(self.string_trains[st].coll)
        return colls

    ### save/modify
    def save(self):
        for st in range(NUM_STRINGS):
            self.string_trains[st].save()

    def set_modified(self, portion=0):
        if portion == 1:
            for st in range(0,2):
                self.string_trains[st].set_modified()
        elif portion == 2:
            for st in range(2,4):
                self.string_trains[st].set_modified()
        else:
            for st in range(NUM_STRINGS):
                self.string_trains[st].set_modified()

    ### job handling
    def start_job(self, job_type):
        steps = sum( [self.string_trains[st].start_job(
                job_type) for st in range(NUM_STRINGS) ])
        return steps

    def task_done(self, job):
        self.string_trains[job.st].task_done(job)

    ### basic training
    def get_basic_train_level(self):
        basic_min_level = self.string_trains[0].min_level()
        for st in range(1, NUM_STRINGS):
            level = self.string_trains[st].min_level()
            if basic_min_level > level:
                basic_min_level = level
        if basic_min_level == string_train.NUM_DYNS:
            return -1
        return basic_min_level

    ### interactive training
    def train_zoom(self, st, dyn, wavfile):
        self.string_trains[st].train_zoom(wavfile)


