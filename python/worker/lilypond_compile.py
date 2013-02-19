#!/usr/bin/env python

import subprocess

LILYPOND_COMMAND = "lilypond \
  -I %s \
  -dinclude-settings=event-listener.ly \
  -dpoint-and-click=note-event \
  -o %s \
  %s"
#  -dinclude-settings=reduce-whitespace.ly \

def get_steps(job):
    return 2

def calculate(job, process_step):
    logfile = open(job.ly_basename+'.log', 'w')
    # make new files
    cmd = LILYPOND_COMMAND % (
        job.ly_include_dir,
        job.pdf_dirname,
        job.ly_filename)
    #print cmd
    cmd = cmd.split()
    process_step.emit()
    p = subprocess.Popen(cmd, stdout=logfile, stderr=logfile)
    p.wait()
    logfile.close()
    process_step.emit()
    return job
    

