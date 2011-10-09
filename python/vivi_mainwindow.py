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

#import utils
import shared

import string_train_all

#import lily
import score_widget

import performer_feeder

#import examine_note_widget

import movie


import os
import time


class ViviMainwindow(QtGui.QMainWindow):
    """ Main window of Vivi, the Virtual Violinist. """
    def __init__(self,
            training_dirname, cache_dirname, final_dirname,
            ly_filename, skill, always_lilypond,
            instrument_number):
        self.app = QtGui.QApplication([])
        QtGui.QMainWindow.__init__(self)
        shared.instrument_number = instrument_number

        ## setup main gui
        self.ui = vivi_mainwindow_gui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        ## setup progresss window
        self.prod = QtGui.QDialog(self)
        self.prod.setWindowTitle("Vivi calculations")
        self.prod.setWindowModality(QtCore.Qt.ApplicationModal)
        vbox = QtGui.QVBoxLayout()
        self.prod.setLayout(vbox)
        self.prod.label = QtGui.QLabel()
        self.prod.progress = QtGui.QProgressBar()
        vbox.addWidget(self.prod.label)
        vbox.addWidget(self.prod.progress)
        self.process_value = 0

        ## setup shared
        dirs.files = dirs.ViviDirs(
            training_dirname, cache_dirname, final_dirname)
        shared.judge = shared.judge_audio_widget.JudgeAudioWidget(
            self.ui.verticalLayout)
        shared.examine_main = shared.examine_note_widget.ExamineNoteWidget(
            shared.examine_note_widget.PLOT_MAIN)
            #shared.examine_note_widget.PLOT_STABLE)
        shared.examine_main.new_examine_note()
        shared.examine_main.plot_actions.setMinimumHeight(100)
        shared.examine_main.plot_actions.highlight(True)
        self.ui.verticalLayout.addWidget(shared.examine_main.plot_actions)

        ## setup other shared stuff
        #shared.perform = shared.performer.Performer()
#        shared.compare = shared.compare_coll.CompareColl()
#
#        shared.listen = [[]]*4
#
#        shared.ability = shared.skill.Skill(skill)

        ## setup training
        self.string_train = string_train_all.StringTrainAll(
            self.ui.string_train_layout)
        #self.string_train.set_note_label(self.ui.note_label)

        self.string_train.process_step.connect(self.process_step)
#        shared.compare.set_string_train(self.string_train)


        ## setup actions?
        self.ui.actionSave_training.triggered.connect(
            self.save_training)
        self.ui.actionBasic_training.triggered.connect(self.basic_training)

        self.ui.actionCompute.triggered.connect(self.compute)
        self.ui.actionCheck_accuracy.triggered.connect(self.train_check)
        self.ui.actionVerify.triggered.connect(self.verify)

        self.ui.actionLearn_attacks.triggered.connect(self.learn_attacks)
        self.ui.actionLearn_stable.triggered.connect(self.learn_stable)
        self.ui.actionLearn_dampen.triggered.connect(self.learn_dampen)


        self.ui.action_Open_ly_file.triggered.connect(self.open_ly_file)
        self.ui.actionQuick_preview.triggered.connect(self.quick_preview)
        self.ui.actionWatch.triggered.connect(self.watch)
        self.ui.actionGenerate_video.triggered.connect(self.generate_video)
        self.ui.actionEnjoy_video.triggered.connect(self.enjoy_video)



#        self.setup_training()
        self.setup_music()
        self.always_lilypond = always_lilypond
#
#        self.only_one = False
#        if ly_filename:
#            self.only_one = True
#            self.open_ly_file(ly_filename)





    def setup_music(self):
        shared.lily = shared.lilypond_compile.LilyPondCompile()
        shared.lily.process_step.connect(self.process_step)
        shared.lily.done.connect(self.finished_ly_compile)

        self.score = score_widget.ScoreWidget(self.ui.score_scroll_area)
        self.score.note_click.connect(self.select_note)

        shared.music = shared.music_events.MusicEvents()

#        self.examine = examine_note_widget.ExamineNoteWidget(
#            self.ui.note_layout)
#
        self.ui.actionRehearse.triggered.connect(self.rehearse)
        self.ui.actionListen.triggered.connect(self.play)
        self.performer_feeder = performer_feeder.PerformerFeeder()
        self.performer_feeder.process_step.connect(self.process_step)
        self.performer_feeder.done.connect(self.rehearse_done)

        self.movie = movie.ViviMovie()
        self.movie.process_step.connect(self.process_step)

    def basic_training(self):
        self.string_train.basic_train()








