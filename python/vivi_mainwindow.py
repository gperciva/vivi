#!/usr/bin/env python
""" Main window of Vivi, the Virtual Violinist. """

# FIXME: to avoid the dreaded
#   [MRSERR] MarControl::to() -  Incompatible type requested -
#   expected mrs_string for control  mrs_string/currentlyPlaying
# I have to import vivi_controller here for some unknown reason!
import vivi_controller

#import os
import dirs

from PyQt4 import QtGui, QtCore
import vivi_mainwindow_gui

import vivi_defines
import shared

import string_instrument

import lilypond_prepare

import score_widget

import instrument_numbers

import performer_feeder

import worker.thread_pool

import movie_prep

import state

import hill_prep
import mix_hill_prep

import mix_audio_prep
import mix_video_prep

import os
import time


class ViviMainwindow(QtGui.QMainWindow):
    """ Main window of Vivi, the Virtual Violinist. """
    def __init__(self,
            training_dirname, cache_dirname, final_dirname,
            ly_filename, skill, always_lilypond):
        self.app = QtGui.QApplication([])
        QtGui.QMainWindow.__init__(self)

        ## setup main gui
        self.ui = vivi_mainwindow_gui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        ## setup progresss window
        #self.prod = QtGui.QDialog(self)
        #self.prod.setWindowTitle("Vivi calculations")
        #self.prod.setWindowModality(QtCore.Qt.ApplicationModal)
        #vbox = QtGui.QVBoxLayout()
        #self.prod.setLayout(vbox)
        #self.prod.label = QtGui.QLabel()
        #self.prod.progress = QtGui.QProgressBar()
        #vbox.addWidget(self.prod.label)
        #vbox.addWidget(self.prod.progress)
        #self.process_value = 0

        ## setup shared
        self.files = dirs.ViviDirs(
            training_dirname, cache_dirname, final_dirname)

        shared.thread_pool = worker.thread_pool.ThreadPool()
        self.thread_pool_results_queue = shared.thread_pool.get_results_queue()
        shared.thread_pool.process_step.connect(self.process_step)
        shared.thread_pool.done_task.connect(self.done_task)

        #shared.judge = shared.judge_audio_widget.JudgeAudioWidget(
        #    self.ui.verticalLayout)
        shared.examine_main = shared.examine_note_widget.ExamineNoteWidget(
            shared.examine_note_widget.PLOT_MAIN)
            #shared.examine_note_widget.PLOT_STABLE)
        shared.examine_main.new_examine_note()
        shared.examine_main.plot_actions.setMinimumHeight(100)
        shared.examine_main.plot_actions.highlight(True)
        self.ui.verticalLayout.insertWidget(
            1,
            shared.examine_main.plot_actions)

        ## setup other shared stuff
        #shared.perform = shared.performer.Performer()
#        shared.compare = shared.compare_coll.CompareColl()
#
#        shared.listen = [[]]*4
#
        shared.skill = skill

        ## setup instruments
        self.instruments = []
        colls = None
        for i, inst_name in enumerate(instrument_numbers.INSTRUMENT_NAMES):
            #print i, inst
            tab = self.ui.tabWidget.widget(i)
            #inst_num = instrument_numbers.DISTINCT_INSTRUMENT_NUMBERS[i]
            inst = string_instrument.StringInstrument(
                tab.layout(),
                i, inst_name,
                training_dirname, cache_dirname, final_dirname,
                self.ui.judge_layout, colls)
            self.instruments.append(inst)
            if i in [0, 5, 7]:
                colls = inst.get_colls()
            if i in [4, 6]:
                colls = None
        #self.string_instrument.set_note_label(self.ui.note_label)
        self.string_instrument = self.instruments[0]
        self.ui.tabWidget.currentChanged.connect(self.tab_changed)

        ## setup actions?
        self.ui.actionSave_training.triggered.connect(
            self.save_training)
        self.ui.actionBasic_training.triggered.connect(self.basic_training)

        # string stuff
        self.ui.actionCompute.triggered.connect(self.calculate_training)
        self.ui.actionCheck_accuracy.triggered.connect(self.calculate_accuracy)

        # dyn stuff
        self.ui.actionVerify.triggered.connect(self.calculate_verify)
        self.ui.actionLearn_stable.triggered.connect(self.calculate_stable)
        self.ui.actionLearn_attacks.triggered.connect(self.calculate_attack)
        self.ui.actionLearn_dampen.triggered.connect(self.calculate_dampen)


        self.ui.action_Open_ly_file.triggered.connect(self.open_ly_file)
        self.ui.actionQuick_preview.triggered.connect(self.quick_preview)
        self.ui.actionWatch.triggered.connect(self.watch)
        self.ui.actionGenerate_video.triggered.connect(self.generate_video)
        self.ui.actionEnjoy_video.triggered.connect(self.enjoy_video)
        self.ui.actionHill_climbing.triggered.connect(self.hill)


        self.progressBar = QtGui.QProgressBar()
        self.ui.statusBar.addPermanentWidget(self.progressBar)
        self.progressBar.hide()

