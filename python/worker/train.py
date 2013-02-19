#!/usr/bin/env python

def get_steps(job):
    return 1

def calculate(job, process_step):
    ears = job.controller.getEars(job.st)
    ears.set_training(job.mf_filename, job.arff_filename)
    ears.processFile()
    process_step.emit()
    ears.saveTraining(job.mpl_filename)
    return job

