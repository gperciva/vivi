#!/usr/bin/env python

import task_stable


def get_steps(self):
    return task_stable.TaskStable.steps_full()

def calculate(job, process_step):
    job.task = task_stable.TaskStable(
        job.controller, process_step)
    job.task.set_data(
        job.inst_type,
        job.st, job.dyn, job.force_init, job.files)
    job.most_stable = job.task.calculate_full()
    return job


