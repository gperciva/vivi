#!/usr/bin/env python

import math

import task_base
import vivi_defines

import numpy

import scipy.stats
import basic_training

import shared
import vivi_controller
import utils
import dynamics
import vivi_types
import basic_training

import note_actions_cats

import pylab

import collection

DH = vivi_defines.DH
ATTACK_LENGTH = int(1.000/DH)*DH
SHORT_ATTACK_LENGTH = int(0.25/DH)*DH

TOO_SMALL_TO_CARE_CAT = 0.5
#TOO_SMALL_TO_CARE_CAT = 0.0

STEPS_X = 17
STEPS_Y = 9
#STEPS_X = 3
#STEPS_Y = 3
RAPS = 2

class TaskAttack(task_base.TaskBase):

    def __init__(self, controller, emit):
        task_base.TaskBase.__init__(self, controller, emit,
            "attack")
        #self.STEPS = 8
        self.STEPS_X = STEPS_X
        self.STEPS_Y = STEPS_Y
        self.best_attack = 0 # a "null" value
        self.best_stability = 1.0

        self.notes = None
        self.forces = None
        #self.second_pass = True
        #self.third_pass = True

    def set_data(self, inst_type, st, dyn, force_init, K, fmi, files):
        task_base.TaskBase.set_data(self, inst_type, st, dyn, files)
        self.taskname += "-%i" % fmi
        #K = 1.0
        #self.controller.set_stable_K(self.st, self.dyn, int(fmi), K)
        self.fmi = fmi
        self.fm = basic_training.FINGER_MIDIS[fmi]
        #self.attack_forces = force_init[fmi]
        self.force_init = force_init[fmi]
        #print self.force_init
        self.LOW_INIT = self.force_init[0]
        self.HIGH_INIT = self.force_init[1]
        #print self.force_init
        #self.test_range = self._make_forces(self.force_init[self.fmi],
        #    num=STEPS_X)
        #self.test_range = self._make_forces(self.force_init,
        #    num=STEPS_X)
        #print self.test_range
        #self.test_range = self.test_range[2:-2]
        self.LOW_INIT = 8.0
        self.HIGH_INIT = 24.0
        self.test_range = numpy.linspace(
            self.LOW_INIT, self.HIGH_INIT, num=STEPS_X)
        #geom_mid = scipy.stats.gmean( [self.LOW_INIT, self.HIGH_INIT])
        #self.test_range = self._make_forces(
        #    [self.force_init[0],
        #    scipy.stats.gmean( [self.LOW_INIT, self.HIGH_INIT]),
        #    self.force_init[1]],
        #    num=STEPS_X)
        self.test_range1 = list(self.test_range)

        self.K_range = numpy.linspace(0.0, 0.12, num=STEPS_Y)
        self.K_range1 = list(self.K_range)
        #self.K_range = numpy.linspace(1.01, 2.0, num=STEPS_Y)
        #self.K_range = numpy.linspace(1.01, 3.0, num=STEPS_Y)

        # FIXME FIXME
        #self.test_range = numpy.linspace(
        #    6.0, 16.0, num=STEPS_X)
        #self.K_range = numpy.linspace(1.0, 1.5, num=STEPS_Y)
        #self.K_range = numpy.linspace(1.02, 1.10, num=STEPS_Y)
        #print self.test_range
        #for a in self.test_range:
        #    print "%.3f" % a,
        #print
        self.second = False

    @staticmethod
    def steps_full():
        return 1*(STEPS_X * STEPS_Y)
        #return 2*(STEPS_X * STEPS_Y)

    def _make_files(self):
        self._setup_controller()

        if self.second:
            #print "First-phase force:", self.best_attack
            self.test_range = self._make_forces(
                [
                0.5*self.best_attack,
                self.best_attack,
                1.5*self.best_attack,
                ], num=STEPS_X)
            self.test_range2 = list(self.test_range)
            #print "second-phase tests:", self.test_range
            self.K_range = numpy.linspace(
                self.best_stability-0.1,
                self.best_stability+0.1,
                num=STEPS_Y)
            self.K_range2 = list(self.K_range)
            self.taskname = self.taskname.replace("attack", "second-att")

        #print self.test_range
        self.kept_files = []
        def single_file(bow_force, count, K):
            finger_midi = basic_training.FINGER_MIDIS[self.fmi]
            # FIXME: oh god ick
            ap = vivi_types.AudioParams( self.st,
                finger_midi,
                dynamics.get_distance(self.inst_type,
                    self.dyn),
                bow_force,
                dynamics.get_velocity(self.inst_type,
                    self.dyn))
            attack_filename = self.files.make_attack_filename(
                self.taskname+'-%.2f' % K,
                ap, count)
            #print attack_filename

            self.controller.reset()
            self.controller.filesNew(attack_filename)

            self.controller.comment("attack inst %i st %i dyn %i finger_midi %.3f"
                    % (self.inst_type, self.st, self.dyn, finger_midi))

            begin = vivi_controller.NoteBeginning()
            begin.physical.string_number = self.st
            begin.physical.dynamic = self.dyn
            begin.physical.finger_position = utils.midi2pos(finger_midi)
            begin.physical.bow_force = bow_force
            begin.physical.bow_bridge_distance = dynamics.get_distance(
                self.inst_type, self.dyn)
            begin.physical.bow_velocity = dynamics.get_velocity(
                self.inst_type, self.dyn)
            end = vivi_controller.NoteEnding()
            #if finger_midi != 0:
            #    self.process_step.emit()
            #    return
            #print "------"

            for i, bow_direction in enumerate([1, -1]*RAPS):
                self.controller.reset(True)
                #print i, bow_direction
                begin.physical.bow_velocity *= bow_direction
                self.controller.note(begin, ATTACK_LENGTH, end)
                #if i % 4 < 2:
                #    self.controller.note(begin, ATTACK_LENGTH, end)
                #else:
                #    self.controller.note(begin, SHORT_ATTACK_LENGTH, end)
                #if i % 4 == 3:
                #if i % 2 == 1:
                #if True:
                    #print "reset"
                #    self.controller.reset(True)
            self.controller.filesClose()

            self.kept_files.append(attack_filename)
            self.process_step.emit()


        K_main = 0.05
        for bow_force in self.test_range:
            for Ki, K in enumerate(self.K_range):
                #print bow_force, K
                self.controller.set_stable_K(self.st, self.dyn,
                    int(self.fmi), K)
                self.controller.set_stable_K_main(self.st, self.dyn,
                    int(self.fmi), K_main)
                # TODO: start counting at 1 due to "if 0" in training_dir
                #for count in range(1,self.REPS+1):
                single_file(bow_force, count=Ki, K=K)


    def get_attack_files_info(self):
        self._examine_files()

    def _examine_files(self):
        #files = self._get_files()

        #self._setup_lists_from_files(files)

        #self.num_rows = len(self.counts[self.fm])
        #self.num_cols = len(self.forces_initial[self.fm])
        self.num_rows = STEPS_Y
        self.num_cols = STEPS_X

        # hack
        #self.forces = self.forces_initial[self.fm]
        self.forces = self.test_range

        # initialize 2d array
        notes = []

        for i in range(self.num_rows):
            notes.append([])
            for j in range(self.num_cols):
                notes[i].append(None)

        shape = (self.num_rows, self.num_cols)
        costs = numpy.zeros(shape, dtype=numpy.float64)

        forces = [ float(str("%.03f" % f)) for f in self.test_range]
        for filename in self.kept_files:
            params, extra, count = self.files.get_audio_params_extra(filename)
            #print filename, params, extra, count
            finger_midi = params.finger_midi
            if finger_midi != self.fm:
                continue

            #row = self.counts[finger_midi].index(count)
            #col = self.forces_initial[finger_midi].index(params.bow_force)
            row = count
            col = forces.index(params.bow_force)

            nac = note_actions_cats.NoteActionsCats()
            nac.load_file(filename, self.files)
            #to_find = "finger_midi %i" % basic_training.FINGER_MIDIS[self.fm]
            to_find = "finger_midi"
            nac.load_note(to_find, full=True)
            cats = [ b for a,b in nac.get_note_cats() ]
            #att = self.portion_attack(cats_means)
            #att = cats_means # consider entire note
            #cost = self.get_cost(att)
            K = self.K_range[row]
            #cost = (1.0 + K)*get_cost(cats)
            cost = get_cost(cats)
            #print row, col
            notes[row][col] = (nac, cost, filename)
            costs[row][col] = cost

        stable_file = open('orig-%i.txt' % self.fmi, 'w')
        for K_i, K in enumerate(self.K_range):
            for Fbi, Fb in enumerate(self.test_range):
                stable_file.write("%g\t%g\t%g\n" % (
                        K,
                        Fb,
                        costs[K_i][Fbi]))
            stable_file.write("\n")
        stable_file.close()
        #numpy.savetxt("orig.txt", costs)
        newcosts = numpy.zeros( shape )
        for i in range(shape[0]):
            for j in range(shape[1]):
                squares = 0
                if j > 0:
                    squares += 1
                if j < shape[1]-1:
                    squares += 1
                if i > 0:
                    squares += 1
                if i < shape[0] - 1:
                    squares += 1
                left = costs[i][j-1] if j>0 else 0
                right = costs[i][j+1] if j<shape[1]-1 else 0
                top = costs[i-1][j] if i>0 else 0
                bot = costs[i+1][j] if i>shape[0]-1 else 0
                newcosts[i][j] = (costs[i][j]/2.0 +
                    (left+right+top+bot) / squares) / 2.0

        stable_file = open('stable-%i.txt' % self.fmi, 'w')
        for K_i, K in enumerate(self.K_range):
            for Fbi, Fb in enumerate(self.test_range):
                stable_file.write("%g\t%g\t%g\n" % (
                        K,
                        Fb,
                        newcosts[K_i][Fbi]))
            stable_file.write("\n")
        stable_file.close()

        # avoid picking edges
        r = 0
        c = 0
        while True:
        #while r == 0 or c == 0 or r == newcosts.shape[0] or c == newcosts.shape[1]:
            #r, c = numpy.unravel_index(costs.argmin(), shape)
            r, c = numpy.unravel_index(newcosts.argmin(), shape)
            #print r, c, newcosts[r][c]
            if r == 0 or c == 0 or r == newcosts.shape[0]-1 or c == newcosts.shape[1]-1:
                newcosts[r][c] = 99999
            else:
                break

        #print r, c, costs[r][c]
        self.best_attack = self.test_range[c]
        self.best_stability = self.K_range[r]
       # #print best_attack, best_stability

        if self.second:
            self.notes2 = list(notes)
            self.best_attack2 = self.best_attack
            self.best_stability2 = self.best_stability
        else:
            self.notes1 = list(notes)
            self.best_attack1 = self.best_attack
            self.best_stability1 = self.best_stability


        return 0,0
        cands = []
        for col, bow_force in enumerate(self.test_range):
        #for col, bow_force in enumerate(self.forces_initial[self.fm]):
            vals = []
            #for row, count in enumerate(self.counts[self.fm]):
            for row in range(STEPS_Y):
                val = notes[row][col]
                #print val
                #if val[1] > 0:
                #    vals.append(val[1])
            if len(vals) > 0:
                val = scipy.mean(vals)
                std = scipy.std(vals)
                worst = max(vals)
            else:
                val = 0
            cands.append( (val, col, bow_force) )
            #cands.append( (worst, col, bow_force) )
            #cands.append( (val+5*std, col, bow_force) )
            #cands.append( (val**2+std**2, col, bow_force) )
        cands.sort()
        lowest_index = cands[0][1]
        self.best_attack = cands[0][2]
        #if self.fmi != 0:
        #    return lowest_index, self.best_attack
        #print '------'
        #for c in cands:
        #    print c
        #print '------'
        #print self.fmi, lowest_index, self.best_attack
        return lowest_index, self.best_attack


    def portion_attack(self, values):
        newvalues = []
        min_length = 18 # 200ms
        past_values = scipy.zeros(min_length)
        pvi = 0
        M = 0.5
        filled = 0
        for val in values:
            if val == vivi_defines.CATEGORY_NULL:
                continue
            newvalues.append(val)
            past_values[pvi] = val
            pvi += 1
            if pvi >= min_length:
                pvi = 0
                filled = 1
            if filled:
                mse = self.mse(past_values)
                if M > mse:
                    break
        return newvalues

