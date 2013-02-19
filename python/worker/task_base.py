#!/usr/bin/env python
""" base class for Task_* """

import random
import numpy

import dynamics
import scipy

SKIP_REBUILD = False
#SKIP_REBUILD = True

class TaskBase():
    """ base class for Task_* """

    def __init__(self, controller, emit, taskname):
        """ constructor """
        self.controller = controller
        self.process_step = emit
        self.taskname = taskname

        self.STEPS = 10 # even number to avoid picking the
                # same value on second pass
        self.REPS = 2
        self.second_pass = False
        self.third_pass = False
        self.second = False

        self.LOW_INIT = 0.0 # blah numbers to start with
        self.HIGH_INIT = 1.0
        self.low_variable = self.LOW_INIT
        self.high_variable = self.HIGH_INIT
        self.test_range = None

    def set_data(self, inst_type, st, dyn, files):
        self.inst_type = inst_type
        self.st = st
        self.dyn = dyn
        self.files = files

    def _remove_previous_files(self):
        """ remove files from previous computation of task """
        self.files.delete_files(
            self.files.get_task_files(self.taskname, self.st,
                dynamics.get_distance(self.inst_type, self.dyn),
                dynamics.get_velocity(self.inst_type, self.dyn)))

    def steps_full(self):
        return 0

    def calculate_full(self):
        """ does a full (re)calculation of the task """
        #self._init_range()
        if not SKIP_REBUILD:
            self._remove_previous_files()
            self._make_files()
        first_answer_index, first_answer = self._examine_files()
        if not self.second_pass:
            return first_answer
        #print first_answer_index, first_answer
        #self._zoom_range(first_answer_index)
        #self._remove_previous_files()
        self.second = True
        self._make_files()
        second_answer_index, second_answer = self._examine_files()
        if not self.third_pass:
            return second_answer
        self._zoom_range(second_answer_index)
        self._remove_previous_files()
        self._make_files()
        third_answer_index, third_answer = self._examine_files()
        return third_answer

    def _init_range(self):
        self.low_variable = self.LOW_INIT
        self.high_variable = self.HIGH_INIT
        self.test_range = scipy.linspace(self.low_variable,
                                self.high_variable, self.STEPS)

    def _make_forces(self, extreme_forces, num):
        a = extreme_forces[0]
        b = extreme_forces[1]
        c = extreme_forces[2]
        #print a, b, c, num
        forces = numpy.append(
            b -( scipy.logspace(scipy.log10(a), scipy.log10(b),
            num=num/2+1) - a),
            scipy.logspace(scipy.log10(b), scipy.log10(c),
            num=num-num/2)[1:]
            )
        forces = numpy.array( sorted(list(set(forces))) )
        if len(forces) != num:
            Exception("problem with forces: length ", len(forces))
        #print forces
        #for i in range(len(forces)):
        #    f = forces[i]
        #    rand = random.uniform( 0.99*f, 1.01*f)
        #    forces[i] = rand
        return forces


    def _make_files(self):
        pass

    def _setup_lists_from_files(self, files):
        # variables about the files
        self.forces_initial = {}
        self.extras = {}
        self.counts = {}
        self.finger_midis = []
        # get info about the files
        for filename in files:
            params, extra, count = self.files.get_audio_params_extra(filename)
            finger_midi = params.finger_midi
            force = params.bow_force

            if not finger_midi in self.finger_midis:
                self.finger_midis.append(finger_midi)
            # setup dictionaries
            if not finger_midi in self.forces_initial:
                self.forces_initial[finger_midi] = []
            if not finger_midi in self.extras:
                self.extras[finger_midi] = []
            if not finger_midi in self.counts:
                self.counts[finger_midi] = []
            # setup lists
            forces_initial = self.forces_initial[finger_midi]
            extras = self.extras[finger_midi]
            counts = self.counts[finger_midi]

            if not force in forces_initial:
                forces_initial.append(force)
            if not extra in extras:
                extras.append(extra)
            if not count in counts:
                counts.append(count)


    def _examine_files(self):
        pass

    def _zoom_range(self, index):
        # only update if it's in the range
        #print self.test_range
        #print self.low_variable, index, self.high_variable
        if (index-1) >= 0:
            self.low_variable = self.test_range[index-1]
        if (index+1) <= len(self.test_range)-1:
            self.high_variable = self.test_range[index+1]
        #print self.test_range[index+1]
        #print self.st, self.test_range
        #print self.st, index
        #print self.low_variable, self.high_variable
        self.test_range = scipy.linspace(self.low_variable,
                                self.high_variable, self.STEPS)
        #print self.st, self.test_range

    def _get_files(self):
        return self.files.get_task_files(self.taskname, self.st,
            dynamics.get_distance(self.inst_type, self.dyn),
            dynamics.get_velocity(self.inst_type, self.dyn))

    def _setup_controller(self):
        self.controller.load_ears_training(self.st,
            self.files.get_mpl_filename(self.st))


