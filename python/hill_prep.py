#!/usr/bin/env python

import shared
import state
import vivi_defines

import instrument_numbers

import notes_info

import performer
import os
import copy
import glob
import random

NUM_REPETITIONS = 20
TRY_ALTERATIONS_SCHEME = [(1.0, 1.0), (1.05, 1.15), (1.2, 1.4)]

def get_num_jobs():
    return NUM_REPETITIONS * (2* len(TRY_ALTERATIONS_SCHEME) - 1)

def alteration_filename(alteration):
    if alteration < 0:
        return "_alter_%.3f" % alteration
    elif alteration == 0:
        return "_alter_1.0"
    else:
        return "_alter_+%.3f" % alteration


def start_job(files, get_instrument_files):
    ### clear out old files
    basename = files.get_ly_basename()
    old_files = glob.glob(os.path.join(files.hills_dir,
            basename) + "*")
    files.delete_files(old_files)

    total_steps = 0
    num_audio_files = len(files.notes_all)
    for i in range(num_audio_files):
        job = state.Job(vivi_defines.TASK_HILL_CLIMBING)
        files.set_notes_index(i)
        job.main_files = files
        job.notes_filename = files.get_notes()
        inst_name, total_num, inst_num = instrument_numbers.instrument_name_from_filename(job.notes_filename)
        print inst_name, total_num, inst_num
        job.instrument_number = inst_num
        #job.distinct_instrument_number = dist_inst_num
        if total_num >= 7:
            inst_type = 2
        elif total_num >= 5:
            inst_type = 1
        else:
            inst_type = 0
        job.inst_type = inst_type
        job.inst_num = inst_num
        inst_files = get_instrument_files(total_num)

        if inst_type == 0:
            job.reduced_inst_num = inst_num % 5
        elif inst_type == 1:
            job.reduced_inst_num = inst_num % 2
        elif inst_type == 2:
            job.reduced_inst_num = inst_num % 3

        job.alterations_filename = job.main_files.get_notes_ext(
            ".alterations")

        performer_prep = performer.Performer(inst_type,
            job.reduced_inst_num,
            inst_files)
        performer_prep.load_file(job.notes_filename)
        job.files = inst_files
        job.notes = list(performer_prep.style.notes)
        job.audio_filename = performer_prep.audio_filename

        job.mpl_filenames = []
        for st in range(4):
            mpl_filename = inst_files.get_mpl_filename(st)
            job.mpl_filenames.append(mpl_filename)
        total_steps += go(job)
#        total_steps += shared.thread_pool.add_task(job)
    return total_steps 

def go(job):
    total_steps = 0
    info = notes_info.NotesInfo()
    info.load_file(job.alterations_filename)
    pncs = info.get_pncs()

    evals = []
    attempt_alterations = []
    for alteration_scheme in list(TRY_ALTERATIONS_SCHEME):
        (low, high) = alteration_scheme
        factor = random.uniform(low, high)
        attempt_alterations.append(factor)
        if factor != 1.0:
            attempt_alterations.append(1.0/factor)
    print "attempting alterations:\t", attempt_alterations

    for alteration in attempt_alterations:
        # setup filenames
        alteration_base_audio_filename = (job.audio_filename +
           alteration_filename(alteration))
        alteration_base_audio_filename = alteration_base_audio_filename.replace(
            job.files.music_dir, job.files.hills_dir)
        dirname = os.path.dirname(alteration_base_audio_filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        this_alterations_filename = (alteration_base_audio_filename+".alterations")
        # reload old, write new .alterations file
        info.load_file(job.alterations_filename)
        pncs = info.get_pncs()
        for pnc in pncs:
            prev = info.info[pnc][-1]
            info.add(pnc, prev * alteration)
        info.write_file(this_alterations_filename)
        alteration_costs = []
        for i in range(NUM_REPETITIONS):
            # generate audio using new file
            this_job = copy.copy(job)
            this_job.audio_filename = alteration_base_audio_filename + "_hill_%04i" % i
            this_job.alterations_filename = this_alterations_filename
            total_steps += shared.thread_pool.add_task(this_job)
    return total_steps

