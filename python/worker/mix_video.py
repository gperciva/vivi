#!/usr/bin/env python

import os
import glob

import vivi_defines

FPS = 25

# one buffer of impulse reponse?
EXTRA_DELAY_BODY_RESPONSE = 2048.0 / 22050.0
DELAY_MOVIE_START_SECONDS = 0.5 + EXTRA_DELAY_BODY_RESPONSE
DELAY_MOVIE_END_SECONDS = 0.5 + EXTRA_DELAY_BODY_RESPONSE


def get_steps(job):
    #if len(job.parts_dirnames) == 1:
    #    return 2
    return 4

def calculate(job, process_step):
    process_step.emit()
    movie_audio_filename = make_movie_audio_file(job.mixed_audio_filename)
    process_step.emit()

    if len(job.parts_dirnames) > 1:
        make_combo_images(job.parts_dirnames, job.images_dirname)
    process_step.emit()

    logfile = os.path.splitext(movie_audio_filename)[0] + ".log"
    cmd = """artifastring_movie.py \
-o %s -i %s --fps %i -l %s %s""" % (job.movie_filename,
        job.images_dirname,
        FPS,
        logfile,
        movie_audio_filename)
    #print cmd
    os.system(cmd)
    process_step.emit()
    return job

def imagemagick_image_string(name, filename):
    cmd = ""
    cmd += " '(' %s -fill white -undercolor black " % (filename)
    cmd += " -gravity northwest "
    cmd += " -annotate +10+10 ' %s ' ')' " % (name)
    return cmd

def imagemagick_horizontal_string(image_one, image_two):
    cmd = " '(' %s %s +append ')' " % (image_one, image_two)
    return cmd

def imagemagick_vertical_string(image_one, image_two):
    cmd = " '(' %s %s -gravity center -append ')' " % (image_one, image_two)
    return cmd

def make_combo_images(parts_dirnames, combo_dirname):
# TODO: simplify
    if len(parts_dirnames) == 2:
        one = parts_dirnames[0]
        two = parts_dirnames[1]
        # ASSUME: we have the same number of files in all dirs
        filenames = glob.glob(os.path.join(one, "*.tga"))
        for one_filename in filenames:
            cmd = "convert "
            two_filename = one_filename.replace(one, two)
            names = [ get_name(filename) for filename in [one_filename, two_filename]]
            cmd += imagemagick_horizontal_string(
                imagemagick_image_string(names[0], one_filename),
                imagemagick_image_string(names[1], two_filename)
                )
            dest = os.path.join(combo_dirname, os.path.basename(one_filename))
            cmd += " %s " % (dest + ".png")
            os.system(cmd)
    elif len(parts_dirnames) == 3:
        one = parts_dirnames[0]
        two = parts_dirnames[1]
        three = parts_dirnames[2]
        # ASSUME: we have the same number of files in all dirs
        filenames = glob.glob(os.path.join(one, "*.tga"))
        for one_filename in filenames:
            cmd = "convert "
            cmd += " -background black "
            two_filename = one_filename.replace(one, two)
            three_filename = one_filename.replace(one, three)
            names = [ get_name(filename) for filename in [one_filename, two_filename, three_filename]]
            cmd += imagemagick_vertical_string(
                imagemagick_horizontal_string(
                    imagemagick_image_string(names[0], one_filename),
                    imagemagick_image_string(names[1], two_filename)
                ),
                imagemagick_image_string(names[2], three_filename)
                )
            dest = os.path.join(combo_dirname, os.path.basename(one_filename))
            cmd += " %s " % (dest + ".png")
            os.system(cmd)
    elif len(parts_dirnames) == 4:
        one = parts_dirnames[0]
        two = parts_dirnames[1]
        three = parts_dirnames[2]
        four = parts_dirnames[3]
        # ASSUME: we have the same number of files in all dirs
        filenames = glob.glob(os.path.join(one, "*.tga"))
        for one_filename in filenames:
            two_filename = one_filename.replace(one, two)
            three_filename = one_filename.replace(one, three)
            four_filename = one_filename.replace(one, four)
            cmd = "convert "
            names = [ get_name(filename) for filename in [one_filename, two_filename, three_filename, four_filename]]
            cmd += imagemagick_vertical_string(
                imagemagick_horizontal_string(
                    imagemagick_image_string(names[0], one_filename),
                    imagemagick_image_string(names[1], two_filename)
                    ),
                imagemagick_horizontal_string(
                    imagemagick_image_string(names[2], three_filename),
                    imagemagick_image_string(names[3], four_filename)
                    ),
                )
            dest = os.path.join(combo_dirname, os.path.basename(one_filename))
            cmd += " %s " % (dest + ".png")
            os.system(cmd)
    else:
        raise Exception("Vivi doesn't know how to mix %i videos",
            len(parts_dirnames))


def make_movie_audio_file(audio_filename):
    movie_audio_filename = audio_filename.replace(".wav", ".movie.wav")
    cmd = "sox %s %s delay %f %f pad 0 %f" % (
        audio_filename, movie_audio_filename,
        DELAY_MOVIE_START_SECONDS,
        DELAY_MOVIE_START_SECONDS,
        DELAY_MOVIE_END_SECONDS)
    os.system(cmd)
    return movie_audio_filename

def get_name(name):
    if "violin-1" in name:
        return "violin 1"
    if "violin-2" in name:
        return "violin 2"
    if "viola" in name:
        return "viola"
    if "cello" in name:
        return "cello"
    return "unknown"



