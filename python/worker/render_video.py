#!/usr/bin/env python

import os

import vivi_defines

#IMAGE_THREAD_EMIT_STEPS = 10
IMAGE_THREAD_EMIT_STEPS = 4

def get_steps(job):
    return 2 + IMAGE_THREAD_EMIT_STEPS

def calculate(job, process_step):
    process_step.emit()
    process_step.emit()
    step = int((job.end_frame - job.start_frame)
        / IMAGE_THREAD_EMIT_STEPS)
    for i in range(IMAGE_THREAD_EMIT_STEPS):
        my_start = job.start_frame + i*step
        if i < IMAGE_THREAD_EMIT_STEPS - 1:
            my_end = job.start_frame + (i+1)*step-1
        else:
            my_end = job.end_frame
#        print "rendering images: %i %i", my_start, my_end
        log_filename = "render-%i-%i.log" % (job.logfile_num, i)
        cmd = """actions2images.py -o %s \
-s %i -e %i --fps %i -q %i -l %s %s""" % (
            job.movie_dirname, my_start, my_end, vivi_defines.VIDEO_FPS,
            job.quality, log_filename, job.actions_filename)
        os.system(cmd)
        process_step.emit()

    return job

