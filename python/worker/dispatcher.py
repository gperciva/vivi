#!/usr/bin/env python

import subprocess

from PyQt4 import QtCore

import vivi_defines

import vivi_controller

# actual calculations here
import train
import accuracy

import verify
import stable
import attack
import dampen

import lilypond_compile
import render_audio
import mix_audio
import hill_climbing
import mix_hill

import render_video
import mix_video

import play_media
##


import utils
import dirs
import state

import operator

import math
import scipy

import os

import task_stable
import task_attack
import task_dampen

import basic_training

class Worker(QtCore.QThread):
    process_step = QtCore.pyqtSignal()
    done_task = QtCore.pyqtSignal()

    def __init__(self, tasks_queue, results_queue):
        QtCore.QThread.__init__(self)

        self.tasks_queue = tasks_queue
        self.results_queue = results_queue
        # lazy loading for these
        self.controller = [None] * vivi_defines.NUM_DISTINCT_INSTRUMENTS
        self.mutex = QtCore.QMutex()

        self.DEBUG_task_number = -1
        self.start()

    def run(self):
        while True:
            job = self.tasks_queue.get()
            #print "worker %i job %i" % (
            #    self.DEBUG_task_number, job.job_type)
            #print job.st, job.job_type
            #print job.instrument_number
            if job.job_type in state.JOBS_WITH_CONTROLLER:
                job.controller = self.get_controller(
                    job.inst_type,
                    job.inst_type,
                    job.inst_num,
                    )

            if job.job_type == vivi_defines.TASK_TRAINING:
                job = train.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_ACCURACY:
                job = accuracy.calculate(job, self.process_step)
            #
            elif job.job_type == vivi_defines.TASK_VERIFY:
                job = verify.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_STABLE:
                job = stable.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_ATTACK:
                job = attack.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_DAMPEN:
                job = dampen.calculate(job, self.process_step)
            #
            elif job.job_type == vivi_defines.TASK_LILYPOND:
                job = lilypond_compile.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_RENDER_AUDIO:
                job = render_audio.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_MIX_AUDIO:
                job = mix_audio.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_PLAY_AUDIO:
                job = play_media.play_audio(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_HILL_CLIMBING:
                job = hill_climbing.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_MIX_HILL:
                job = mix_hill.calculate(job, self.process_step)

            elif job.job_type == vivi_defines.TASK_RENDER_VIDEO_PREVIEW:
                job = render_video.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_RENDER_VIDEO:
                job = render_video.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_MIX_VIDEO:
                job = mix_video.calculate(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_PLAY_VIDEO_PREVIEW:
                job = play_media.play_video(job, self.process_step)
            elif job.job_type == vivi_defines.TASK_PLAY_VIDEO:
                job = play_media.play_video(job, self.process_step)
            else:
                raise Exception("Unknown job type")

            self.process_step.emit()
            self.tasks_queue.task_done()
            self.results_queue.put(job)
            self.done_task.emit()

### lazy loading access methods
    def get_controller(self, index, instrument_type, instrument_number):
        #print "worker %i looking for %i %i" % (
        #    self.DEBUG_task_number, index, instrument_number)
        if not self.controller[index]:
            self.mutex.lock()
            #print "worker %i making new %i %i %i" % (
            #    self.DEBUG_task_number, index, instrument_type, instrument_number)
            self.controller[index] = vivi_controller.ViviController(
                instrument_type,
                instrument_number)
            ### WTF?!?!?
            import time
            time.sleep(0.1)
            self.mutex.unlock()
        return self.controller[index]



### computations
    @staticmethod
    def get_steps(job):
        # string stuff
        if job.job_type == vivi_defines.TASK_TRAINING:
            module_steps = train.get_steps(job)
        elif job.job_type == vivi_defines.TASK_ACCURACY:
            module_steps = accuracy.get_steps(job)
        # dyn stuff
        elif job.job_type == vivi_defines.TASK_VERIFY:
            module_steps = verify.get_steps(job)
        elif job.job_type == vivi_defines.TASK_STABLE:
            module_steps = stable.get_steps(job)
        elif job.job_type == vivi_defines.TASK_ATTACK:
            module_steps = attack.get_steps(job)
        elif job.job_type == vivi_defines.TASK_DAMPEN:
            module_steps = dampen.get_steps(job)
        # other
        elif job.job_type == vivi_defines.TASK_LILYPOND:
            module_steps = lilypond_compile.get_steps(job)
        elif job.job_type == vivi_defines.TASK_RENDER_AUDIO:
            module_steps = render_audio.get_steps(job)
        elif job.job_type == vivi_defines.TASK_MIX_AUDIO:
            module_steps = mix_audio.get_steps(job)
        elif job.job_type == vivi_defines.TASK_PLAY_AUDIO:
            module_steps = play_media.get_steps(job)
        elif job.job_type == vivi_defines.TASK_HILL_CLIMBING:
            module_steps = hill_climbing.get_steps(job)
        elif job.job_type == vivi_defines.TASK_MIX_HILL:
            module_steps = mix_hill.get_steps(job)

        elif job.job_type == vivi_defines.TASK_RENDER_VIDEO_PREVIEW:
            module_steps = render_video.get_steps(job)
        elif job.job_type == vivi_defines.TASK_RENDER_VIDEO:
            module_steps = render_video.get_steps(job)
        elif job.job_type == vivi_defines.TASK_MIX_VIDEO:
            module_steps = mix_video.get_steps(job)
        elif job.job_type == vivi_defines.TASK_PLAY_VIDEO_PREVIEW:
            module_steps = play_media.get_steps(job)
        elif job.job_type == vivi_defines.TASK_PLAY_VIDEO:
            module_steps = play_media.get_steps(job)
        else:
            raise Exception("Dispatcher: job type not supported")

        return module_steps + 1

