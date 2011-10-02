#!/usr/bin/env python

from PyQt4 import QtCore

IDLE = 0
BASIC_TRAINING = 1
SVM = 2
ACCURACY = 3
STABLE = 4
ATTACKS = 5
DAMPEN = 6

class State(QtCore.QObject):
    next_step = QtCore.pyqtSignal(int, int, name='next_step')
    finished_step = QtCore.pyqtSignal(int, int, name='finished_step')

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.job_type = IDLE
        self.jobs = []
        self.job_index = 0
        self.parallel = False
        self.done_steps = 0

    def idle(self):
        self.job_type = IDLE
        self.jobs = []
        self.job_index = 0
        self.done_steps = 0

    def step(self):
        self.done_steps += 1
        if self.parallel:
            if self.done_steps == sum(self.jobs):
                self.finished_step.emit(self.job_type, self.job_index)
        else:
            if self.done_steps == self.jobs[self.job_index]:
                self.finished_step.emit(self.job_type, self.job_index)
                self.jobs[self.job_index] = 0
                self.done_steps = 0
                self.job_index += 1
                self.start()

    def prep(self, job_type, jobs, parallel=False):
        self.job_type = job_type
        self.jobs = jobs
        self.parallel = parallel
        self.done_steps = 0

    def start(self):
        for i in range(len(self.jobs)):
            if self.jobs[i] > 0:
                self.job_index = i
                self.next_step.emit(self.job_type, self.job_index)
                if not self.parallel:
                    return