######################### old stuffs

    def load_ly_file(self, ly_filename):
        dirs.files.set_ly_basename(ly_filename)
        if shared.lily.lily_file_needs_compile():
            self.progress_dialog("Generating score", 2)
            shared.lily.call_lilypond()
        elif self.always_lilypond:
            print "Generating lilypond",
            shared.lily.call_lilypond()
        else:
            self.finished_ly_compile()

    def finished_ly_compile(self):
        self.score.load_file(dirs.files.get_ly_extra(".pdf"))
        dirs.files.set_notes_from_ly()

    def save_training(self):
        self.string_train.save()


    def progress_dialog(self, text, maximum):
        self.prod.label.setText(text)
        self.prod.progress.setMaximum(maximum)
        self.process_value = 0
        self.prod.progress.setValue(self.process_value)
        self.prod.show()

    def process_step(self):
        self.process_value += 1
        if self.process_value == self.prod.progress.maximum():
            self.prod.hide()
        else:
            self.prod.progress.setValue(self.process_value)

    def needs_basic(self):
        # TODO: is this debug only, or permanent?
        return False
        if self.string_train.get_basic_train_level() < 1:
            QtGui.QMessageBox.warning(self,
                "Vivi error",
                "Vivi needs more basic training first!",    
                QtGui.QMessageBox.Close)
            return True
        return False

    def compute(self):
        self.save_training()
        if self.needs_basic():
            return
        steps = self.string_train.compute_training()
        if steps == 0:
            return
        self.progress_dialog("Computing training files", steps)

    def rehearse(self):
        self.save_training()
        wavfiles = []
        for i in range(len(dirs.files.notes_all)):
            dirs.files.set_notes_index(i)
            self.performer_feeder.set_instrument(shared.instrument_number+i)
            self.performer_feeder.load_file(
                dirs.files.get_notes() )
            steps = self.performer_feeder.play_music()
            self.progress_dialog("Rehearsing music", steps)
            # FIXME: oh god ick, total hack
            while self.performer_feeder.state != performer_feeder.STATE_NULL:
                time.sleep(0.1)
        num_parts = len(dirs.files.notes_all)
        if num_parts > 1:
            # mixing
            cmd = "ecasound "
            for i in range(num_parts):
                dirs.files.set_notes_index(i)
                wav_filename = dirs.files.get_notes_ext(".wav")

                #pan = int(100*i / (num_parts-1))
                pan = int(100*(i+1) / (num_parts+1))
                print pan
                cmd += "-a:%i %s -erc:1,2 -epp:%i " % (
                    i, wav_filename, pan)
            mixed_filename = dirs.files.get_notes_ext(".wav")
            mixed_filename = mixed_filename.replace(".wav", "-mixed.wav")
            cmd += "-a:all -o %s" % (mixed_filename)
            os.system(cmd)
            self.performer_feeder.load_wav(mixed_filename[:-4])
            self.mixed_filename = mixed_filename


    def rehearse_done(self):
        pass
        #print "rehearse done"
#        if self.only_one:
#            self.app.quit()
#        else:
#            self.examine.load_file(self.ly_basename)

#        self.progress_dialog("Rehearsing piece", 4)
#        self.process_step()
#        self.app.processEvents()
#        cmd = './vivi_play.py ly/basic-scale.ly'
#        os.system(cmd)
#        self.process_step()
#        self.examine.load_file(self.ly_basename)
#        self.prod.hide()


    def play(self):
        self.performer_feeder.play()

    def select_note(self, lily_line, lily_col):
        filename = dirs.files.get_ly_extra("")
        import glob
        filename = glob.glob(filename+'*.actions')[0]
        filename = filename[:-8]
        shared.examine_main.load_file(filename)
        #pnc_text = "point_and_click %i %i" % (lily_line, lily_col)
        pnc_text = "point_and_click %i %i" % (lily_col, lily_line)
        if shared.examine_main.load_note(pnc_text):
            shared.examine_main.play()
        else:
            print "no note found:", pnc_text

        #self.string_train.set_note_label(self.ui.note_label)
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
#        self.string_train.select(st, lvl)
        #self.examine.show_note_info()
#        self.examine.play()

    def train_note(self):
        train_list = self.examine.examine_note.get_train_list()
        level = self.examine.examine_note.level
        self.string_train.train_note(train_list, level)

    def train_zoom(self):
        st, level, filename = shared.examine_main.get_zoom()
        self.string_train.train_zoom(st, level, filename)

    def train_check(self):
        self.save_training()
        steps = self.string_train.check_accuracy()
        if steps == 0:
            return
        self.progress_dialog("Checking accuracy", steps)

    def verify(self):
        self.save_training()
        steps = self.string_train.verify()
        if steps == 0:
            return
        self.progress_dialog("Verify", steps)

    def learn_attacks(self):
        steps = self.string_train.learn_attacks()
        if steps == 0:
            return
        self.progress_dialog("Learning attacks", steps)

    def learn_stable(self):
        steps = self.string_train.learn_stable()
        if steps == 0:
            return
        self.progress_dialog("Learning stable", steps)

    def learn_dampen(self):
        steps = self.string_train.learn_dampen()
        if steps == 0:
            return
        self.progress_dialog("Learning dampen", steps)

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
        #print "generate low-quality preview video"
        self.movie.end_time = self.performer_feeder.get_duration()
        for i in range(len(dirs.files.notes_all)):
            dirs.files.set_notes_index(i)
            steps = self.movie.generate_preview()
            self.progress_dialog("Generating movie", steps)
            # FIXME: oh god ick, total hack
            while self.movie.state != 0:
                time.sleep(0.1)
        num_parts = len(dirs.files.notes_all)
        if num_parts > 1:
            self.movie.mix(self.mixed_filename)

    def generate_video(self):
        #print "generate high-quality video"
        self.movie.end_time = self.performer_feeder.get_duration()
        steps = self.movie.generate_movie()
        self.progress_dialog("Generating movie", steps)

    def watch(self):
        steps = self.movie.watch_preview()
        self.progress_dialog("Watching movie", steps)

    def enjoy_video(self):
        steps = self.movie.watch_movie()
        self.progress_dialog("Watching movie", steps)


    def set_modified(self):
        self.string_train.set_modified()

    def close(self):
        self.save_training()
        # TODO: workaround for some weird python invisible bug
        #import os
        #os.system("reset")
        self.app.quit()

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
        elif key == 't':
            self.train_note()
        elif key == 'z':
            self.train_zoom()
        elif key == 'y':
            self.open_ly_file('ly/example-input.ly')
        elif key == 'i':
            self.open_ly_file('ly/basic/scale-combo.ly')
        elif key == 'u':
            self.open_ly_file('ly/black-box.ly')
        elif key == 'm':
            self.set_modified()
        else:
            QtGui.QMainWindow.keyPressEvent(self, event)