def split_cats(cats):
    notes = []
    for i in range(RAPS):
        notes.append([])
        notes.append([])
    notes_i = -1
    prev = None
    for i, cat in enumerate(cats):
        if cat is None: 
            continue
        if cat == vivi_defines.CATEGORY_WAIT:
            continue
        if cat == vivi_defines.CATEGORY_NULL:
            prev = None
            continue
        if prev is None:
            notes_i += 1
        prev = cat
        notes[notes_i].append(cat)
    return notes

def get_cost(values):
    if len(values) == 0:
        return 0
    examines = split_cats(values)
    #examine = filter(lambda x: x != vivi_defines.CATEGORY_NULL, values)
    #examine = filter(lambda x: x != vivi_defines.CATEGORY_WAIT, examine)
    #print examine
    #for i in range(4):
    #    examines[i] = numpy.array([
    #        c if abs(c) > TOO_SMALL_TO_CARE_CAT else 0
    #        for c in examines[i]])
    #for i in range(vivi_defines.ATTACK_HARSH_HOPS):
    #    examine[i] -= 0.5
        #if 0 < examine[i] < 1.0:
        #    examine[i] = 0
    #print examine
    #total = sum(map(lambda x: x*x, examine))
    total = 0.0
    count = 0
    for i in range(RAPS):
        for j in range(len(examines[i])):
            c = examines[i][j]
            #total += j * (c**2)
            #total += (float(j)**0.5) * (c**2)
            #total += (c**2)
            total += abs(c)
            count += 1
    total /= float(count)
    return total


#if __name__ == "__main__":

