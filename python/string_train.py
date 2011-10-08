#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import string_train_gui

import dyn_train

#import ears
import vivi_controller
import utils

import state

#import performer
#import violin_practice

import shared


NUM_DYNS = 4

STATE_NULL = 0
STATE_BASIC_TRAINING = 1
STATE_SVM = 2

CALCULATE_TRAINING = 1
CHECK_ACCURACY = 2
LEARN_ATTACKS = 3
LEARN_STABLE = 4


class StringTrain(QtGui.QFrame):
    process_step = QtCore.pyqtSignal()

    def __init__(self, parent, st):
        QtGui.QWidget.__init__(self)
        self.st = st

        ### setup GUI
        self.ui = string_train_gui.Ui_string_train_box()
        self.ui.setupUi(self)
        parent.addWidget(self)
        if self.st == 0:
            text = 'G'
        elif self.st == 1:
            text = 'D'
        elif self.st == 2:
            text = 'A'
        elif self.st == 3:
            text = 'E'
        self.ui.string_label.setText(text)

        ### setup per-string control loop for training
        self.controller = vivi_controller.ViviController(shared.instrument_number)

        self.dyns = []
        for di in range(NUM_DYNS):
            dyn = dyn_train.DynTrain(
                self.ui.horizontalLayout,
                self.st, di, self.controller, None)
            dyn.process_step.connect(self.process_step_emit)
            self.dyns.append(dyn)

        self.dyn_steps = [0]*NUM_DYNS
        self.dyn_working_index = -1

        self.state = state.State()
        self.state.next_step.connect(self.next_step)
        self.state.finished_step.connect(self.finished_step)

    def save(self):
        for di in range(NUM_DYNS):
            self.dyns[di].write()

    ### bulk processing state
    def process_step_emit(self):
        self.process_step.emit()
        self.state.step()

    def start(self):
        self.state.start()

    def next_step(self, job_type, job_index):
        self.dyns[job_index].start()

    def finished_step(self, job_type, job_index):
        pass

    def set_modified(self):
        for st in range(NUM_STRINGS):
            self.train[st].set_modified()
#
#    def next_step(self):
#        print self.st, "next step ", self.dyn_steps
#        for di in range(NUM_DYNS):
#            if self.dyn_steps[di] > 0:
#                self.do_next_step(di)
#                self.dyn_steps[di] -= 1
#                return
#
#    def decide_next_step(self):
#        print self.st, "decide next step ", self.dyn_steps
#        if self.dyn_steps[self.dyn_working_index] > 0:
#            # continue working
#            self.dyn_steps[self.dyn_working_index] -= 1
#            return
#        else:
#            for di in range(NUM_DYNS):
#                if self.dyn_steps[di] > 0:
#                    self.do_next_step(di)
#                    self.dyn_steps[di] -= 1
#                    return
#        return
#
#        self.dyn_steps[self.dyn_steps_index] = 0
#
#        while (self.dyn_steps[self.dyn_steps_index] == 0):
#            self.dyn_steps_index += 1
#            if self.dyn_steps_index >= 4:
#                self.dyn_steps_index = -1
#                self.dyn_steps = [0]*4
#                self.state = 0
#            #    print "false"
#                return False
#        if self.dyn_steps[self.dyn_steps_index] > 0:
#            #print "true"
#            return True
#
    ### basic training
    def min_level(self):
        for li in range(NUM_DYNS):
            di = utils.level_to_dyn(li)
            if not self.dyns[di].has_basic_training():
                return li
        return NUM_DYNS

    def basic_train_prep(self, level):
        jobs = [0]*NUM_DYNS
        dyn = utils.level_to_dyn(level)
        jobs[dyn] = 1
        self.state.prep(state.BASIC_TRAINING, jobs)
        return self.dyns[dyn].basic_prep()

#    def has_level(self, level):
#        for di in range(4):
#            if self.dyns[di].level == level:
#                return self.dyns[di].has_basic_level()
#        return False
#
#    def get_train_level(self, level):
#        for di in range(4):
#            if self.dyns[di].level == level:
#                return self.dyns[di].get_train_level()
#    def get_dyn_level(self, level):
#        for di in range(4):
#            if self.dyns[di].level == level:
#                return self.dyns[di]
#
#
    def set_modified(self):
        for di in range(NUM_DYNS):
            if self.dyns[di].judged_main_num > 0:
                self.dyns[di].set_modified()
#
#
#    def basic_train_next(self, level):
#        return self.dyns[level].basic_train_next()
#
    def compute_training_steps(self):
        jobs = []
        for st in range(NUM_DYNS):
            jobs.append(self.dyns[st].compute_training_steps())
        self.state.prep(state.SVM, jobs)
        return sum(jobs)

    def check_accuracy_steps(self):
        jobs = []
        for st in range(NUM_DYNS):
            jobs.append(self.dyns[st].check_accuracy_steps())
        self.state.prep(state.ACCURACY, jobs)
        return sum(jobs)

    def check_verify_steps(self):
        jobs = []
        for st in range(NUM_DYNS):
            jobs.append(self.dyns[st].check_verify_steps())
        self.state.prep(state.VERIFY, jobs)
        return sum(jobs)

    def learn_stable_steps(self):
        jobs = []
        for st in range(NUM_DYNS):
            jobs.append(self.dyns[st].learn_stable_steps())
        self.state.prep(state.STABLE, jobs)
        return sum(jobs)

    def learn_dampen_steps(self):
        jobs = []
        for st in range(NUM_DYNS):
            jobs.append(self.dyns[st].learn_dampen_steps())
        self.state.prep(state.DAMPEN, jobs)
        return sum(jobs)

    def learn_attacks_steps(self):
        jobs = []
        for st in range(NUM_DYNS):
            jobs.append(self.dyns[st].learn_attacks_steps())
        self.state.prep(state.ATTACKS, jobs)
        return sum(jobs)



    def train_zoom(self, dyn, wavfile):
        self.dyns[dyn].train_zoom(wavfile)

