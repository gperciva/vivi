#!/usr/bin/env python

# TODO: minimal changes from task_stable; more work needed here

import math
import scipy.stats

import task_base
import vivi_defines

import dirs
import note_actions_cats
import dynamics
import vivi_controller

import utils
import vivi_types
import basic_training

import collection

STABLE_LENGTH = 1.0

IGNORE_INITIAL_PERCENT = 0.25

class TaskVerify(task_base.TaskBase):

    def __init__(self, st, dyn, controller, emit):
        task_base.TaskBase.__init__(self, st, dyn, controller, emit,
            "verify")
        self.STEPS = 2
        self.REPS = 1
        self.LOW_INIT = 1.0
        self.HIGH_INIT = 1.01

        self.second_pass = False
        self.notes = None

    def set_forces(self, forces):
        self.stable_forces = forces

    def steps_full(self):
        return 1 * (self.STEPS * self.REPS)

    def _make_files(self):
        self._setup_controller()

        for K in self.test_range:
            self.controller.set_stable_K(self.st, self.dyn, K)
            for count in range(self.REPS):
                # TODO: this loop could be done in a separate C++ file
                for force_relative_index in range(3):
                    for fmi, finger_midi in enumerate(basic_training.FINGER_MIDIS):
                        bow_force = self.stable_forces[fmi][force_relative_index]
                        audio_params = vivi_types.AudioParams(
                                self.st, finger_midi,
                                dynamics.get_distance(self.dyn),
                                bow_force,
                                dynamics.get_velocity(self.dyn))
                        verify_filename = dirs.files.make_verify_filename(
                            audio_params,
                            K, count+1)
                        self.controller.filesNew(verify_filename)
                        self.controller.comment(
                            "verify st %i dyn %i finger_midi %.3f"
                            % (self.st, self.dyn, finger_midi))
                        begin = vivi_controller.NoteBeginning()
                        vivi_types.audio_params_to_physical(
                            audio_params, self.dyn, begin.physical)
                        end = vivi_controller.NoteEnding()
                        end.keep_bow_velocity = True
                        #for bow_direction in [1, -1]:
                        #    begin.physical.bow_velocity *= bow_direction
                        #    self.controller.note(begin, STABLE_LENGTH, end)
                        self.controller.note(begin, STABLE_LENGTH, end)
                    self.controller.filesClose()
                self.process_step.emit()

    def get_stable_files_info(self):
        files = self._get_files()

        self._setup_lists_from_files(files)

        # ASSUME: no screw-ups in the file creation
        self.num_rows = len(self.counts[0]) * len(self.extras[0])
        self.num_cols = len(self.forces_initial[0])*len(self.finger_midis)
        self.num_counts = len(self.counts[0])

        # initialize 2d array
        self.notes = []
        for i in range(self.num_rows):
            self.notes.append([])
            for j in range(self.num_cols):
                self.notes[i].append(None)
        for filename in files:
            params, extra, count = dirs.files.get_audio_params_extra(filename)
            finger_midi = params.finger_midi
            force = params.bow_force

            # and setup self.examines
            row = (self.num_counts*self.extras[finger_midi].index(extra)
                    + self.counts[finger_midi].index(count))
            col = (len(self.finger_midis) * 
                    self.forces_initial[finger_midi].index(force)
                    + self.finger_midis.index(finger_midi)
                    )
            nac = note_actions_cats.NoteActionsCats()
            nac.load_file(filename[0:-4])
            #to_find = "finger_midi %i" % fm
            to_find = "finger_midi"
            nac.load_note(to_find)
            examine_cats = nac.note_cats_means[int(
                len(nac.note_cats_means) * IGNORE_INITIAL_PERCENT) :]
            stability = self.get_stability(examine_cats)
            self.notes[row][col] = (nac, stability)

    def _examine_files(self):
        self.get_stable_files_info()

        end = []
        middle = []
        num_rows = len(self.notes)
        # find "most stable" rows
        candidates = []
        for block in range(num_rows/self.num_counts):
            block_vals = []
            for count in range(self.num_counts):
                vals = []
                for col_block in range(self.num_cols / len(self.finger_midis)):
                    cvs = []
                    for col_i in range(len(self.finger_midis)):
                        row = self.num_counts*block + count
                        col = len(self.finger_midis)*col_block+col_i
#                        cv = self.examines[row][col].plot_actions.stability
                        cv = self.notes[row][col][1]
                        if cv > 0:
                            cvs.append(cv)
                    #print cvs
                    vals.append( scipy.stats.gmean(cvs) )
                # only take the constant-force examples
                if block == 0:
                    end.append(vals[0])
                    end.append(vals[2])
                middle.append(vals[1])
                row_stable = scipy.stats.gmean(vals)
                block_vals.append(row_stable)
            #print "%.2f\t%.3f" % (self.extras[block], scipy.stats.gmean(block_vals)),
            #print
            #print "\t%.3f" % (scipy.std(block_vals))
            candidates.append( 
                (scipy.stats.gmean(block_vals), self.extras[0][block], block) )
        #print candidates
        candidates.sort()
        most_stable = candidates[0][1]
        index = candidates[0][2]
        # these should be stable
        for m in middle:
            if m > 1.0:
                #print "a middle is:", m
                return None, False
        # these should be unstable
        for e in end:
            if e < 1.0:
                #print "an end is:", e
                return None, False
        return None, True
        #return index, most_stable

    def get_stability(self,cats):
        direction = 1
        areas = []
        area = []
        for cat in cats:
            if cat == vivi_defines.CATEGORY_NULL:
                continue
            if abs(cat) < 0.5:
                continue
            if cat * direction > 0:
                area.append(cat*cat)
            else:
                if area:
                    areas.append(area)
                area = []
                area.append(cat*cat)
                direction = math.copysign(1, cat)
        if area:
            areas.append(area)
        stable = 1.0
        scale_factor = 1.0 / float(len(cats))
        for a in areas:
            area_fitness = sum(a) * sum(a) / len(a)
            #area_fitness = sum(a) / math.sqrt(len(a))
            #area_fitness = 1.0 / math.sqrt(len(a))
            #area_fitness = len(a) * sum(a) / all_bad
            #area_fitness = len(a)
            stable *= area_fitness
        stable *= scale_factor
        return stable
