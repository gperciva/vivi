#!/usr/bin/env python

from PyQt4 import QtCore

import vivi_defines

STRING_JOBS = [
    vivi_defines.TASK_TRAINING, vivi_defines.TASK_ACCURACY,
    ]
DYN_JOBS = [
    vivi_defines.TASK_VERIFY, vivi_defines.TASK_STABLE,
    vivi_defines.TASK_ATTACK, vivi_defines.TASK_DAMPEN,
    ]
JOBS_WITH_CONTROLLER = [
    vivi_defines.TASK_TRAINING, vivi_defines.TASK_ACCURACY, # for ears
    vivi_defines.TASK_VERIFY, vivi_defines.TASK_STABLE,
    vivi_defines.TASK_ATTACK, vivi_defines.TASK_DAMPEN,
    vivi_defines.TASK_RENDER_AUDIO,
    vivi_defines.TASK_HILL_CLIMBING,
]

class Job():
    def __init__(self, job_type):
        self.job_type = job_type


class State(QtCore.QObject):
    # job_type, job_index or -1 (for parallel)
    next_step = QtCore.pyqtSignal(int, int, name='next_step')
    finished_step = QtCore.pyqtSignal(int, int, name='finished_step')

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.job_type = 0
        self.jobs = []
        self.job_index = None
        self.parallel = False
        self.parallel_steps = None

    def step(self):
        if self.parallel:
            self.parallel_steps += 1
            if self.parallel_steps == sum(self.jobs):
                self.finished_step.emit(self.job_type, -1)
        else:
            self.jobs[self.job_index] -= 1
            if self.jobs[self.job_index] == 0:
                self.finished_step.emit(self.job_type, self.job_index)
                self.start()

    def prep(self, job_type, jobs, parallel=False):
        self.job_type = job_type
        self.jobs = jobs
        self.parallel = parallel

    def start(self):
        if self.parallel:
            self.job_index = None
            self.parallel_steps = 0
        for i, job in enumerate(self.jobs):
            if job > 0:
                self.next_step.emit(self.job_type, i)
                if not self.parallel:
                    self.job_index = i
                    return

