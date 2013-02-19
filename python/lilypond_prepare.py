#!/usr/bin/env python
import os
import shutil
import glob

import filecmp

import vivi_defines
import state
import shared


def lily_file_needs_compile(files):
    pdf_dirname = os.path.dirname(files.get_ly_extra(".pdf"))
    if not os.path.isdir(pdf_dirname):
        os.makedirs(pdf_dirname)

    ly_original = files.get_ly_original()
    ly_filename = files.get_ly_extra(".ly")
    if (os.path.isfile(ly_filename) and
        filecmp.cmp(ly_original, ly_filename) and
        os.path.exists(files.get_ly_extra(".pdf"))):
        return False
    shutil.copy(ly_original, ly_filename)
    return True

def remove_old_files(basename):
    for extension in ['*.notes', '*.pdf', '*.midi', '*.log']:
        map(os.remove,
            glob.glob(basename+extension))

def start_job(files):
    remove_old_files(files.get_ly_extra(""))
    job = state.Job(vivi_defines.TASK_LILYPOND)

    job.ly_include_dir = os.path.abspath(os.path.dirname(
        files.get_ly_original()))
    job.pdf_dirname = os.path.dirname(files.get_ly_extra(".pdf"))
    job.ly_filename = files.get_ly_extra(".ly")
    job.ly_basename = files.get_ly_extra("")
    steps = shared.thread_pool.add_task(job)
    return steps

