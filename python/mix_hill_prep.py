#!/usr/bin/env/python

import state
import shared
import vivi_defines

import instrument_numbers

import notes_info

import os
import copy
import glob

def start_job(files, get_instrument_files):
    total_steps = 0
    num_audio_files = len(files.notes_all)
    for i in range(num_audio_files):
        job = state.Job(vivi_defines.TASK_MIX_HILL)
        files.set_notes_index(i)
        job.main_files = files
        job.notes_filename = files.get_notes()

        # get alterations
        basename = files.notes # TODO: fix bad integration
        old_files = glob.glob(os.path.join(files.hills_dir,
            basename) + "*")
        job.alterations = set()
        job.count = 0
        for filename in old_files:
            if "alterations" in filename:
                continue
            relevant = filename.split("alter_")[1]
            split = relevant.split("_hill_")
            alter_text = split[0]
            job.alterations.add( float(alter_text) )
            number = int(split[1].split(".")[0])
            if job.count < number:
                job.count = number

        inst_name, dist_inst_num, inst_num = instrument_numbers.instrument_name_from_filename(job.notes_filename)
        job.instrument_number = inst_num
        job.distinct_instrument_number = dist_inst_num
        inst_files = get_instrument_files(dist_inst_num)

        job.alterations_filename = job.main_files.get_notes_ext(
            ".alterations")

        job.files = inst_files
        job.audio_filename = job.main_files.get_notes_ext(
            "")

        total_steps += shared.thread_pool.add_task(job)
    return total_steps 