#        self.setup_training()
        self.setup_sheet_music()
        self.always_lilypond = always_lilypond

#
#        self.only_one = False
#        if ly_filename:
#            self.only_one = True
#            self.open_ly_file(ly_filename)

        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget.setCurrentIndex(0)

        self.waiting_tasks = {}



    def setup_sheet_music(self):
        self.score = score_widget.ScoreWidget()
        self.ui.score_scroll_area.setWidget(self.score)
        self.ui.score_scroll_area.setMinimumHeight(100)
        #print self.ui.score_scroll_area.sizeHint()

#        self.score = score_widget.ScoreWidget(
#            self.ui.tabWidget.widget(
#                self.ui.tabWidget.count()-1).layout())
        self.score.note_click.connect(self.select_note)

        shared.music = shared.music_events.MusicEvents()
        #self.examine = examine_note_widget.ExamineNoteWidget(
        #    self.ui.note_layout)

        self.ui.actionRehearse.triggered.connect(self.rehearse)
        self.ui.actionListen.triggered.connect(self.play)
        self.performer_feeder = None

        self.movies = []


    def basic_training(self):
        self.string_instrument.basic_train()

    ### bulk processing state
    def process_step(self):
        self.process_value += 1
        #self.prod.progress.setValue(self.process_value)
        self.progressBar.setValue(self.process_value)
        #if self.prod.progress.maximum() == self.process_value:
        #    self.prod.hide()

######################### old stuffs

    def load_ly_file(self, ly_filename):
        self.files.set_ly_basename(ly_filename)
        if lilypond_prepare.lily_file_needs_compile(self.files) or self.always_lilypond:
            self.job(vivi_defines.TASK_LILYPOND, "Compiling LilyPond score")
        else:
            self.finished_ly_compile()

    def finished_ly_compile(self):
        self.score.load_file(self.files.get_ly_extra(".pdf"))
        self.files.set_notes_from_ly()
        notes_filenames = self.files.get_notes_files()
        self.pncs = {}
        for note_filename in notes_filenames:
            pncs = []
            lines = open(note_filename).readlines()
            for line in lines:
                pnc_index = line.find("point-and-click")
                if pnc_index >= 0:
                    pnc = line[pnc_index+16:].strip()
                    pncs.append(pnc)
            self.pncs[note_filename] = pncs

    def save_training(self):
        for inst in self.instruments:
            inst.save()


    def progress_dialog(self, text, maximum):
        self.process_value = 0

        #self.prod.label.setText(text)
        #self.prod.progress.setMaximum(maximum)
        #self.prod.progress.setValue(self.process_value)

        self.ui.statusBar.showMessage(text)
        self.progressBar.setMaximum(maximum)
        self.progressBar.setValue(self.process_value)
        self.progressBar.show()

    def needs_basic(self):
        # TODO: is this debug only, or permanent?
        return False
        if self.string_instrument.get_basic_train_level() < 1:
            QtGui.QMessageBox.warning(self,
                "Vivi error",
                "Vivi needs more basic training first!",    
                QtGui.QMessageBox.Close)
            return True
        return False

    def job(self, job_type, text):
        if job_type in state.STRING_JOBS or job_type in state.DYN_JOBS:
            steps = self.string_instrument.start_job(job_type)
        elif job_type is vivi_defines.TASK_LILYPOND:
            steps = lilypond_prepare.start_job(self.files)
        elif job_type is vivi_defines.TASK_RENDER_AUDIO:
            steps = self.performer_feeder.start_job(self.get_instrument_files)
            self.waiting_tasks[job_type] = self.performer_feeder.num_audio_files
        elif job_type is vivi_defines.TASK_MIX_AUDIO:
            raise Exception("TASK_MIX_AUDIO should be started automatically")
        elif job_type is vivi_defines.TASK_HILL_CLIMBING:
            steps = hill_prep.start_job(self.files, self.get_instrument_files)
            self.waiting_tasks[job_type] = hill_prep.get_num_jobs()
        elif job_type is vivi_defines.TASK_PLAY_AUDIO:
            job = state.Job(job_type)
            job.audio_filename = self.files.get_ly_extra("-all.wav")
            steps = shared.thread_pool.add_task(job)
        elif job_type is vivi_defines.TASK_RENDER_VIDEO_PREVIEW:
            steps = movie_prep.start_job(self.files)
            self.waiting_tasks[job_type] = (
                self.performer_feeder.num_audio_files *
                movie_prep.get_split_tasks())
        elif job_type is vivi_defines.TASK_MIX_VIDEO:
            raise Exception("TASK_MIX_VIDEO should be started automatically")
        elif job_type is vivi_defines.TASK_PLAY_VIDEO_PREVIEW:
            job = state.Job(job_type)
            job.movie_filename = self.files.get_ly_movie_preview()
            steps = shared.thread_pool.add_task(job)
        elif job_type is vivi_defines.TASK_RENDER_VIDEO:
            steps = movie_prep.start_job(self.files, 1)
            self.waiting_tasks[job_type] = (
                self.performer_feeder.num_audio_files *
                movie_prep.get_split_tasks())
        elif job_type is vivi_defines.TASK_PLAY_VIDEO:
            job = state.Job(job_type)
            job.movie_filename = self.files.get_ly_movie()
            steps = shared.thread_pool.add_task(job)
        else:
            raise Exception("Main window: unknown job type")
        if steps > 0:
            self.progress_dialog(text, steps)


    def rehearse(self):
        if not self.performer_feeder:
            self.performer_feeder = performer_feeder.PerformerFeeder(self.files)
        self.job(vivi_defines.TASK_RENDER_AUDIO, "Rendering audio")

    def rehearse_done(self):
        pass

    def play(self):
        self.job(vivi_defines.TASK_PLAY_AUDIO, "Playing music")

    def select_note(self, lily_line, lily_col):
        notes_filename = None
        search = "%i %i" % (lily_col, lily_line)
        for filename, values in self.pncs.iteritems():
            # don't bother breaking out of this; it's fast enough
            for val in values:
                if val == search:
                    notes_filename = filename[:-6]
        if notes_filename is None:
            return
        shared.examine_main.load_file(notes_filename, self.files)
        #pnc_text = "point_and_click %i %i" % (lily_line, lily_col)
        pnc_text = "point_and_click %i %i" % (lily_col, lily_line)
        if shared.examine_main.load_note(pnc_text):
            shared.examine_main.play()
        else:
            print "no note found:", pnc_text

        #self.string_instrument.set_note_label(self.ui.note_label)
