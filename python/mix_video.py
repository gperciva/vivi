#!/usr/bin/env python

from PyQt4 import QtCore

import state

import utils
import dirs

import glob
import os
import subprocess
FPS = 25

# one buffer of impulse reponse?
EXTRA_DELAY_BODY_RESPONSE = -2048.0 / 22050.0
DELAY_MOVIE_START_SECONDS = 0.5 + EXTRA_DELAY_BODY_RESPONSE
DELAY_MOVIE_END_SECONDS = 0.5 + EXTRA_DELAY_BODY_RESPONSE
TMP_MOVIE_DIR = '/tmp/vivi-cache/movie/'

class MixVideo(QtCore.QThread):
    process_step = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QThread.__init__(self)

        self.audio_filename = None

        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
        self.state = state.State()
        self.start()

    def run(self):
        while True:
            self.mutex.lock()
            self.condition.wait(self.mutex)
            if self.state == state.PLAYING_MOVIE:
                self.watch_movie_thread()
            self.state = state.IDLE
            self.mutex.unlock()

    def watch_movie_thread(self):
        #os.system("mplayer blender/violin-1.avi")
#        if self.preview:
#            movie_filename = "vivi-preview.avi"
#        else:
#            movie_filename = "vivi-movie.avi"
        os.system("mplayer -really-quiet %s" % (
            self.movie_filename))
        self.process_step.emit()


    def watch_preview(self):
        self.job(vivi_defines.TASK_PLAY_VIDEO_PREVIEW, "Playing video")

    def play(self):
        self.state = state.PLAYING_MOVIE
        self.condition.wakeOne()

    def play_video(self):
        #utils.play(self.audio_filename)
        pass

    def make_movie_audio_file(self, audio_filename):
        movie_audio_filename = audio_filename.replace(".wav", ".movie.wav")
        cmd = "sox %s %s delay %f %f pad 0 %f" % (
            audio_filename, movie_audio_filename,
            DELAY_MOVIE_START_SECONDS,
            DELAY_MOVIE_START_SECONDS,
            DELAY_MOVIE_END_SECONDS)
        os.system(cmd)
        return movie_audio_filename

    def mix(self, audio_filename):
        movie_audio_filename = self.make_movie_audio_file(
            audio_filename)
        # make combo images
        DIR = "/tmp/vivi-cache/movie/"
        filenames = glob.glob(DIR+"1/*.tga")
        for filename in filenames:
                other = filename.replace("/1/", "/2/")
                cmd = "convert %s %s +append %s" % (
                    filename, other,
                    DIR+os.path.basename(filename))
                os.system(cmd)
        # actual mix
        self.movie_filename = os.path.join(
            TMP_MOVIE_DIR, "vivi-mix-preview.avi")
        logfile = TMP_MOVIE_DIR+"mix-mencoder.log"
        cmd = """artifastring_movie.py \
-o %s -i %s --fps %i -l %s %s""" % (
            self.movie_filename,
            TMP_MOVIE_DIR, FPS,
            logfile,
            movie_audio_filename)
        print cmd
        os.system(cmd)