#    def learn_stable(self):
#        self.state = LEARN_STABLE
#        for di in DYNS:
#            self.dyn_steps[di] = self.dyns[di].learn_stable_steps()
#        self.dyn_steps_index = 0
#        if self.dyn_steps[self.dyn_steps_index] > 0:
#            self.dyns[self.dyn_steps_index].learn_stable()
#        else:
#            if self.find_next_step():
#                self.dyns[self.dyn_steps_index].learn_stable()
#        return sum(self.dyn_steps)
#
#
#    #def process_step_emit(self):
#    #    self.process_step.emit()
#
#
#
#
################## old stuffs
#
#    def old_constructor(self):
#        self.st = st
#
#        self.setup_gui()
#
#        self.dyns = []
#        self.make_cat_type_widget('f')
#        self.make_cat_type_widget('mf')
#        self.make_cat_type_widget('mp')
#        self.make_cat_type_widget('p')
#
#        self.train = string_train.StringTrain(self.st)
#        self.train.process_step.connect(self.process_step_emit)
#
#        self.display()
#
#            
#
#    def make_cat_type_widget(self, text):
#        cat_type_widget = QtGui.QFrame()
#        cat_type_widget.ui = string_train_gui.Ui_train_cat_frame()
#        cat_type_widget.ui.setupUi(cat_type_widget)
#        cat_type_widget.ui.dyn_type.setText(text)
#        cat_type_widget.setAutoFillBackground(True)
#        self.ui.horizontalLayout.addWidget(cat_type_widget)
#        # weird subclassing event thingy
#        cat_type_widget.mousePressEvent = self.click
#        self.dyns.append(cat_type_widget)
#
#    def click(self, event):
#        parent = self.parent().parent().string_train
#        self.check_coll = check_coll_widget.CheckCollWidget(
#            parent)
#        #self.check_coll.accepted.connect(self.save_training)
#        self.check_coll.check(self.st, False, self.train.coll)
#
#    def display(self):
#        for di in range(4):
#            self.dyns[di].display()
#        return
##        if self.train.modified_out:
##            self.cat_out.setBackgroundRole(
##                    QtGui.QPalette.Highlight)
##        else:
##            self.cat_out.setBackgroundRole(
##                QtGui.QPalette.Window)
##        if self.train.modified_in:
##            self.cat_in.setBackgroundRole(
##                    QtGui.QPalette.Highlight)
##        else:
##            self.cat_in.setBackgroundRole(
##                QtGui.QPalette.Window)
#
#        if self.train.judged_out_num > 0:
#            #text = str(self.train.judged_out_num)+ ' trained'
#            text = str(self.train.judged_main_num)+ ' trained'
#            self.cat_out.ui.num_trained_label.setText(text)
#        else:
#            self.cat_out.ui.num_trained_label.setText("")
#        if self.train.judged_in_num > 0:
#            text = str(self.train.judged_in_num)+ ' trained'
#            self.cat_in.ui.num_trained_label.setText("")
#            #self.cat_in.ui.num_trained_label.setText(text)
#        else:
#            self.cat_in.ui.num_trained_label.setText("")
#
#        if self.train.accuracy_out >= 0:
#            text = '%.1f%%\t' % self.train.accuracy_out
#            self.cat_out.ui.accuracy_label.setText(text)
#        else:
#            self.cat_out.ui.accuracy_label.setText("")
#
#        if self.train.accuracy_in >= 0:
#            text = '%.1f%%' % self.train.accuracy_in
#            self.cat_in.ui.accuracy_label.setText(text)
#        else:
#            self.cat_in.ui.accuracy_label.setText("")
#
#        #self.set_force(self.ui.force_f, 0)
#        #self.set_force(self.ui.force_mf, 2)
#        #self.set_force(self.ui.force_mp, 3)
#        #self.set_force(self.ui.force_p, 1)
#        #self.ui.label_f.setEnabled(self.train.levels.hasLevel(0))
#        #self.ui.label_mf.setEnabled(self.train.levels.hasLevel(2))
#        #self.ui.label_mp.setEnabled(self.train.levels.hasLevel(3))
#        #self.ui.label_p.setEnabled(self.train.levels.hasLevel(1))
#
#    def set_force(self, label, dynamic_index):
#        force = self.train.force_init[dynamic_index]
#        if force > 0:
#            label.setText( str("%.1f" % force) )
#        else:
#            label.setText("")
#
##    def mousePressEvent(self, event):
##        print "click", self.st
#

#    def select(self, level):
#        if level >= 0:
#            self.ui.string_label.setBackgroundRole(
#                    QtGui.QPalette.AlternateBase)
##                    QtGui.QPalette.Highlight)
#            for di in range(4):
#                if self.dyns[di].level == level:
#                    self.dyns[di].select(True)
#                else:
#                    self.dyns[di].select(False)
#        else:
#            self.ui.string_label.setBackgroundRole(
#                    QtGui.QPalette.Window)
#            for di in range(4):
#                self.dyns[di].select(False)
#