#        status = self.examine.load_note(lily_line, lily_col)
#        if not status:
            # done in examine (examine_note_widget) now!
#            QtGui.QMessageBox.warning(self,
#                "Vivi error",
#                "Vivi needs to rehearse music first!",    
#                QtGui.QMessageBox.Close)
#            return
#        st = self.examine.examine_note.note_st
#        lvl = self.examine.examine_note.level
#        self.string_instrument.select(st, lvl)
        #self.examine.show_note_info()
#        self.examine.play()

    #def train_note(self):
    #    train_list = self.examine.examine_note.get_train_list()
     #   level = self.examine.examine_note.level
     #   self.string_instrument.train_note(train_list, level)

    def train_zoom(self):
        st, level, filename, dist_inst_num = shared.examine_main.get_zoom()
        self.instruments[dist_inst_num].train_zoom(st, level, filename)

# string stuff
    def calculate_training(self):
        if self.needs_basic():
            return
        self.job(vivi_defines.TASK_TRAINING, "Computing training files")

    def calculate_accuracy(self):
        self.job(vivi_defines.TASK_ACCURACY, "Checking accuracy")

# dyn stuff
    def calculate_verify(self):
        self.job(vivi_defines.TASK_VERIFY, "Verifying stability")

    def calculate_stable(self):
        self.job(vivi_defines.TASK_STABLE, "Learning stable")

    def calculate_attack(self):
        self.job(vivi_defines.TASK_ATTACK, "Learning attacks")

    def calculate_dampen(self):
        self.job(vivi_defines.TASK_DAMPEN, "Learning dampen slur")

