#!/usr/bin/env python

import state
import shared

import utils
import glob
import vivi_defines

import numpy
import os.path

def sort_filenames(filename):
    at = os.path.splitext(os.path.basename(filename))[0].split("-")
    #print at
    value = 0
    if at[-2] == 'violin':
        value += 100
    elif at[-2] == 'viola':
        value += 200
    elif at[-2] == 'cello':
        value += 300
    value += int(at[-1])
    return value

def start_job(ly_basename):
    audio_filenames = glob.glob(ly_basename + "*.wav")
    audio_filenames = filter(lambda x: not x.endswith(".forces.wav"),
        audio_filenames)
    audio_filenames = filter(lambda x: "-s0.wav" not in x,
        audio_filenames)
    audio_filenames = filter(lambda x: "-s1.wav" not in x,
        audio_filenames)
    audio_filenames = filter(lambda x: "-s2.wav" not in x,
        audio_filenames)
    audio_filenames = filter(lambda x: "-s3.wav" not in x,
        audio_filenames)
    audio_filenames.sort(key=sort_filenames)
    #print audio_filenames

    job = state.Job(vivi_defines.TASK_MIX_AUDIO)
    job.ly_basename = ly_basename
    job.audio_filenames = audio_filenames
    job.pans = pan(audio_filenames)
    #print job.pans
    job.amps = amplification(audio_filenames)
#    print job.pans
    steps = shared.thread_pool.add_task(job)
    return steps

def filenames_list_contains(filenames, values):
    if len(filenames) != len(values):
        return False
    found = [False] * len(values)
    for filename in filenames:
        for i, val in enumerate(values):
            if val in filename:
                found[i] = True
    if False in found:
        return False
    return True
    

def pan(filenames):
            #pan = int(100*i / (num_parts-1))
            #pan = int(100*(i+1) / (self.num_parts+1))
    if filenames_list_contains(filenames, ["violin-1", "violin-2",
        "violin-3", "violin-4", "viola-1", "cello-1" ]):
        return [20, 80, 30, 70, 40, 60]
    if filenames_list_contains(filenames, ["violin-1", "violin-2","cello-1" ]):
        return [25, 75, 50]
    #elif filenames_list_contains(filenames, ["viola-1", "violin-1", "violin-2"]):
    #    return [50, 25, 75]
    elif len(filenames) == 1:
        return [50]
    elif len(filenames) == 2:
        return [25, 75]
    elif len(filenames) == 3:
        return [20, 50, 80]
    else:
        return numpy.linspace(25, 75, num=len(filenames))
    return [50]

def amplification(filenames):
    amps = []
    for filename in filenames:
        if "violin-1" in filename:
            amps.append(100)
        elif "violin-2" in filename:
            amps.append(100)
        elif "violin-3" in filename:
            amps.append(100)
        elif "viola" in filename:
            amps.append(100)
        elif "cello" in filename:
            amps.append(100)
        else:
            #print "Unrecognized instrument; what amplication?"
            amps.append(100)
    return amps


