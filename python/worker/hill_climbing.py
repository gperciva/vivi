#!/usr/bin/env python

import render_audio

def get_steps(job):
    return render_audio.get_steps(job)

def calculate(job, process_step):
    return render_audio.calculate(job, process_step)


