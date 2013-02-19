#!/usr/bin/env python

import task_attack


def get_steps(job):
    return task_attack.TaskAttack.steps_full()

def calculate(job, process_step):
    job.task = task_attack.TaskAttack(job.controller, process_step)
    job.task.set_data(
        job.inst_type,
        job.st, job.dyn,
        job.force_init,
        job.K, job.fmi,
        job.files)
    job.force_init = job.task.calculate_full()
    return job


