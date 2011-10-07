#!/usr/bin/env python
""" Owned by MainWindow, owner of violin strings."""

from PyQt4 import QtGui, QtCore
import string_train_all_gui

import state
import string_train

NUM_STRINGS = 4

class StringTrainAll(QtGui.QFrame):
    """ Class which distributes messages amongst the violin strings."""
    process_step = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtGui.QFrame.__init__(self)

        ### setup GUI
        self.ui = string_train_all_gui.Ui_string_train_all_gui()
        self.ui.setupUi(self)
        parent.addWidget(self)

        ### setup strings
        self.string_trains = []
        for st in range(NUM_STRINGS):
            st_train = string_train.StringTrain(self.layout(), st)
            st_train.process_step.connect(self.process_step_emit)
            self.string_trains.append(st_train)

        ### setup state
        self.state = state.State()
        self.state.next_step.connect(self.next_step)
        self.state.finished_step.connect(self.finished_step)

    ### save/modify
    def save(self):
        for st in range(NUM_STRINGS):
            self.string_trains[st].save()

    def set_modified(self):
        for st in range(NUM_STRINGS):
            self.string_trains[st].set_modified()

    ### bulk processing state
    def process_step_emit(self):
        self.process_step.emit()
        self.state.step()

    def next_step(self, job_type, job_index):
        self.string_trains[job_index].start()

    def finished_step(self, job_type, job_index):
        pass



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

    def basic_train(self):
        basic_min_level = self.get_basic_train_level()
        if basic_min_level < 0:
            return
        jobs = []
        for st in range(NUM_STRINGS):
            jobs.append(self.string_trains[st].basic_train_prep(basic_min_level))
        self.state.prep(state.BASIC_TRAINING, jobs)
        self.state.start()

    ### train SVMs
    def compute_training(self):
        jobs = []
        for st in range(NUM_STRINGS):
            jobs.append(self.string_trains[st].compute_training_steps())
        self.state.prep(state.SVM, jobs, parallel=True)
        self.state.start()
        return sum(jobs)

    def check_accuracy(self):
        jobs = []
        for st in range(NUM_STRINGS):
            jobs.append(self.string_trains[st].check_accuracy_steps())
        self.state.prep(state.SVM, jobs, parallel=True)
        self.state.start()
        return sum(jobs)

    def verify(self):
        jobs = []
        for st in range(NUM_STRINGS):
            jobs.append(self.string_trains[st].check_verify_steps())
        self.state.prep(state.VERIFY, jobs, parallel=True)
        self.state.start()
        return sum(jobs)

    def learn_stable(self):
        jobs = []
        for st in range(NUM_STRINGS):
            jobs.append(self.string_trains[st].learn_stable_steps())
        self.state.prep(state.STABLE, jobs, parallel=True)
        self.state.start()
        return sum(jobs)

    def learn_dampen(self):
        jobs = []
        for st in range(NUM_STRINGS):
            jobs.append(self.string_trains[st].learn_dampen_steps())
        self.state.prep(state.DAMPEN, jobs, parallel=True)
        self.state.start()
        return sum(jobs)

    def learn_attacks(self):
        jobs = []
        for st in range(NUM_STRINGS):
            jobs.append(self.string_trains[st].learn_attacks_steps())
        self.state.prep(state.ATTACKS, jobs, parallel=True)
        self.state.start()
        return sum(jobs)


#        for level in range(len(levels.level_params)):
#            for st in STRINGS:
#                if not self.string_trains[st].has_level(level):
#                    self.basic_level = level
#                    self.basic_training_string = st
#                    #print "FOUND TRAINING:",
#                    #print level, st
#                    self.basic_train_next()
#                    return
#
#    def basic_train_next(self):
#        #print "START BASIC TRAIN NEXT",
#        #print self.basic_training_string, self.basic_level
#        while self.string_trains[self.basic_training_string].has_level(self.basic_level):
#        #    print "in while",
#        #    print self.basic_training_string, self.basic_level
#            self.basic_training_string += 1
#            if self.basic_training_string > (NUM_STRINGS-1):
#                # stop training
#                self.basic_training_string = -1
#                self.select(-1, -1)
#                return
##            else:
##                self.string_trains[self.basic_training_string].train.levels.set_level(self.next_basic_level)
#        #print "after while",
#        #print self.basic_training_string, self.basic_level
#        if self.basic_training_string >= 0:
#            #print self.basic_training_string, self.basic_level
#            train_list = self.string_trains[self.basic_training_string].get_train_level(self.basic_level)
#            self.string_trains_note(train_list, self.basic_level)
#
#
#    def train_note(self, train_list, level):
#        #print train_list
#        self.string_trains_list = train_list
#        # ick, but necessary for force-based train note
#        self.basic_level = level
#        self.string_trains_next()
#
#
#
#
#
#
################## old stuffs
#
#    def select(self, num, level):
#        for st in STRINGS:
#            if st == num:
#                self.string_trains[st].select( level )
#            else:
#                self.string_trains[st].select( -1 )
#
#    def retrain(self, st, dyn, wavfile):
#        self.string_trainsing = self.string_trains[st].dyns[dyn]
#        self.string_trainsing.train_reinit(wavfile)
#        self.string_trains_prompt()
#
#    def train_end(self):
#        self.string_trains_list_index = -1
#        self.string_trains_list = []
#        self.note_label.setText('')
#        self.display()
#
#    def train_next(self):
#        self.string_trains_list_index += 1
#        if self.string_trains_list_index >= len(self.string_trains_list):
#            self.string_trains_end()
#            if self.basic_training_string >= 0:
#                self.basic_train_next()
#            return
#        params = self.string_trains_list[self.string_trains_list_index]
#        st = params.st
#        self.select(st, self.basic_level)
#        self.string_trainsing = self.string_trains[st].get_dyn_level(self.basic_level)
#        self.string_trainsing.train_init( params )
#        self.string_trains_prompt()
#
#    def train_prompt(self):
#        #text = self.string_trainsing.get_cat_message()
#        #self.note_label.setText(text)
#        #utils.play(self.string_trainsing.train_filename)
#        pass
#
#    def display(self):
#        for st in STRINGS:
#            self.string_trains[st].display()
#
#    def opinion(self, key):    
#        if not self.string_trainsing:
#            return
#        opinion = self.string_trainsing.opinion(key)
#        if opinion == string_train.dyn_train.OPINION_END:
#            self.display()
#            self.string_trains_next()
#        elif opinion == string_train.dyn_train.OPINION_QUIT:
#            self.string_trains_end()
#        elif opinion == string_train.dyn_train.OPINION_CONTINUE:
#            self.string_trains_prompt()
#
#
#    def hasBasicTraining(self):
#        for st in STRINGS:
#            if not self.string_trains[st].has_level(0):
#                return False
#        return True
#

    def train_zoom(self, st, dyn, wavfile):
        self.string_trains[st].train_zoom(dyn, wavfile)
#        self.string_trainsing = self.string_trains[st].get_dyn_level(level)
#        self.string_trainsing.train_reinit(wavfile)
#        self.string_trains_prompt()

#    def learn_stable(self):
#        self.state = CALCULATING_STABLE
#        self.done_steps = 0
#        self.total_steps = 0
#        for st in STRINGS:
#            self.total_steps += self.string_trains[st].learn_stable()
#        return self.total_steps
#
#    def delete_file(self, st, dyn, wavfile):
#        self.string_trains[st].dyns[dyn].delete_file(wavfile)
#

    # keep this separate, for compare_coll
#    def set_note_label(self, note_label):
#        self.note_label = note_label



