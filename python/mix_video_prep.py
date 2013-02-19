#!/usr/bin/env python

import os.path

import state
import shared

import utils
import glob
import vivi_defines

def start_job(files, quality):
    job = state.Job(vivi_defines.TASK_MIX_VIDEO)
    job.movie_base_dirname = files.get_ly_movie_dir()
    job.parts_dirnames = [dirname
        for dirname in glob.glob(os.path.join(job.movie_base_dirname, "*"))
            if os.path.isdir(dirname) ]
    # TODO: ick
    def strings_order(instrument_name):
        name = instrument_name.split("-")[-2]
        inst_num = int(instrument_name.split("-")[-1])
        if name == "violin":
            return inst_num
        elif name == "viola":
            return 10 + inst_num
        elif name == "cello":
            return 20 + inst_num
        else:
            return 0
    job.parts_dirnames.sort(key=strings_order)
    if len(job.parts_dirnames) == 1:
        job.images_dirname = job.parts_dirnames[0]
    else:
        job.images_dirname = job.movie_base_dirname + "-combo"
        if not os.path.exists(job.images_dirname):
            os.makedirs(job.images_dirname)
    job.mixed_audio_filename = files.get_ly_extra("-all.wav")

    if quality == 0:
        job.movie_filename = job.movie_base_dirname+"-preview.avi"
    else:
        job.movie_filename = job.movie_base_dirname+"-movie.avi"
    steps = shared.thread_pool.add_task(job)
    return steps