# other stuff


    def open_ly_file(self, ly_filename=None):
        if ly_filename:
            self.ly_filename = ly_filename
            self.load_ly_file(ly_filename)
            return
        ly_filename = QtGui.QFileDialog.getOpenFileName(
            None, "Open ly file", "ly/",
            "LilyPond input files (*.ly)")
        if ly_filename:
            self.ly_filename = str(ly_filename)
            self.load_ly_file(str(ly_filename))

    def quick_preview(self):
        self.job(vivi_defines.TASK_RENDER_VIDEO_PREVIEW, "generating preview video")

    def hill(self):
        self.job(vivi_defines.TASK_HILL_CLIMBING, "hill climbing")

    def generate_video(self):
        self.job(vivi_defines.TASK_RENDER_VIDEO, "generating main video")

    def watch(self):
        self.job(vivi_defines.TASK_PLAY_VIDEO_PREVIEW, "Playing video preview")

    def enjoy_video(self):
        self.job(vivi_defines.TASK_PLAY_VIDEO, "Playing main video")


    def tab_changed(self, index):
        if index < len(self.instruments):
            self.string_instrument = self.instruments[index]

    def set_modified(self, portion):
        self.string_instrument.set_modified(portion)

    def close(self):
        self.save_training()
        # TODO: workaround for some weird python invisible bug
        #import os
        #os.system("reset")
        self.app.quit()

    def get_instrument_files(self, index):
        return self.instruments[index].files

    def done_task(self):
        # must do before the render_audio test
        job = self.thread_pool_results_queue.get()
        if job.job_type in state.STRING_JOBS or job.job_type in state.DYN_JOBS:
            self.string_instrument.task_done(job)
        elif job.job_type is vivi_defines.TASK_LILYPOND:
            self.finished_ly_compile()
        elif job.job_type is vivi_defines.TASK_RENDER_AUDIO:
            self.waiting_tasks[job.job_type] -= 1
            if self.waiting_tasks[job.job_type] == 0:
                steps = mix_audio_prep.start_job(job.ly_basename)
                self.progress_dialog("Mixing audio", steps)
        elif job.job_type is vivi_defines.TASK_MIX_AUDIO:
            pass
        elif job.job_type is vivi_defines.TASK_PLAY_AUDIO:
            pass
        elif job.job_type is vivi_defines.TASK_HILL_CLIMBING:
            self.waiting_tasks[job.job_type] -= 1
            if self.waiting_tasks[job.job_type] == 0:
                steps = mix_hill_prep.start_job(self.files, self.get_instrument_files)
                self.progress_dialog("Deciding on a hill direction", steps)
        elif job.job_type is vivi_defines.TASK_MIX_HILL:
            pass
        elif job.job_type is vivi_defines.TASK_RENDER_VIDEO_PREVIEW:
            self.waiting_tasks[job.job_type] -= 1
            if self.waiting_tasks[job.job_type] == 0:
                steps = mix_video_prep.start_job(self.files,
                    job.quality)
                self.progress_dialog("Mixing video", steps)
        elif job.job_type is vivi_defines.TASK_PLAY_VIDEO_PREVIEW:
            pass
        elif job.job_type is vivi_defines.TASK_MIX_VIDEO:
            pass
        elif job.job_type is vivi_defines.TASK_RENDER_VIDEO:
            self.waiting_tasks[job.job_type] -= 1
            if self.waiting_tasks[job.job_type] == 0:
                steps = mix_video_prep.start_job(self.files,
                    job.quality)
                self.progress_dialog("Mixing video", steps)
        elif job.job_type is vivi_defines.TASK_PLAY_VIDEO:
            pass
        else:
            print "done other job"
        self.thread_pool_results_queue.task_done()
        if shared.thread_pool.all_tasks_finished():
            self.progressBar.hide()
            self.ui.statusBar.clearMessage()
            # TODO: maybe?
            #gc.collect()

    def keyPressEvent(self, event):
        try:
            key = chr(event.key())
        except:
            QtGui.QMainWindow.keyPressEvent(self, event)
            return
        key = key.lower()
        if key == 'q':
            self.close()
        elif (key == 'p'):
            shared.examine_main.play()
        #elif key == 't':
            #self.train_note()
        elif key == 'z':
            self.train_zoom()
        elif key == 'y':
            self.open_ly_file('ly/example-input.ly')
        elif key == 'i':
            #self.open_ly_file('ly/basic/scale-combo.ly')
            #self.open_ly_file('ly/basic-violin/scale-forte-2.ly')
            #self.open_ly_file('ly/basic-violin/scale-double-forte.ly')
            self.open_ly_file('ly/black-box-cello.ly')
            #self.open_ly_file('ly/bach-double.ly')
        elif key == 'u':
            self.open_ly_file('ly/black-box.ly')
        elif key == 'x':
            self.set_modified(1)
        elif key == 's':
            self.set_modified(2)
        elif key == 'm':
            self.set_modified(0)
        else:
            QtGui.QMainWindow.keyPressEvent(self, event)

