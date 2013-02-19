#!/usr/bin/env python
import os
import shutil
from PyQt4 import QtCore

import glob
import dirs

GENERATE_MOVIE = 1
WATCH_MOVIE = 2

IMAGE_THREAD_STEPS = 4
FPS = 25

# one buffer of impulse reponse?
EXTRA_DELAY_BODY_RESPONSE = 2048.0 / 22050.0
DELAY_MOVIE_START_SECONDS = 0.5 + EXTRA_DELAY_BODY_RESPONSE
DELAY_MOVIE_END_SECONDS = 0.5 + EXTRA_DELAY_BODY_RESPONSE

TMP_MOVIE_DIR = '/tmp/vivi-cache/movie/'

# used inside ViviMovie, below
class BlenderImages(QtCore.QThread):
    process_step = QtCore.pyqtSignal()
    def __init__(self, start_frame, end_frame, logfile_num, quality, actions_filename):
        QtCore.QThread.__init__(self)
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.logfile_num = logfile_num
        self.quality = quality
        self.actions_filename = actions_filename
        if "1" in actions_filename:
            self.movie_dir = TMP_MOVIE_DIR+"1/"
        elif "2" in actions_filename:
            self.movie_dir = TMP_MOVIE_DIR+"2/"
        else:
            self.movie_dir = TMP_MOVIE_DIR+"3/"
        if not os.path.exists(self.movie_dir):
            os.makedirs(self.movie_dir)

    def run(self):
        step = int((self.end_frame-self.start_frame)
            / IMAGE_THREAD_STEPS)
        for i in range(IMAGE_THREAD_STEPS):
            my_start = self.start_frame + i*step
            if i < IMAGE_THREAD_STEPS - 1:
                my_end = self.start_frame + (i+1)*step-1
            else:
                my_end = self.end_frame
            log_filename = "render-%i-%i.log" % (self.logfile_num, i)
            cmd = """actions2images.py -o %s \
-s %i -e %i --fps %i -q %i -l %s %s""" % (self.movie_dir,
my_start, my_end, FPS, self.quality, log_filename, self.actions_filename)
            os.system(cmd)
            self.process_step.emit()

class ViviMovie(QtCore.QThread):
    process_step = QtCore.pyqtSignal()
    done = QtCore.pyqtSignal()
    def __init__(self):
        QtCore.QThread.__init__(self)

        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
        self.state = 0
        self.start()
        self.end_time = 0.0

        # not thread-safe!
        if not os.path.isdir(TMP_MOVIE_DIR):
            os.mkdir(TMP_MOVIE_DIR)
#        map(os.remove,
#            glob.glob(os.path.join(TMP_MOVIE_DIR, '*.tga')) +
#            glob.glob(os.path.join(TMP_MOVIE_DIR, '*.log')))

    def run(self):
        while True:
            self.mutex.lock()
            self.condition.wait(self.mutex)
            if self.state == GENERATE_MOVIE:
                self.generate_movie_thread()
            if self.state == WATCH_MOVIE:
                self.watch_movie_thread()
            self.state = 0
            self.process_step.emit()
            self.mutex.unlock()

    def make_movie_actions_file(self, actions_filename):
        actions_lines = open(actions_filename).readlines()
        movie_actions_filename = actions_filename.replace(".actions",
            ".movie.actions")
        movie_actions_file = open(movie_actions_filename, "w")
        last_time = 0.0
        for line in actions_lines:
            if line[0] != '#':
                splitline = line.split('\t')
                seconds = float(splitline[1])
                seconds += DELAY_MOVIE_START_SECONDS
                last_time = seconds
                splitline[1] = str("%f"%seconds)
                line = '\t'.join(splitline)
                if len(splitline) == 2:
                    line += '\n'
            movie_actions_file.write(line)
        last_time += DELAY_MOVIE_END_SECONDS
        movie_actions_file.write(str("w\t%f\n"%last_time))
        movie_actions_file.close()
        return movie_actions_filename

    def generate_movie(self):
        self.quality = 1
        self.state = GENERATE_MOVIE

        #map(os.remove,
        #    glob.glob(os.path.join(basename + '*.movie.actions')))
        self.audio_filename = dirs.files.get_notes_last("*.wav")
        self.actions_filename = self.make_movie_actions_file(
            dirs.files.get_notes_last("*.actions"))

        self.condition.wakeOne()
        return 4*IMAGE_THREAD_STEPS + 1

    def generate_preview_steps (self, notes_last_filename):
        self.quality = 0
        self.audio_filename = notes_last_filename
        self.actions_filename = self.make_movie_actions_file(
            notes_last_filename.replace(".wav", ".actions"))
        return 4*IMAGE_THREAD_STEPS + 1

    def generate_preview(self):
        self.state = GENERATE_MOVIE
        self.condition.wakeOne()

    def generate_movie_thread(self):
        print "generate movie thread"
#        if os.path.isdir(TMP_MOVIE_DIR):
#            shutil.rmtree(TMP_MOVIE_DIR)
#
#        shutil.copyfile("ly/violin-1.actions",
#            "blender/violin-1.actions")
#        shutil.copyfile(
#            self.ly_filename.replace('.ly', '.wav'),
#            "blender/violin-1.wav")
#        os.chdir("blender")
        self.process_step.emit()

        end_time_delayed = (self.end_time
            + DELAY_MOVIE_START_SECONDS + DELAY_MOVIE_END_SECONDS)
        end_frame = int(end_time_delayed * FPS) + 1
        blender_images = []
        step = end_frame/4
        for i in range(4):
            blend_start = i*step + 1
            if i < 3:
                blend_end = (i+1)*step
            else:
                blend_end = end_frame
            blender_images.append( BlenderImages(
                blend_start, blend_end, i, self.quality,
                self.actions_filename))
            blender_images[i].process_step.connect(
                self.process_step_emit)
            blender_images[i].start()
        for i in range(4):
            blender_images[i].wait()

        return
        movie_audio_filename = self.make_movie_audio_file(
            self.audio_filename)

#        os.system("lame violin-1-delay.wav")
        self.process_step.emit()

        if self.quality == 0:
            movie_filename = "vivi-preview.avi"
        else:
            movie_filename = "vivi-movie.avi"
        logfile = TMP_MOVIE_DIR+"mencoder.log"
        cmd = """artifastring_movie.py \
-o %s -i %s --fps %i -l %s %s""" % (TMP_MOVIE_DIR+movie_filename,
            TMP_MOVIE_DIR, FPS,
            logfile,
            movie_audio_filename)
        os.system(cmd)
        self.process_step.emit()

        self.done.emit()

    def watch_movie(self):
        self.state = WATCH_MOVIE
        self.preview = False
        self.condition.wakeOne()
        return 1

    def watch_preview(self):
        self.state = WATCH_MOVIE
        self.preview = True
        self.condition.wakeOne()
        return 1

    def watch_movie_thread(self):
        #os.system("mplayer blender/violin-1.avi")
        if self.preview:
            movie_filename = "vivi-preview.avi"
        else:
            movie_filename = "vivi-movie.avi"
        os.system("mplayer -really-quiet %s" % (TMP_MOVIE_DIR+movie_filename))
        self.process_step.emit()

        self.done.emit()

    def process_step_emit(self):
        self.process_step.emit()

