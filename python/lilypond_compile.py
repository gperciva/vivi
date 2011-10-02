#!/usr/bin/env python
import os
import shutil
import glob
from PyQt4 import QtCore

import subprocess
import filecmp

import dirs

STATE_COMPILE_LILYPOND = 1
LILYPOND_COMMAND = "lilypond \
  -I %s \
  -dinclude-settings=event-listener.ly \
  -o %s \
  %s"
#  -dinclude-settings=reduce-whitespace.ly \

class LilyPondCompile(QtCore.QThread):
    process_step = QtCore.pyqtSignal()
    done = QtCore.pyqtSignal()
    def __init__(self):
        QtCore.QThread.__init__(self)

        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
        self.state = 0
        self.start()

    def run(self):
        while True:
            self.mutex.lock()
            self.condition.wait(self.mutex)
            if self.state == STATE_COMPILE_LILYPOND:
                self.call_lilypond_thread()
            self.mutex.unlock()

    def call_lilypond(self):
        self.state = STATE_COMPILE_LILYPOND
        self.condition.wakeOne()
        return 2

    def lily_file_needs_compile(self):
        self.ly_basename = dirs.files.get_ly_extra()
        self.ly_filename = dirs.files.get_ly_extra(".ly")
        ly_original = dirs.files.get_ly_original()
        self.ly_include_dir = os.path.abspath(
            os.path.dirname(ly_original))

        self.pdf_dirname = os.path.dirname(dirs.files.get_ly_extra(".pdf"))
        if not os.path.isdir(self.pdf_dirname):
            os.makedirs(self.pdf_dirname)
        if (os.path.isfile(self.ly_filename) and
            filecmp.cmp(ly_original, self.ly_filename)):
            return False
        shutil.copy(ly_original, self.ly_filename)
        return True

    def remove_old_files(self, basename):
        for extension in ['*.notes', '*.pdf', '*.midi', '*.log']:
            map(os.remove,
                glob.glob(basename+extension))

    def call_lilypond_thread(self):
        self.remove_old_files(self.ly_basename)
        self.process_step.emit()

        logfile = open(self.ly_basename+'.log', 'w')
        # make new files
        cmd = LILYPOND_COMMAND % (
            self.ly_include_dir,
            self.pdf_dirname,
            self.ly_filename)
        cmd = cmd.split()
        p = subprocess.Popen(cmd, stdout=logfile,
            stderr=logfile)
        p.wait()
        logfile.close()
        
        self.process_step.emit()
        self.done.emit()

