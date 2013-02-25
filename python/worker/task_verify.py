#!/usr/bin/env python

# TODO: minimal changes from task_stable; more work needed here

import math
import scipy.stats
import numpy
import random

import task_base
import vivi_defines

import note_actions_cats
import dynamics
import vivi_controller

import utils
import vivi_types
import basic_training

import collection
import agm_sequence

HOP = 22050/float(512)

STABLE_LENGTH = 1.0
ATTACK_LENGTH = int(0.1*HOP)/HOP

LOW_MEAN_ACCEPTED = -0.25
HIGH_MEAN_ACCEPTED = 0.5

STEPS = 9
REPS = 1
#STEPS = 3
#REPS = 1

FINGERS = [0, 1, 6]


class TaskVerify(task_base.TaskBase):

    def __init__(self, controller, process_step):
        task_base.TaskBase.__init__(self, controller, process_step,
            "verify")
        self.STEPS = STEPS
        self.REPS = REPS
        self.LOW_INIT = 1.0
        self.HIGH_INIT = 1.05

        #self.second_pass = False
        self.notes = None
        self.verify_good = True

    def set_data(self, inst_type, st, dyn, finger_midi, forces, files):
        task_base.TaskBase.set_data(self, inst_type, st, dyn, files)
        self.taskname += "-%i" % finger_midi
        self.forces = forces
        self.force_init = forces
