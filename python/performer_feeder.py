#!/usr/bin/env python

from PyQt4 import QtCore
import performer

import shared

import state
import vivi_defines
import vivi_controller
import dirs

import glob

import os.path
import instrument_numbers

import notes_info

def generate_alterations(alterations_filename, pncs):
    info = notes_info.NotesInfo()
    for pnc in pncs:
        info.add(pnc, 1.0)
    info.write_file(alterations_filename)

#def get_notes_from_nac(nac):
#    pncs = []
#    for line in nac.lines:
#        find = line.find("point_and_click")
#        if find >= 0:
#            pnc = line[find:-1]
#            pncs.append(pnc)
#    return pncs
#
def get_pncs_from_notes(notes_filename):
    notes_lines = open(notes_filename).readlines()
    pncs = []
    for line in notes_lines:
        pos = line.find("point-and-click")
        if pos >= 0:
            pnc = line[pos:]
            pnc = pnc.rstrip()
            pnc = pnc.replace("-", "_")
            pncs.append(pnc)
    return pncs



class PerformerFeeder():
    def __init__(self, files):
        self.files = files

    def set_instrument(self, instrument_number):
        pass
        #self.performer.set_instrument(instrument_number)

    def load_file(self, filename):
        #self.performer.load_file(filename)
        pass

    def start_job(self, get_instrument_files):
        total_steps = 0

        old_files = glob.glob(self.files.get_ly_extra("*.wav"))
        #print old_files
        dirs.ViviDirs.delete_files(old_files)

        # mixing needs to happen after this finishes
        self.num_audio_files = len(self.files.notes_all)
        for i in range(self.num_audio_files):
            job = state.Job(vivi_defines.TASK_RENDER_AUDIO)
            self.files.set_notes_index(i)
            job.main_files = self.files

            # remove more old files
            old_files = glob.glob(self.files.get_notes_last("") + "*.actions")
            dirs.ViviDirs.delete_files(old_files)

            job.alterations_filename = job.main_files.get_notes_ext(
                ".alterations")
            if not os.path.exists(job.alterations_filename):
                pncs = get_pncs_from_notes(job.main_files.get_notes())
                generate_alterations(job.alterations_filename, pncs)

            job.notes_filename = self.files.get_notes()
            job.ly_basename = self.files.get_ly_extra("")
            inst_name, total_num, inst_num = instrument_numbers.instrument_name_from_filename(job.notes_filename)
            #print "performer feeder total_num:", total_num, inst_num
            if total_num >= 7:
                inst_type = 2
            elif total_num >= 5:
                inst_type = 1
            else:
                inst_type = 0
            #print "performer feeder:", inst_name, inst_type, inst_num
            job.inst_type = inst_type
            job.inst_num = inst_num
            inst_files = get_instrument_files(total_num)

            if inst_type == 0:
                job.reduced_inst_num = inst_num % 5
            elif inst_type == 1:
                job.reduced_inst_num = inst_num % 2
            elif inst_type == 2:
                job.reduced_inst_num = inst_num % 3
            #print inst_num, job.reduced_inst_num
            performer_prep = performer.Performer(inst_type,
                job.reduced_inst_num, inst_files)
            performer_prep.load_file(job.notes_filename)
            job.files = inst_files
            job.notes = list(performer_prep.style.notes)
            job.audio_filename = performer_prep.audio_filename
            job.mpl_filenames = []
            for st in range(4):
                mpl_filename = inst_files.get_mpl_filename(st)
                job.mpl_filenames.append(mpl_filename)
            total_steps += shared.thread_pool.add_task(job)
        return total_steps

    def perform_thread(self):
        self.performer.play_music()

    def play_music(self):
        self.state = state.RENDER_MUSIC
        self.condition.wakeOne()

    # TODO: used for video generation, but I'm feeling icky
    # about this.
    def get_duration(self):
        return self.performer.get_duration()

