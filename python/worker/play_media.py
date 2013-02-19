#!/usr/bin/env python

import os

def get_steps(job):
    return -1

def play_audio(job, process_step):
    # play(1) uses 300% cpu to play a stereo file!
    cmd = "aplay -q %s" % job.audio_filename
    #print "render_audio:", cmd
    os.system(cmd)
    return job

def play_video(job, process_step):
    cmd = "mplayer -really-quiet %s" % job.movie_filename
    print cmd
    os.system(cmd)
    return job

