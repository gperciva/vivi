#!/usr/bin/env python

#PLOT = True
PLOT = False

import math

import task_base

import scipy.stats
import dirs
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

import numpy
import pylab
import matplotlib.cm

import midi_pos

# 50 ms = 8.6 hops
# 52.2 ms = 9 hops
# 100 ms = 17.2 hops
DAMPEN_NOTE_SECONDS = 0.5
#DAMPEN_WAIT_SECONDS = 0.25
DAMPEN_WAIT_SECONDS = 0.5 # HACK

HOPS_DAMPEN = 8
HOPS_SETTLE = int( DAMPEN_NOTE_SECONDS * 44100.0/256.0) - HOPS_DAMPEN
HOPS_WAIT   = int( DAMPEN_WAIT_SECONDS * 44100.0/256.0) + HOPS_DAMPEN - 1


class TaskDampen(task_base.TaskBase):

    def __init__(self, st, dyn, controller, emit):
        task_base.TaskBase.__init__(self, st, dyn, controller, emit,
            "dampen")
        #self.STEPS = 6
        #self.REPS = 4
        self.STEPS = 6
        self.REPS = 1

        self.notes = None
        self.initial_force = None

        self.hops = HOPS_SETTLE + HOPS_DAMPEN + HOPS_WAIT

    def steps_full(self):
        return 2*(self.STEPS * self.REPS)

    def set_K(self, K):
        self.controller.set_stable_K(self.st, self.dyn, K)

    def set_initial_force(self, force):
        self.initial_force = force

    def _make_files(self):
        self._setup_controller()

        for damp in self.test_range:
            self.controller.set_dampen(self.st, self.dyn, damp)
            for count in range(1, self.REPS+1):

                begin = vivi_controller.NoteBeginning()
                begin.physical.string_number = self.st
                begin.physical.dynamic = self.dyn
                begin.physical.finger_position = 0.0
                begin.physical.bow_force = self.initial_force
                begin.physical.bow_bridge_distance = dynamics.get_distance(self.dyn)
                begin.physical.bow_velocity = dynamics.get_velocity(self.dyn)

                filename = dirs.files.make_dampen_filename(
                    self.taskname, 
                    vivi_types.AudioParams(self.st,
                        midi_pos.pos2midi(begin.physical.finger_position),
                        dynamics.get_distance(self.dyn),
                        begin.physical.bow_force,
                        dynamics.get_velocity(self.dyn)),
                    damp, count)
                end = vivi_controller.NoteEnding()
                end.lighten_bow_force = True
                end.keep_bow_velocity = True
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
            params, extra, count = dirs.files.get_audio_params_extra(filename)
            row = self.counts[0].index(count)
            col = self.extras[0].index(extra)

            nac = note_actions_cats.NoteActionsCats()
            nac.load_file(filename[0:-4])
            nac.load_note("note", full=True)
            self.notes[row][col] = (nac, 0, filename)


    def _examine_files(self):
        self.get_file_info()

        rmss = vivi_controller.doubleArray(self.hops)
        candidates = []
        for col, dampen in enumerate(self.extras[0]):
            costs = []
            for row, count in enumerate(self.counts[0]):
                filename = self.notes[row][col][2]
                ears = self.controller.getEars(self.st, self.dyn)
                ears.get_rms_from_file(self.hops,
                    filename, rmss)
                cost = self.get_dampen_cost(rmss, dampen, count)
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
        rmss_arr = numpy.empty(self.hops)
        for i in range(self.hops):
            rmss_arr[i] = rmss[i]
        if PLOT:
            color = dampen
            if count == 1:
                pylab.semilogy(rmss_arr,
                    color=matplotlib.cm.jet(dampen),
                    label=str("%.1f"%dampen))
            else:
                pylab.semilogy(rmss_arr,
                    color=matplotlib.cm.jet(dampen))
            pylab.legend()
#        print HOPS_SETTLE, HOPS_DAMPEN, HOPS_WAIT, self.hops

        total = 0.0
        total_damp = 0.0
        total_wait = 0.0
        prev = rmss[HOPS_SETTLE-1]
        #print '----'
        for i in range(HOPS_SETTLE - HOPS_DAMPEN, HOPS_SETTLE):
        #    print i
            value = rmss[i]
            total_damp += value
        for i in range(HOPS_SETTLE, HOPS_SETTLE + HOPS_WAIT/2):
        #    print i
            value = rmss[i]
            total_wait += value
        total = total_damp + total_wait
        total /= HOPS_DAMPEN + HOPS_WAIT/2
        return total

