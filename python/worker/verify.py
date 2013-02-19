#!/usr/bin/env python

import task_verify


def get_steps(self):
    return task_verify.TaskVerify.steps_full()

def calculate(job, process_step):
    job.task = task_verify.TaskVerify(job.controller, process_step)
    job.task.set_data(
        job.inst_type,
        job.st, job.dyn,
        0,
        #job.fm,
        job.finger_forces, job.files)
    job.force_init = job.task.calculate_full()
    return job


