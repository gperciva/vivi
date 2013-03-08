#!/usr/bin/env python

from PyQt4 import QtCore

import Queue

import dispatcher
import vivi_controller

#NUM_THREADS = 4
NUM_THREADS = 3
#NUM_THREADS = 1

class ThreadPool(QtCore.QObject):
    process_step = QtCore.pyqtSignal()
    done_task = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.tasks_queue = Queue.Queue()
        self.results_queue = Queue.Queue()

        self.workers = []
        for task_number in range(NUM_THREADS):
            worker = dispatcher.Worker(
                self.tasks_queue, self.results_queue)
            worker.process_step.connect(self.process_step_emit)
            worker.done_task.connect(self.done_task_emit)
            worker.DEBUG_task_number = task_number
            self.workers.append(worker)
        self.tasks_waiting = 0

    def get_results_queue(self):
        return self.results_queue

    def all_tasks_finished(self):
        return (self.tasks_waiting == 0)

    def add_task(self, task):
        steps = dispatcher.Worker.get_steps(task)
        self.tasks_queue.put(task)
        self.tasks_waiting += 1
        #print "now waiting for ", self.tasks_waiting
        return steps

    def process_step_emit(self):
        self.process_step.emit()

    def done_task_emit(self):
        self.tasks_waiting -= 1
#        print "now waiting for ", self.tasks_waiting
        if self.tasks_waiting < 0:
            raise Exception("More tasks completed than begun!")
        self.done_task.emit()