#self.finger_midi = finger_midi
        # ick
        #self.finger_midi_index = finger_midi

    @staticmethod
    def steps_full():
        return 3 * (STEPS * REPS)

    def _make_files(self):
        self._setup_controller()
        K = 0.01

        def make_file_force(bow_force, fmi, count):
            self.controller.set_stable_K(self.st, self.dyn, fmi, K)
            finger_midi = basic_training.FINGER_MIDIS[fmi]
            # FIXME: oh god ick
            ap = vivi_types.AudioParams( self.st,
                    finger_midi,
                    dynamics.get_distance(self.inst_type,
                        self.dyn),
                    bow_force,
                    dynamics.get_velocity(self.inst_type,
                        self.dyn))
            attack_filename = self.files.make_attack_filename(
                    self.taskname,
                    ap, count)
            #print attack_filename

            self.controller.reset()
            self.controller.filesNew(attack_filename)

            self.controller.comment("verify inst %i st %i dyn %i finger_midi %.3f"
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
            #end.keep_bow_velocity = True

            for bow_direction in [1, -1]:
                begin.physical.bow_velocity *= bow_direction
                #begin.physical.bow_force = bow_force
                #begin.keep_ears = False
                #begin.keep_bow_force = False
                #self.controller.note(begin, ATTACK_LENGTH, end)

                #begin.physical.bow_force = bow_force*0.8
                #begin.keep_ears = True
                #begin.keep_bow_force = True
                #self.controller.note(begin, STABLE_LENGTH-ATTACK_LENGTH, end)
                self.controller.note(begin, STABLE_LENGTH, end)
            self.controller.filesClose()
            #self.process_step.emit()
            return attack_filename

        def split_cats(cats):
            notes = [[],[]]
            #notes = [[],[],[],[]]
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


        def get_cats(basename):
            nac = note_actions_cats.NoteActionsCats()
            nac.load_file(basename, self.files)
            #to_find = "finger_midi %i" % basic_training.FINGER_MIDIS[self.fm]
            to_find = "finger_midi"
            nac.load_note(to_find, full=True)
            cats = [ b for a,b in nac.get_note_cats() ]
            #att = self.portion_attack(cats_means)
            #att = cats_means # consider entire note
            #cost = self.get_cost(att)
            notes = split_cats(cats)
            return notes

        def process_cats(cats):
            #print len(cats)
            mean = numpy.mean(cats)
            return mean
        #    #std = numpy.std(cats)
        #    #exit(1)
        #    #if std > 0.5:
            #    return 0
        #    if mean < -0.5:
        #        direction = -1
        #    elif mean > 0.5:
        #        direction = 1
        #    else:
        #        direction = 0
        #    return direction

        def handle_finger(fmi):
            files = []
            init = self.force_init[fmi]
            #low = scipy.stats.gmean( [init[0], init[1]])
            #high = scipy.mean( [init[1], init[2]])
            low = init[0]
            if low < 0.01:  
                low = 0.01
            high = init[2]
    
            # sanity check
            lows = []
            highs = []
            mids = []

    
            low_files = []
            high_files = []
            lows.append(low)
            highs.append(high)
            for count in range(1,self.REPS+1):
                low_filename = make_file_force(low, fmi, count)
                low_cats = []
                low_cats.extend( sum( get_cats(low_filename), []) )
                low_direction = process_cats(low_cats)
                low_files.append((low, low_filename, low_direction))
                high_filename = make_file_force(high, fmi, count)
                high_cats = []
                high_cats.extend( sum( get_cats(high_filename), []) )
                high_direction = process_cats(high_cats)
                high_files.append((high, high_filename, high_direction))
                #print low_direction, high_direction
                if low_direction > LOW_MEAN_ACCEPTED or high_direction < HIGH_MEAN_ACCEPTED:
                    #print "PANIC: fail to begin attack search"
                    self.verify_good = False
                self.process_step.emit()
                self.process_step.emit()

            def process(force, fmi, lows, mids, highs, low_files,
                    high_files):
                #print "%.3f\t%.3f\t%.3f" % (
                #    low, force, high)
                these_files = []
                directions = []
                for count in range(1,self.REPS+1):
                    mid_filename = make_file_force(force, fmi, count)
                    mid_cats = get_cats(mid_filename)
                    mid_direction1 = process_cats(mid_cats[0])
                    mid_direction2 = process_cats(mid_cats[1])
                    mid_direction = numpy.mean((mid_direction1, mid_direction2))
                    #if mid_direction1 != mid_direction2:
                    #    mid_direction1 = 0
                    these_files.append( (force, mid_filename, mid_direction))
                    directions.append(mid_direction1)
                if numpy.mean(directions) < LOW_MEAN_ACCEPTED:
                    lows.append(force)
                    #low_files = these_files
                    low_files.extend(these_files)
                    #print "low"
                elif numpy.mean(directions) > HIGH_MEAN_ACCEPTED:
                    highs.append(force)
                    #high_files = these_files
                    high_files.extend(these_files)
                    #print "high"
                else:
                    mids.append(force)
                    files.extend(these_files)
                    #print "mid"
                for count in range(self.REPS):
                    self.process_step.emit()
                return low_files, high_files

            while len(mids) == 0:
                if (len(lows) + len(highs) + len(mids)) >= STEPS: 
                    break
                #force = numpy.mean( (max(lows), min(highs)) )
                force = scipy.stats.gmean( (max(lows), min(highs)) )
                #print "init", fmi, max(lows), force, min(highs)
                low_files, high_files = process(force, fmi, lows,
                    mids, highs, low_files, high_files)
            while True:
                if (len(lows) + len(highs) + len(mids)) >= STEPS: 
                    break
                #print max(lows), min(mids), max(mids), min(highs)
                lowdistrel = min(mids) / max(lows)
                highdistrel = min(highs) / max(mids)
                #print lowdistrel, highdistrel
                if lowdistrel > highdistrel:
                    force = scipy.stats.gmean( (max(lows), min(mids)) )
                    force *= random.uniform(0.95, 1.05)
                else:
                    force = scipy.stats.gmean( (max(mids), min(highs)) )
                    force *= random.uniform(0.95, 1.05)
                #print "main", max(lows), min(mids), max(mids), min(highs)
                #print "new force:\t", force
                # do force
                low_files, high_files = process(force, fmi, lows,
                    mids, highs, low_files, high_files)
            files.extend(low_files)
            files.extend(high_files)
            files.sort()
            if len(mids) == 1:
                mids.append( mids[0]*1.05 )
            elif len(mids) == 0:
                mids.append( max(lows) )
                mids.append( min(highs) )
                self.verify_good = False
            self.mids[fmi] = [ min(mids), max(mids) ]
            mids.sort()
            #print mids

            return files
   
        self.kept_files = [[], [], []]
        self.mids = [[], [], []]
        for fmi in range(3):
            #print '-------------- ', fmi
            self.kept_files[fmi] = handle_finger(fmi)
        #handle_finger(1, self.kept_files[1])
        #handle_finger(2, self.kept_files[2])

        #print self.kept_files
        #print self.mids

        return


        #print self.forces
        #import scipy.special
        #agm = scipy.special.agm(min(self.forces), max(self.forces))
        #agm /= 4.0
        #mid = (min(self.forces) + max(self.forces)) / 2
        #mid /= 8.0
        #lower = list(numpy.linspace(min(self.forces), mid, STEPS/2+1))
        ###upper = list(numpy.linspace(agm, max(self.forces), STEPS/2+2))[:-1]
        #upper = list(numpy.exp(
        #    numpy.linspace(
        #        numpy.log(mid),
        #        numpy.log(max(self.forces)),
        #        STEPS/2+1)))
        #self.test_range = list(set(lower + upper))

        #self.test_range = list(numpy.linspace(min(self.forces),
        #    max(self.forces), STEPS))
        #self.test_range = list(numpy.exp(
            #numpy.linspace(
            #    numpy.log(min(self.forces)),
            #    numpy.log(max(self.forces)),
            #    STEPS)))
        #print "TEST:", self.test_range
        #print "fmi:", self.finger_midi_index
        #print self.forces
        #self.test_range = self._make_forces(self.forces, 7)
        self.test_range = []
        #forces = self.test_range
        #self.test_range = numpy.array([forces[0], forces[1], forces[2],
        #    forces[4],
        #    forces[6], forces[7], forces[8]])
        #forces = self.test_range

        K = 1.0
        self.controller.set_stable_K(self.st, self.dyn, K)
        for fmi, finger_midi in enumerate(FINGERS):
            test_forces = self._make_forces(self.forces[fmi], 9)
            test_forces = test_forces[3:6]
            self.test_range.extend( list(test_forces))
            #print self.test_range
            for count in range(self.REPS):
                # ick
                #fmi = self.finger_midi_index
                #finger_midi = self.finger_midi
                #finger_midi = basic_training.FINGER_MIDIS[fmi]
                #test_forces = numpy.append(numpy.linspace(
                #      self.forces[fmi][0],
                #      self.forces[fmi][1],
                #      num=3, endpoint=False),
                #    numpy.linspace(
                #      self.forces[fmi][1],
                #      self.forces[fmi][2],
                #      num=4, endpoint=True))
                #for a in test_forces:
                #    print "%.3f " % a,
                #print
                #test_forces = self.test_range
                #print test_forces
                #for fmi, finger_midi in enumerate(basic_training.FINGER_MIDIS):
                for bow_force in test_forces:
                    audio_params = vivi_types.AudioParams(
                                self.st, finger_midi,
                                dynamics.get_distance(self.inst_type,self.dyn),
                                bow_force,
                                dynamics.get_velocity(self.inst_type,self.dyn))
                    verify_filename = self.files.make_verify_filename(
                            self.taskname,
                            audio_params,
                            count)
                    #print verify_filename
                    self.controller.filesNew(verify_filename)
                    self.controller.comment(
                            "verify int %i st %i dyn %i finger_midi %.3f"
                            % (self.inst_type, self.st, self.dyn, finger_midi))
                    begin = vivi_controller.NoteBeginning()
                    vivi_types.audio_params_to_physical(
                            audio_params, self.dyn, begin.physical)
                    end = vivi_controller.NoteEnding()
                    end.keep_bow_velocity = True
                        #for bow_direction in [1, -1]:
                        #    begin.physical.bow_velocity *= bow_direction
                        #    self.controller.note(begin, STABLE_LENGTH, end)

                        #print "Starting note, force:", bow_force
                    self.controller.note(begin, STABLE_LENGTH, end)
                    self.controller.filesClose()
                self.process_step.emit()

    def get_stable_files_info(self):
        #files = self._get_files()

        #self._setup_lists_from_files(files)

        # ASSUME: no screw-ups in the file creation
        #fm = basic_training.FINGER_MIDIS[self.finger_midi_index]
        #fm = self.finger_midi
        #self.num_rows = len(self.counts[0]) * len(self.extras[0])
        #self.num_rows = len(self.counts[0])
        #self.num_cols = len(self.forces_initial[0])*len(self.finger_midis)
        #self.num_counts = len(self.counts[0])

        self.num_rows = REPS*3
        self.num_counts = REPS
        self.num_cols = STEPS

        #print self.num_rows, self.num_cols
        # initialize 2d array
        self.notes = []
        for i in range(self.num_rows):
            self.notes.append([])
            for j in range(self.num_cols):
                self.notes[i].append(None)

        row = 0
        col = 0
        for i in range(3):
            row = i*self.num_counts
            col = 0
            #print len(self.kept_files[i])
            for vals in self.kept_files[i]:
                force, filename, direction = vals
                nac = note_actions_cats.NoteActionsCats()
                nac.load_file(filename, self.files)
                #to_find = "finger_midi %i" % fm
                to_find = "finger_midi"
                nac.load_note(to_find, full=True)
                #print row, col
                self.notes[row][col] = (nac, direction, filename)
                row += 1
                if (row % REPS) == 0:
                    row = i*self.num_counts
                    col += 1
        return


        for filename in files:
            params, extra, count = self.files.get_audio_params_extra(filename)
            finger_midi = params.finger_midi
            fmi = FINGERS.index(finger_midi)
            force = params.bow_force
            #if finger_midi != self.finger_midi:
            #if finger_midi != basic_training.FINGER_MIDIS[self.finger_midi_index]:
            #    continue
            #print filename, self.finger_midis, finger_midi, fmi, self.finger_midi_index
            count_i = self.counts[finger_midi].index(count)
            #K_i = self.extras[finger_midi].index(extra)
            force_i = self.forces_initial[finger_midi].index(force)
            #force_i = self.test_range.index(force)

            # and setup self.examines
            row = count_i
            col = force_i + len(self.finger_midis)*fmi
            #print row, col

            nac = note_actions_cats.NoteActionsCats()
            nac.load_file(filename[0:-4], self.files)
            #to_find = "finger_midi %i" % fm
            to_find = "finger_midi"
            nac.load_note(to_find)
            examine_cats = nac.note_cats_means
            rms = self.get_rms(examine_cats)
            self.notes[row][col] = (nac, rms, filename)
            #print row, col, filename

    def _examine_files(self):
        self.get_stable_files_info()
        return 0, 1.0

        attack = numpy.zeros( (self.num_rows, self.num_cols) )
        #print self.num_rows, self.num_cols
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                #print row, col
                rms = self.notes[row][col][1]
                attack[row][col] = rms
                #print attack[row][col]

        forces_initial = self.forces_initial[0]
        #if True:
        if False:
            attack_file = open('verify-%i.txt' % 0, 'w')
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    attack_file.write("%g %g\n" % (
                        forces_initial[col],
                        attack[row][col]))
                attack_file.write("\n")
            attack_file.close()
        #K = self.extras[0][stable_index]
        #print "stable index %i, K = %.2f " %(stable_index, K)
        #col_means = numpy.mean(abs(attack), axis=0)

        index = 0
        best_force = 0
        #index = numpy.argmin(col_means)
        #best_force = forces_initial[index]
        #print index, best_force
        return index, best_force

    def get_rms(self,cats):
        #rms = 0.0
        net = 0.0
        #count = 0
        for cat in cats:
            if cat == vivi_defines.CATEGORY_NULL:
                continue
            #rms += cat*cat
            net += cat
            #count += 1
        #rms /= count
        #rms = math.sqrt(rms)
        return net
        #return rms

