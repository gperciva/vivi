#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import dyn_train_gui

import collection
import vivi_defines

import numpy
import math
import scipy
import scipy.stats

import basic_training

import os # to delete audio files whose judgement was cancelled

#import levels
import utils
import vivi_types

import instrument_numbers

# TODO: **must** import ears first, then controller.  No clue why.
#import ears

# TODO: **must** import this first, then controller.  No clue why.
import vivi_controller
import dynamics
import controller_params
#import vivi_controller

#import utils
import shared

import state

#import ears

import examine_auto_widget
import compare_coll


# just for BASIC_PARAMS; iffy; icky
#import performer
#BASIC_PARAMS = performer.BasicParams(force_std=0.01, velocity_std=0.01,
#    duration_settle=1.0, duration_play=0.5)
BASIC_SECONDS = 0.3
BASIC_SKIP = 0.5

FINGERS = [0, 1, 6]

class DynTrain(QtGui.QFrame):
    process_step = QtCore.pyqtSignal()

    def __init__(self, parent_gui, parent, st, dyn,
            inst_type, inst_num, coll, files):
        QtGui.QFrame.__init__(self)
        self.parent = parent
        self.st = st
        self.dyn = dyn
        self.inst_type = inst_type
        self.inst_num = inst_num
        self.files = files

        ### setup GUI
        self.ui = dyn_train_gui.Ui_dyn_train_box()
        self.ui.setupUi(self)
        parent_gui.addWidget(self)

        #self.mousePressEvent = self.click
        self.ui.modify.clicked.connect(self.click_modified)
        #self.ui.force_factor.clicked.connect(self.click_force_factor)

        #self.force_buttons = QtGui.QButtonGroup(self)
        self.force_buttons = []
        self.force_factor_buttons = []
        for i in range(len(FINGERS)):
            force_button = QtGui.QPushButton(self)
            force_button.setObjectName("force-%i" % i)
            force_button.setMaximumSize(QtCore.QSize(40, 16777215))
            force_button.setAutoFillBackground(True)
            #force_button.setFlat(True)
            self.ui.verticalLayout.insertWidget(
                self.ui.verticalLayout.count()-2,force_button)
            #self.force_buttons.addButton(force_button, i)
            self.force_buttons.append(force_button)

            force_button.clicked.connect(self.click_force)


        for i in range(len(FINGERS)):
            force_factor_button = QtGui.QPushButton(self)
            force_factor_button.setObjectName("force_factor-%i" % i)
            force_factor_button.setMaximumSize(QtCore.QSize(40, 16777215))
            force_factor_button.setAutoFillBackground(True)
            #force_factor_button.setFlat(True)
            self.ui.verticalLayout.insertWidget(
                self.ui.verticalLayout.count()-2,force_factor_button)
            #self.force_factor_buttons.addButton(force_factor_button, i)
            self.force_factor_buttons.append(force_factor_button)

            force_factor_button.clicked.connect(self.click_force_factor)
        #self.force_factor_buttons.buttonClicked.connect(self.click_force_factor)

        self.ui.dampen_normal.clicked.connect(self.click_dampen)
        #self.ui.dampen_slur.clicked.connect(self.click_dampen)
        self.ui.verify.clicked.connect(self.click_verify)

        self.ui.dyn_type.clicked.connect(self.click_dyn_type)

        self.level = utils.dyn_to_level(self.dyn)

        self.modified = {}
        for key in state.DYN_JOBS:
            self.modified[key] = False

        self.verify_good = None

        self.coll = coll
        ### setup variables
        self.judged_main_num = self.coll.num_main()

        self.basic_trained = False

        #self.force_init = [0 for fm in basic_training.FINGER_MIDIS ]
        self.force_init = [0 for fm in FINGERS ]
        self.mid_forces = [ [0,0] for fm in FINGERS ]
        self.force_factor = [1.0,1.0,1.0]

        self.controller_params = controller_params.ControllerParams(
            self.files.get_dyn_vivi_filename(self.st, self.dyn,
                self.inst_num))
        #print "dyn_train", self.inst_type, self.inst_num

        self.dampen_normal = False
        #self.dampen_slur = False
        #self.read()


        self.examine = examine_auto_widget.ExamineAutoWidget(self)
        self.examine.select_note.connect(self.examine_auto_select_note)

        #self.task_verify = [None for fm in basic_training.FINGER_MIDIS ]
        self.task_verify = [None for fm in FINGERS ]
        self.task_stable = None
        #self.task_attacks = [None for fm in basic_training.FINGER_MIDIS ]
        self.task_attacks = [None for fm in FINGERS ]
        self.task_dampen = None

        self.display()



    def select(self, enable):
        if enable:
            self.ui.dyn_type.setBackgroundRole(
                    QtGui.QPalette.Highlight)
                    #QtGui.QPalette.AlternateBase)
        else:
            self.ui.dyn_type.setBackgroundRole(
                    QtGui.QPalette.Window)

    def highlight(self, widget, highlight=True):
        # TODO: really bad way of highlighting!
        # but QPushButtons don't seem
        # to have a nice way to highlight!
        if highlight:
            widget.setStyleSheet("background-color: darkBlue; color: white;")
        else:
            widget.setStyleSheet("")

    def display(self):
        if not self.coll.num_main():
            self.setEnabled(False)
            self.ui.dyn_type.setText(utils.dyn_to_text(self.dyn))
            #self.ui.num_trained_label.setText("")
            for i in range(len(basic_training.FINGER_MIDIS)):
                #self.force_buttons.button(i).setText("")
                self.force_buttons[i].setText("")
                self.force_factor_buttons[i].setText("")
            self.ui.dampen_normal.setText("")
            #self.ui.dampen_slur.setText("")
            self.ui.verify.setText("")
            return
        # do we need any basic training?
        #print "trying basic,", self.st, self.dyn
        if not basic_training.get_next_basic(
                self.inst_type,
                self.dyn, self.coll,
                self.files):
            self.ui.dyn_type.setStyleSheet(
                "")
            self.ui.dyn_type.setText(utils.dyn_to_text(self.dyn))
        else:
            self.ui.dyn_type.setStyleSheet(
                "color: red;")
            self.ui.dyn_type.setText(utils.dyn_to_text(self.dyn))

        self.setEnabled(True)

        for i in range(len(FINGERS)):
            if self.force_init[i] > 0:
                if round(self.force_init[i],2) < 1.0:
                    self.force_buttons[i].setText(("%.2f N"
                        % self.force_init[i])[1:])
                else:
                    self.force_buttons[i].setText("%.1f N"
                        % self.force_init[i])
                #self.force_buttons.button(i).setText("%.1f N"
                #    % self.force_init[i])
            else:
                #self.force_buttons.button(i).setText("")
                self.force_buttons[i].setText("")
            if self.force_factor_buttons[i] > 1.0:
                self.force_factor_buttons[i].setText(
                    str("%.2f")%self.force_factor[i])
            else:
                self.force_factor_buttons[i].setText("")
        if self.dampen_normal < 1.0:
            self.ui.dampen_normal.setText(
                str("%.2f")%self.dampen_normal)
        else:
            self.ui.dampen_normal.setText("")
        #if self.dampen_slur < 1.0:
        #    self.ui.dampen_slur.setText(
        #        str("%.2f")%self.dampen_slur)
        #else:
        #    self.ui.dampen_slur.setText("")

        if self.verify_good is None:
            self.ui.verify.setText("")
        elif self.verify_good:
            self.ui.verify.setStyleSheet(
                "")
            self.ui.verify.setText("Y")
        else:
            self.ui.verify.setStyleSheet(
                "color: red;")
            self.ui.verify.setText("N")

        #if self.modified[vivi_defines.TASK_STABLE]:
        #    self.ui.force_factor.setStyleSheet(
        #        "background-color: darkBlue; color: white;")
        #else:
        #    self.force_factor_buttons.setStyleSheet("")


        for i in range(len(basic_training.FINGER_MIDIS)):
            self.highlight(self.force_buttons[i],
                self.modified[vivi_defines.TASK_ATTACK])
            self.highlight(self.force_factor_buttons[i],
                self.modified[vivi_defines.TASK_ATTACK])
            #self.highlight(self.force_buttons.button(i),
            #    self.modified_attack)
        self.highlight(self.ui.dampen_normal, self.modified[vivi_defines.TASK_DAMPEN])
        #self.highlight(self.ui.dampen_slur, self.modified[vivi_defines.TASK_DAMPEN])
        self.highlight(self.ui.verify, self.modified[vivi_defines.TASK_VERIFY])
        if self.verify_good is False:
           self.ui.verify.setStyleSheet(
               "background-color: red; color: black;")

    def click_modified(self):
        # will call this set_modified as well
        self.parent.set_modified_this()
        self.set_modified()

    def set_modified(self):
        for key in state.DYN_JOBS:
            self.modified[key] = True
        self.display()

    def need_job(self, job_type):
        if self.coll.num_main() == 0:
            return False
        if not self.modified[job_type]:
            return False
        return True

    def make_filename(self, prefix, extra=""):
        return 'out-dyn/%s-t%i-i%i-s%i-d%i-e%i.txt' % ( prefix,
            self.inst_type, self.inst_num, self.st, self.dyn, extra)

    def make_job(self, job_type, fmi=None, fm=None):
        #print "new job:", self.st, self.dyn, job_type
        job = state.Job(job_type)
        job.inst_type = self.inst_type
        job.inst_num = self.inst_num
        job.st = self.st
        job.dyn = self.dyn
        job.files = self.files
        job.fmi = fmi
        job.fm = fm

        extreme = self.get_extreme_forces()
        #print "Extreme forces: ", extreme[0]
        #print "mid forces: ", self.mid_forces[0]
        #forces = [ self.files.get_audio_params(x[0]).bow_force
        #    for x in self.coll.coll]
        if job_type == vivi_defines.TASK_VERIFY:
            #job.finger_forces = map(lambda x: [min(x), max(x)], extreme)
            job.finger_forces = extreme
            #job.finger_forces = [item for sublist in extreme for item in sublist]
        elif job_type == vivi_defines.TASK_STABLE:
            job.force_init = self.extreme
            #print "INIT:", job.force_init
            #job.force_init = self.force_init
            #job.finger_forces = map(lambda x: [x[2], x[3], x[4]], extreme)
        elif job_type == vivi_defines.TASK_ATTACK:
            att = []
            for j in range(3):
                #a = [ self.mid_forces[i][0], extreme[i][2] ]
                i = job.fmi
                a = [ 1.0*self.mid_forces[i][0],
                      1.0*self.mid_forces[i][1]
                    ]
                if i == j:
                    out = open(self.make_filename("mid_forces", i), 'a')
                    out.write("%i\t%.4f\t%.4f\n" % (i,
                        self.mid_forces[i][0],
                        self.mid_forces[i][1]))
                    out.close()
                #print a
                #a = [ self.mid_forces[i][0],
                #    numpy.mean( [self.mid_forces[i][1], extreme[i][2]]) ]
                #a = numpy.linspace( self.mid_forces[i][0],
                #    self.mid_forces[i][1], num=7) [2:5]
                #a = extreme
                #print a
                att.append(a)
            job.force_init = att
        else:
            job.force_init = self.force_init

        job.mpl_filename = self.files.get_mpl_filename(self.st)
        # extra info
        if job_type == vivi_defines.TASK_ATTACK:
            job.K = self.force_factor
        if job_type == vivi_defines.TASK_DAMPEN:
            job.K = self.force_factor[0]
            job.force_init = self.force_init[0]
        return job

    def start_job(self, job_type):
        #if not self.need_job(job_type) and job_type != vivi_defines.TASK_VERIFY:
        if not self.need_job(job_type):
            return 0
        #print "start", self.st, self.dyn, job_type
        if job_type == vivi_defines.TASK_VERIFY:
            steps = 0
            job = self.make_job(job_type)
            steps += shared.thread_pool.add_task(job)
        elif job_type == vivi_defines.TASK_ATTACK:
            steps = 0
            ### FIXME: only open string
            #for fmi, fm in enumerate(basic_training.FINGER_MIDIS):
            for fmi, fm in enumerate([0]):
                job = self.make_job(job_type, fmi, fm)
                #print "job fm", fm, job.force_init
                steps += shared.thread_pool.add_task(job)
        elif job_type == vivi_defines.TASK_DAMPEN:
            steps = 0
            #for keep_bow in [False, True]:
            for keep_bow in [False]:
                job = self.make_job(job_type)
                job.keep_bow_velocity = keep_bow
                steps += shared.thread_pool.add_task(job)
        else:
            job = self.make_job(job_type)
            steps = shared.thread_pool.add_task(job)
        return steps



    def read(self):
        ### read forces
        self.controller_params.load_file()
        self.force_init = []
        self.mid_forces = []
        self.force_factor = [1.0,1.0,1.0]
        for i in range(len(FINGERS)):
            self.force_init.append(
                self.controller_params.get_attack_force(i))
            mids = [
                self.controller_params.get_mid_force_low(i),
                self.controller_params.get_mid_force_high(i)]
            #print mids
            self.mid_forces.append(mids)
            self.force_factor[i] = self.controller_params.get_stable_K(i)
        self.dampen_normal = self.controller_params.dampen_normal
        #self.dampen_slur = self.controller_params.dampen_slur
        self.display()

    def write(self):
        ### write forces
        for i in range(len(FINGERS)):
            self.controller_params.set_force(i, self.force_init[i])
            self.controller_params.set_mid_force_low(i, self.mid_forces[i][0])
            self.controller_params.set_mid_force_high(i, self.mid_forces[i][1])
            self.controller_params.set_stable_K(i, self.force_factor[i])
        self.controller_params.dampen_normal = self.dampen_normal
        #self.controller_params.dampen_slur = self.dampen_slur
        self.controller_params.write_file()


    def get_all_cat_forces(self, low_include, high_include, fm):
        forces = []
        for x in range(low_include, high_include+1):
            forces.extend( self.get_forces_finger(x, fm) )
        return forces

    def get_extreme_forces(self):
        finger_forces = []
        for fmi, fm in enumerate(basic_training.FINGER_MIDIS):
            cands = numpy.array(map(
                lambda(x): self.files.get_audio_params(x[0]).bow_force,
                (
                  self.coll.get_items_cat_finger(  0, fm)
                )))
            median = scipy.median(cands)
            cands = numpy.array(map(
                lambda(x): self.files.get_audio_params(x[0]).bow_force,
                (
                  self.coll.get_items_cat_finger( -2, fm)
                + self.coll.get_items_cat_finger( -1, fm)
                + self.coll.get_items_cat_finger(  0, fm)
                + self.coll.get_items_cat_finger(  1, fm)
                + self.coll.get_items_cat_finger(  2, fm)
                )))
            #print cands.min()
            #print median
            #print cands.max()
            forces = [cands.min(), median, cands.max()]
            finger_forces.append( forces )
            continue
            # middle
            middle_forces = self.get_forces_finger(0,fm)
            middle_force = scipy.mean(middle_forces)
            # low
            low_forces = self.coll.get_items_cat_finger_bp(
                -vivi_defines.CATEGORIES_EXTREME, fm,
                dynamics.get_distance(self.inst_type,
                    self.dyn))
            low_forces = map(
                lambda(x): self.files.get_audio_params(x[0]).bow_force,
                low_forces)
            really_low = min(low_forces)
            #forces = self.get_all_cat_forces(
            #    -vivi_defines.CATEGORIES_EXTREME,-1,0)
            #low_force = scipy.stats.gmean( forces + [min(middle_forces)])
            #print low_forces
            low_force = scipy.mean( low_forces + [min(middle_forces)])
            # high
            forces = self.get_forces(vivi_defines.CATEGORIES_EXTREME)
            really_high = max(forces)
            forces = self.get_all_cat_forces(
                1, vivi_defines.CATEGORIES_EXTREME,0)
            high_force = scipy.mean( forces + [min(middle_forces)])
            # all
            mid_low = scipy.mean( [low_force, middle_force] )
            mid_high = scipy.mean( [high_force, middle_force] )
            forces = [really_low, low_force, mid_low,
                middle_force, mid_high, high_force, really_high] 
            #print low_force, middle_force, high_force
            finger_forces.append( forces )
        #print finger_forces
        return finger_forces


    def get_forces_finger(self, cat, finger_midi):
        forces = map(
            lambda(x): self.files.get_audio_params(x[0]).bow_force,
            filter(lambda(y):
                self.files.get_audio_params(y[0]).finger_midi == finger_midi,
                self.coll.get_items_cat(cat)))
        return forces

    def get_forces(self, cat):
        forces = map(
            lambda(x): self.files.get_audio_params(x[0]).bow_force,
                self.coll.get_items_cat(cat))
        return forces


    def examine_auto_select_note(self):
        note_filename_text = self.examine.get_selected_filename()
        if note_filename_text:
            shared.examine_main.load_file(note_filename_text[0], self.files)
            if self.examine.mode == "second-att":
                shared.examine_main.load_note(note_filename_text[1], full=True)
            elif self.examine.mode == "verify":
                shared.examine_main.load_note(note_filename_text[1], full=True)
            elif self.examine.mode == "attack":
                shared.examine_main.load_note(note_filename_text[1], full=True)
            else:
                shared.examine_main.load_note(note_filename_text[1])



    def click_force_factor(self, event):
        force_index = int(self.sender().objectName()[13])
        #print "clicked second attack %i" % force_index
        #if self.task_attacks[force_index]:
        if self.task_attacks:
            self.examine.examine("second-att", self.st, self.dyn,
                self.task_attacks[force_index], force_index)

    def click_force(self, event):
        force_index = int(self.sender().objectName()[6])
        #print "clicked attack %i" % force_index
        #if self.task_attacks[force_index]:
        if self.task_attacks:
            self.examine.examine("attack", self.st, self.dyn,
                self.task_attacks[force_index], force_index)

    def click_dampen(self):
        #if self.sender().objectName() == "dampen_slur":
        #    if self.task_dampen_slur:
        #        self.examine.examine("dampen", self.st, self.dyn,
        #            self.task_dampen_slur)
        #else:
        if self.task_dampen_normal:
            self.examine.examine("dampen", self.st, self.dyn,
                self.task_dampen_normal)

    def click_verify(self):
        #task.set_data(self.st, self.dyn, self.get_extreme_forces())
        # yes this is right for now
        if self.task_verify:
            self.examine.examine("verify", self.st, self.dyn,
                self.task_verify)
        #force_index = int(self.sender().objectName()[6])
        #print "clicked verify"
        #force_index = 0
        #if self.task_verify:
        #    self.examine.examine("attack", self.st, self.dyn,
        #        #self.task_verify[force_index], force_index)
        #        self.task_verify, force_index)

    def task_done(self, job):
        if job.job_type in state.DYN_JOBS:
            self.modified[job.job_type] = False
            if job.job_type == vivi_defines.TASK_VERIFY:
                self.verify_good = job.task.verify_good
                self.mid_forces = job.task.mids
                #self.task_verify = job.task
                #self.task_attack = job.task # oh god ick
                self.modified_verify = False
                # initial estimates
                #print FINGERS.index(job.fm)
                #self.force_init[FINGERS.index(job.fm)] = job.force_init
                #self.task_attacks[FINGERS.index(job.fm)] = job.task
                #self.force_init[0] = job.force_init
                self.task_verify = job.task
            elif job.job_type == vivi_defines.TASK_STABLE:
                self.force_factor = job.most_stable
                self.task_stable = job.task
                self.modified_stable = False
            elif job.job_type == vivi_defines.TASK_ATTACK:
                #self.force_init[job.fmi] = job.force_init
                #self.task_attacks[job.fmi] = job.task
                self.force_init[job.fmi] = job.task.best_attack
                self.force_factor[job.fmi] = job.task.best_stability
                self.task_attacks[job.fmi] = job.task

                out = open(self.make_filename("forces", job.fmi), 'a')
                out.write("%i\t%.4f\t%.4f\n" % (job.fmi,
                    job.task.best_attack,
                    job.task.best_stability))
                out.close()

                self.modified_attack = False
            elif job.job_type == vivi_defines.TASK_DAMPEN:
                #if job.keep_bow_velocity:
                #    self.task_dampen_slur = job.task
                #    self.dampen_slur = job.dampen
                #else:
                if True:
                    self.task_dampen_normal = job.task
                    self.dampen_normal = job.dampen
                self.modified_dampen = False
            self.display()
        else:
            raise Exception("message should not be here!")


    def click_dyn_type(self, event):
        needs_basic = basic_training.get_next_basic(
            self.inst_type,
            self.dyn, self.coll,
            self.files)
        if needs_basic:
            (cat, finger) = needs_basic
            print "need ", cat, finger
            text = "Needs category %i" % (
                cat + vivi_defines.CATEGORIES_CENTER_OFFSET )
        else:
            finger = 0
            text = ""
        cmd = "python train-vivi-interactive.py %i %i %i %i %i %s" % (
            self.inst_type,
            self.inst_num, self.st, self.dyn,
            round(finger), text)
        os.system(cmd)
        self.parent.read() # TODO: clean up
        self.set_modified()


