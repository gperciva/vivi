#!/usr/bin/env python

import subprocess
import shutil

def get_steps(job):
    return 2

def calculate(job, process_step):
    job.mixed_filename = job.ly_basename + "-all.wav"
    process_step.emit()
    if len(job.audio_filenames) == 1:
        shutil.copyfile(job.audio_filenames[0], job.mixed_filename)
    else:
        # mixing
        cmd = "ecasound "
        for i, wav_filename in enumerate(job.audio_filenames):
            pan_value = job.pans[i]
            amp_value = job.amps[i]
            cmd += " -a:%i %s -erc:1,2 -epp:%i -ea:%i " % (
                i, wav_filename, pan_value, amp_value)
        cmd += " -a:all -o %s " % (job.mixed_filename)
        cmd = cmd.split()
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        p.wait()
    #cmd = "normalize-audio %s " % job.mixed_filename
    #cmd = cmd.split()
    #p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
    #        stderr=subprocess.PIPE)
    #p.wait()
    process_step.emit()
    return job

