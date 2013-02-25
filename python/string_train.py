#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import string_train_gui

import vivi_defines

import dyn_train

import utils

import collection
import state

import compare_coll
import shared

import judge_audio_widget

import os
import os.path

import instrument_numbers

NUM_DYNS = 6

class StringTrain(QtGui.QFrame):
    def __init__(self, parent, st, inst_type, inst_num,
            files,
            judge_layout, coll):
        QtGui.QWidget.__init__(self)

        ### internal state
        self.st = st
        self.inst_type = inst_type
        self.inst_num = inst_num
        self.coll = coll
        self.files = files
        self.judge_layout = judge_layout
        #print "string_train", self.inst_type, self.inst_num

        ### setup GUI
        self.ui = string_train_gui.Ui_string_train_box()
        self.ui.setupUi(self)
        parent.addWidget(self)

        self.dyns = []
        for di in range(NUM_DYNS):
            dyn = dyn_train.DynTrain(
                self.ui.horizontalLayout, self,
                self.st, di,
                self.inst_type, self.inst_num, self.coll,
                self.files)
            self.dyns.append(dyn)
            pass

        self.ui.accuracy.clicked.connect(self.click_accuracy)

        self.compare = None
        self.judge = None
        self.accuracy = 0.0

        self.modified = {}
        for key in state.STRING_JOBS:
            self.modified[key] = False


        if self.inst_type == 0:
            string_names = ['G', 'D', 'A', 'E']
        else:
            string_names = ['C', 'G', 'D', 'A']

        self.ui.string_label.setText(string_names[self.st])

        self.read()



    def display(self):

        num_trained = self.coll.num_main()
        if num_trained > 0:
            self.ui.num_trained.setText(str(self.coll.num_main()))
        else:
            self.ui.num_trained.setText("")
        if self.accuracy > 0:
            if vivi_defines.REGRESSION:
                # round number
                self.ui.accuracy.setText(
                    str("%.3f")%( self.accuracy ))
            else:
                self.ui.accuracy.setText(
                    str("%.1f%%")%( self.accuracy ))
        else:
            self.ui.accuracy.setText("")

        self.highlight(self.ui.num_trained,
            self.modified[vivi_defines.TASK_TRAINING])
        self.highlight(self.ui.accuracy,
            self.modified[vivi_defines.TASK_ACCURACY])

        for dyn in self.dyns:
            dyn.display()


    def highlight(self, widget, highlight=True):
        # TODO: really bad way of highlighting!
        # but QPushButtons don't seem
        # to have a nice way to highlight!
        if highlight:
            widget.setStyleSheet("background-color: darkBlue; color: white;")
        else:
            widget.setStyleSheet("")

    def read(self):
        try:
            ### read collection
            mf_filename = self.files.get_mf_filename(self.st)
            self.coll.add_mf_file(mf_filename)
            lines = open(self.files.get_string_filename(self.st)).readlines()
            self.accuracy = float(lines[0])
        except:
            self.accuracy = 0.0
        for dyn in self.dyns:
            dyn.read()
        self.display()

    def save(self):
        for di, dyn in enumerate(self.dyns):
            dyn.write()
        if self.inst_num > 0:
            return
        if self.coll.need_save():
            ### write collection
            mf_filename = self.files.get_mf_filename(self.st)
            self.coll.write_mf_file(mf_filename)
        if True:
            ### save accuracy
            string_file = open(self.files.get_string_filename(self.st), "w")
            string_file.write("%.3f" % self.accuracy)
            string_file.close()


    def set_modified_this(self):
        for key in state.STRING_JOBS:
            self.modified[key] = True
        self.coll.set_modified()
        self.display()

    def set_modified(self):
        for di, dyn in enumerate(self.dyns):
            dyn.set_modified()
        self.set_modified_this()

    def is_need_job(self, job_type):
        if self.coll.num_main() == 0:
            return False
        if not self.modified[job_type]:
            return False
        return True

    def make_job(self, job_type):
        job = state.Job(job_type)
        job.inst_type = self.inst_type
        job.inst_num = self.inst_num
        job.st = self.st
        job.files = self.files
        job.mf_filename = self.files.get_mf_filename(self.st)
        job.arff_filename = self.files.get_arff_filename(self.st)
        job.mpl_filename = self.files.get_mpl_filename(self.st)
        if job.job_type == vivi_defines.TASK_TRAINING:
            if not os.path.exists(job.mf_filename):
                return None
        if job.job_type == vivi_defines.TASK_ACCURACY:
            job.coll = self.coll
            job.cats_dir = self.files.get_cats_dir()
            if not os.path.exists(job.arff_filename):
                return None
        return job

    def start_job(self, job_type):
        if job_type in state.DYN_JOBS:
            steps = sum( [dyn.start_job(job_type) for dyn in self.dyns ])
            return steps
        if not self.is_need_job(job_type):
            return 0
        job = self.make_job(job_type)
        if not job:
            return 0
        steps = shared.thread_pool.add_task(job)
        return steps


    def make_judge(self, parent):
        judge = judge_audio_widget.JudgeAudioWidget(parent)
        judge.judged_cat.connect(self.judged_cat)
        judge.display(parent)
        return judge

    def train_zoom(self, wavfile, cancel_will_delete=True):
        self.cancel_will_delete = cancel_will_delete
        self.train_filename = wavfile
        # TODO: clean this up
        self.judge = self.make_judge(self.judge_layout)
        self.judge.user_judge(wavfile)


    def click_accuracy(self, event):
        if self.accuracy == 0:
            return
        if not self.compare:
            self.compare = compare_coll.CompareColl(self.files)
            self.compare.row_delete.connect(self.delete_file)
            self.compare.row_retrain.connect(self.retrain_file)
        self.compare.compare(self.st, self.coll)

    def delete_file(self, filename):
        self.coll.delete(filename+'.wav')
        self.set_modified()
        #if not basic_training.get_next_basic(self.dyn, self.coll):
        #    self.basic_trained = True
        #else:
        #    self.basic_trained = False
        self.display()

    def retrain_file(self, filename):
        # TODO: passing a python string through a signal turns it into a
        # QString.  This changes it back to a python string
        wavfile = str(filename)
