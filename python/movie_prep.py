#!/usr/bin/python

import shared
import state
import vivi_defines
import os

SPLIT_IMAGES_INTO_NUM_THREADS = 4

# half a buffer of impulse reponse?
EXTRA_DELAY_BODY_RESPONSE = 1024.0 / 22050.0
DELAY_MOVIE_START_SECONDS = 0.5 + EXTRA_DELAY_BODY_RESPONSE
DELAY_MOVIE_END_SECONDS = 0.5 + EXTRA_DELAY_BODY_RESPONSE

def get_end_time(actions_filename):
    lines = open(actions_filename).readlines()
    end_time = float(lines[-1].split()[1] )
    return end_time

def get_split_tasks():
    return SPLIT_IMAGES_INTO_NUM_THREADS

def start_job(files, quality=0):
    total_steps = 0
    for i in range(len(files.notes_all)):
        files.set_notes_index(i)
        actions_filename = files.get_notes_last("*.actions")
        ly_basename = files.get_ly_basename()
        movie_dirname = os.path.join(
            files.get_ly_movie_dir(),
            os.path.splitext(os.path.basename(str(actions_filename)))[0])
        if not os.path.exists(movie_dirname):
            os.makedirs(movie_dirname)
        #print "started job to create", actions_filename
        total_steps += start_split_jobs(actions_filename,
            movie_dirname, ly_basename, quality)
    return total_steps

def start_split_jobs(actions_filename, movie_dirname, ly_basename, quality):
    total_steps = 0
    end_time = get_end_time(actions_filename)
    end_time_delayed = (end_time
        + DELAY_MOVIE_START_SECONDS + DELAY_MOVIE_END_SECONDS)
    end_frame = int(end_time_delayed * vivi_defines.VIDEO_FPS) + 1
    image_step = end_frame / SPLIT_IMAGES_INTO_NUM_THREADS
    for i in range(SPLIT_IMAGES_INTO_NUM_THREADS):
        if quality == 0:
            job = state.Job(vivi_defines.TASK_RENDER_VIDEO_PREVIEW)
            job.quality = 0
        else:
            job = state.Job(vivi_defines.TASK_RENDER_VIDEO)
            job.quality = 1

        job.start_frame = i * image_step + 1
        if i < (SPLIT_IMAGES_INTO_NUM_THREADS - 1):
            job.end_frame = (i+1) * image_step
        else:
            job.end_frame = end_frame
        job.ly_basename = ly_basename
        job.movie_dirname = movie_dirname
        job.logfile_num = i
        job.actions_filename = make_movie_actions_file(actions_filename)
        job.ly_basename = ly_basename
        total_steps += shared.thread_pool.add_task(job)
    return total_steps

def get_instrument_camera(actions_filename):
    name = actions_filename.split("-")[-2]
    if "violin" in name:
        return 0
    if "viola" in name:
        return 1
    if "cello" in name:
        return 2
    return 0

def make_movie_actions_file(actions_filename):
    actions_lines = open(actions_filename).readlines()
    movie_actions_filename = actions_filename.replace(".actions",
        ".movie.actions")
    movie_actions_file = open(movie_actions_filename, "w")
    movie_actions_file.write("c\t0.0\t%i\n" % (
        get_instrument_camera(actions_filename)))
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

