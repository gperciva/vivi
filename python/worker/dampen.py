#!/usr/bin/env python

import task_dampen


def get_steps(self):
    return task_dampen.TaskDampen.steps_full()

def calculate(job, process_step):
    job.task = task_dampen.TaskDampen( job.controller, process_step)
    job.task.set_data(job.inst_type, job.st, job.dyn,
        job.force_init,
        job.K, job.force_init, job.keep_bow_velocity, job.files)
    job.dampen = job.task.calculate_full()
    return job