#        self.train_zoom(str(filename), cancel_will_delete=False)
        self.cancel_will_delete = False
        self.train_filename = wavfile
        self.judge = self.make_judge(self.compare.ui.verticalLayout)
        self.judge.user_judge(wavfile)

    def judged_cat(self, cat):
        if cat == judge_audio_widget.JUDGEMENT_CANCEL:
            if self.cancel_will_delete:
                os.remove(self.train_filename+".wav")
                os.remove(self.train_filename+".forces.wav")
                os.remove(self.train_filename+".actions")
        else:
            self.train_filename = self.files.move_works_to_train(
                self.train_filename)
            if self.cancel_will_delete:
                self.coll.add_item(self.train_filename+'.wav',
                    cat)
            else:
                self.coll.add_item(self.train_filename+'.wav',
                    cat, replace=True)
                self.compare.compare(self.st, self.coll)
            self.judged_main_num = self.coll.num_main()
            self.set_modified()
#        if self.state.job_type == state.BASIC_TRAINING:
#            if self.coll.is_cat_valid(cat):
#                self.basic_train_next()
#            else:
#                self.basic_train_end()
#        else:
#            self.train_over()
        self.judge.judged_cat.disconnect(self.judged_cat)
        self.judge.display(show=False)
        self.judge = None

    def task_done(self, job):
        self.save()
        if job.job_type in state.STRING_JOBS:
            self.modified[job.job_type] = False
            if job.job_type == vivi_defines.TASK_ACCURACY:
                self.accuracy = job.accuracy
            self.display()
        elif job.job_type in state.DYN_JOBS:
            self.dyns[job.dyn].task_done(job)
        else:
            raise Exception("message should not be here!")


