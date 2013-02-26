#!/usr/bin/env python

import subprocess
import style_base

import notes_info
import dynamics

DEBUG_PARAMS = 0
EXTRA_FINAL_REST = 0.5


PROFILE = False
PROFILE = True

if PROFILE:
    import cProfile

def get_steps(job):
    return len(job.notes)

def time_calculate(job, process_step):
    setup_controller(job)

    job.controller.filesNew(job.audio_filename)

    job.current_st = None
    job.arco = False

    info = notes_info.NotesInfo()
    info.load_file(job.alterations_filename)
    #print job.alterations_filename

    for note in job.notes:
        if style_base.StyleBase.is_note(note):
            render_note(job, note, info)
        else:
            render_rest(job, note)
        process_step.emit()
    job.controller.rest(EXTRA_FINAL_REST)

    job.controller.filesClose()
    process_step.emit()


def calculate(job, process_step):
    if PROFILE:
        cProfile.runctx("time_calculate(job, process_step)",
            globals(), locals(),
            "profile.stats")
    else:
        time_calculate(job, process_step)
    return job


def render_note(job, note, info):
    try:
        alters = info.info[note.point_and_click]
        alter = alters[-1]
    except KeyError:
        alter = 1
        print "failed to find:", note.point_and_click
    #print alter

    if note.pizz:
        if job.arco:
            job.controller.bowStop()
            job.arco = False
        if DEBUG_PARAMS:
            print '---- pizz'
            note.begin.print_params()
            note.end.print_params()
        if note.begin.physical.dynamic < 0:
            print "CRITICAL ERROR: dynamic below 0!"
        job.controller.pizz(note.begin, note.duration)
    else:
        if DEBUG_PARAMS:
            print '---- note'
            note.begin.print_params()
            note.end.print_params()
        job.arco = True
        job.controller.note(note.begin, note.duration,
            note.end,
            note.point_and_click, alter)

def render_rest(job, note):
    if DEBUG_PARAMS:
            print '---- rest'
    if job.arco:
        job.controller.bowStop()
        job.arco = False
    job.controller.rest(note.duration)


def setup_controller(job):
    for st in range(4):
        job.controller.load_ears_training(st, job.mpl_filenames[st])
        #print job.mpl_filenames[st]
        for dyn in range(dynamics.NUM_DYNAMICS):
            job.controller.load_dyn_parameters(st, dyn,
                job.files.get_dyn_vivi_filename(st, dyn,
                job.reduced_inst_num),
                    )


