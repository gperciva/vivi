#!/usr/bin/env python

#PLOT = True
PLOT = False

#import numpy
#import pylab
#import matplotlib

import math

import task_base

import scipy.stats
import basic_training

import shared
import vivi_controller
import utils
import dynamics
import vivi_types
import basic_training

import note_actions_cats

import glob
import os.path

#import numpy
#import pylab
#import matplotlib.cm

import midi_pos

# 50 ms = 8.6 hops
# 52.2 ms = 9 hops
# 100 ms = 17.2 hops
DH = 512 / 22050.0
DAMPEN_NOTE_HOPS = int(1.0 / DH)
DAMPEN_NOTE_SECONDS = int( DAMPEN_NOTE_HOPS ) * DH
DAMPEN_WAIT_SECONDS = DAMPEN_NOTE_SECONDS
DAMPEN_NOTE_SAMPLES = 512 * DAMPEN_NOTE_HOPS

HOPS_DAMPEN = 2
HOPS_SETTLE = DAMPEN_NOTE_HOPS - HOPS_DAMPEN
HOPS_WAIT   = DAMPEN_NOTE_HOPS

STEPS = 9
REPS = 1

class TaskDampen(task_base.TaskBase):

    def __init__(self, controller, emit):
        task_base.TaskBase.__init__(self, controller, emit,
            "dampen")
        #self.STEPS = 6
        #self.REPS = 4
        self.STEPS = STEPS
        self.REPS = REPS
        #self.second_pass = True

        self.notes = None
        self.initial_force = None

        self.hops = HOPS_SETTLE + HOPS_DAMPEN + HOPS_WAIT

    @staticmethod
    def steps_full():
        return 1*(STEPS * REPS)
        #return 2*(STEPS * REPS)

    def set_K(self, K):
        self.controller.set_stable_K(self.st, self.dyn, 0, K)

    def set_data(self, inst_type, st, dyn, finger_forces, K, force_init,
            keep_bow, files):
        task_base.TaskBase.set_data(self, inst_type, st, dyn, files)
        self.taskname += "-%i" % keep_bow
        self.controller.set_stable_K(self.st, self.dyn, 0, K)
        self.initial_force = force_init
        self.keep_bow_velocity = keep_bow
        self._init_range()

    def _make_files(self):
        self._setup_controller()
        #print self.test_range
        #print self.keep_bow_velocity

        for damp in self.test_range:
            self.controller.set_dampen(self.st, self.dyn, damp)
            for count in range(1, self.REPS+1):

                begin = vivi_controller.NoteBeginning()
                begin.physical.string_number = self.st
                begin.physical.dynamic = self.dyn
                begin.physical.finger_position = 0.0
                begin.physical.bow_force = self.initial_force

                begin.physical.bow_bridge_distance = dynamics.get_distance(
                    self.inst_type, self.dyn)
                begin.physical.bow_velocity = dynamics.get_velocity(
                    self.inst_type, self.dyn)

                filename = self.files.make_dampen_filename(
                    self.taskname, 
                    vivi_types.AudioParams(self.st,
                        midi_pos.pos2midi(begin.physical.finger_position),
                        dynamics.get_distance(
                            self.inst_type, self.dyn),
                        begin.physical.bow_force,
                        dynamics.get_velocity(
                            self.inst_type, self.dyn)),
                    damp, count)
                end = vivi_controller.NoteEnding()
                end.lighten_bow_force = True
                end.keep_bow_velocity = self.keep_bow_velocity
                self.controller.filesNew(filename)
                self.controller.note(begin, DAMPEN_NOTE_SECONDS, end)
                self.controller.rest(DAMPEN_WAIT_SECONDS)
                self.controller.filesClose()
                self.process_step.emit()
        return

    def get_file_info(self):
        files = self._get_files()

        self._setup_lists_from_files(files)

        self.num_rows = len(self.counts[0])
        self.num_cols = len(self.extras[0])

        self.notes = []
        for i in range(self.num_rows):
            self.notes.append([])
            for j in range(self.num_cols):
                self.notes[i].append(None)

        for filename in files:
            params, extra, count = self.files.get_audio_params_extra(filename)
            row = self.counts[0].index(count)
            col = self.extras[0].index(extra)

            nac = note_actions_cats.NoteActionsCats()
            nac.load_file(filename[0:-4], self.files)
            nac.load_note("note", full=True)
            self.notes[row][col] = (nac, 0, filename)


    def _examine_files(self):
        self.get_file_info()

        import scipy.io.wavfile

        rmss = vivi_controller.doubleArray(self.hops)
        candidates = []
        for col, dampen in enumerate(self.extras[0]):
            costs = []
            for row, count in enumerate(self.counts[0]):
                filename = self.notes[row][col][2]
                #print filename
                sr, timedomain = scipy.io.wavfile.read(filename)
                examine = timedomain[DAMPEN_NOTE_SAMPLES:]
                cost = math.sqrt( sum(examine**2) / float(len(examine)) )

                #ears = self.controller.getEars(self.st)
                #ears.get_rms_from_file(self.hops,
                #    filename, rmss)
                #cost = self.get_dampen_cost(rmss, dampen, count)
                #cost = 0.0

                self.notes[row][col] = (self.notes[row][col][0], cost, filename)
                costs.append(cost)
            cost = scipy.stats.gmean(costs)
            #print dampen, '\t', "%.3f"%cost, '\t\t',
            #for x in costs:
            #    print "%.3f" % x,
            #print
            #print ["%.3f" % x for x in costs]
            candidates.append( 
                (cost, dampen, col) )
        if PLOT:
            pylab.show()
        candidates.sort()
        #print '---------'
        #for c in candidates:
        #    print c
        answer = candidates[0][1]
        index = candidates[0][2]

        return index, answer

    def get_dampen_files_info(self):
        self._examine_files()

    def get_dampen_cost(self, rmss, dampen, count):
        if PLOT:
            rmss_arr = numpy.empty(self.hops)
            for i in range(self.hops):
                rmss_arr[i] = rmss[i]
            color = dampen
            if count == 1:
                pylab.semilogy(rmss_arr,
                    color=matplotlib.cm.jet(dampen),
                    label=str("%.1f"%dampen))
            else:
                pylab.semilogy(rmss_arr,
                    color=matplotlib.cm.jet(dampen))
            pylab.legend()
        #print HOPS_SETTLE, HOPS_DAMPEN, HOPS_WAIT, self.hops

        total = 0.0
        total_damp = 0.0
        total_wait = 0.0
        prev = rmss[HOPS_SETTLE-1]
        #print '----'

        ### ending of the main note
        for i in range(HOPS_SETTLE - HOPS_DAMPEN, HOPS_SETTLE):
        #    print i
            value = rmss[i]
            total_damp += value

        ### waiting time
        for i in range(HOPS_SETTLE, HOPS_SETTLE + HOPS_WAIT):
        #    print i
            value = rmss[i]
            total_wait += value
        #total = total_damp + total_wait
        total = total_wait
        #total /= HOPS_DAMPEN + HOPS_WAIT
        total /= HOPS_WAIT
        total = math.sqrt(total)
        return total

