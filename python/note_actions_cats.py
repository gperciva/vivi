#!/usr/bin/python

import shared
import os
import dynamics
import dirs

import collection

import vivi_types

HOP_SECONDS = 44100.0 / shared.vivi_controller.EARS_HOPSIZE

class NoteActionsCats:
    def __init__(self):
        self.basename = None
        self.lines = []
        self.cat_lines = []
        self.note_text = None
        self.note_prelim_line = None
        self.note_lines = []
        self.note_cat_lines = []
        self.note_forces = []
        self.note_cats = []
        self.note_cats_means = []
        self.note_skip = 0

    def reset_note(self):
        self.note_text = None
        self.note_prelim_line = None
        self.note_lines = []
        self.note_cat_lines = []
        self.note_forces = []
        self.note_cats = []
        self.note_cats_means = []
        self.note_skip = 0

    def load_file(self, filename):
        self.basename = filename
        self.lines = open(self.basename+'.actions').readlines()
        cats_name = dirs.files.get_cats_name(filename)
        try:
            self.cat_lines = open(cats_name+'.cats').readlines()
        except:
            self.cat_lines = []
        self.reset_note()

    def load_note(self, note_text, full=False):
        if not self.lines:
            return False
        self.reset_note()
        self.note_text = note_text

        i = 0
        skip_start = 0
        while not self.lines[i].find(self.note_text) >= 0:
            if self.lines[i] == 's':
                skip_start = float(self.lines[i].split()[1])
            if self.lines[i] == 'k':
                skip_end = float(self.lines[i].split()[1])
                self.note_skip += skip_end - skip_start
            i += 1
            if i >= len(self.lines):
                #print "Item not found"
                return False

        self.note_prelim_line = self.lines[i]
        note_prelim_info = self.note_prelim_line.split()
        self.note_st = int(note_prelim_info[3])
        self.note_dyn = float(note_prelim_info[5])
        self.note_finger = round(float(note_prelim_info[7]))
        self.note_pos = dynamics.get_distance(self.note_dyn)
        self.note_vel = dynamics.get_velocity(self.note_dyn)
        # find beginning of real actions
        while self.lines[i].startswith('#'):
            i += 1
        i += 1

        while (not self.lines[i].startswith('#')) or (full):
            self.note_lines.append( self.lines[i] )
            if self.lines[i][0] == 's':
                skip_start = float(self.lines[i].split()[1])
            if self.lines[i][0] == 'k':
                skip_end = float(self.lines[i].split()[1])
                self.note_skip += skip_end - skip_start
            i += 1
            if i >= len(self.lines):
                break

        self.note_start = float(self.note_lines[0].split()[1])
        self.note_length = (float(self.note_lines[-1].split()[1])
            - self.note_start) - self.note_skip

        note_end = self.note_start + self.note_length
        for line in self.cat_lines:
            if line[0] != '#':
                splitline = line.split()
                seconds = float(splitline[1])
                if seconds >= self.note_start and seconds <= note_end:
                    self.note_cat_lines.append(line)

        self.note_forces = self.get_note_forces()
        self.note_cats = self.get_note_cats()
        self.note_cats_means = self.get_note_cats_means(self.note_cats)

        if len(self.note_cats) < len(self.note_forces):
            self.note_cats.append((0, 0))
        return True

    def get_note_forces(self):
        note_forces = []
        skip = False
        for line in self.note_lines:
            if line[0] == 's':
                skip = True
            elif line[0] == 'k':
                skip = False
            if skip:
                continue
            if line[0] == 'b':
                splitline = line.split()
                seconds = float(splitline[2])
                force = float(splitline[4])
                note_forces.append( (seconds, force) )
        return note_forces

    def get_note_cats(self):
        cats = []
        if not self.note_cat_lines:
            return cats
        for line in self.note_cat_lines:
            if line[0] == 'c':
                splitline = line.split()
                seconds = float(splitline[1])
                cat = float(splitline[2])
                cats.append( (seconds, cat) )
        return cats

    def get_note_cats_means(self, cats):
        # get cat_means
        note_cats_means = []
        length = shared.vivi_controller.CATS_MEAN_LENGTH
        filt = [collection.CATEGORY_NULL] * length
        filt_index = 0
        for seconds, c in cats:
            filt[filt_index] = c
            filt_index += 1
            if filt_index == length:
                filt_index = 0
            if collection.CATEGORY_NULL in filt:
                note_cats_means.append(collection.CATEGORY_NULL)
            else:
                mean = float(sum(filt)) / length
                note_cats_means.append(mean)
        return note_cats_means

    def get_seconds(self, start, dur):
        start_sec = self.note_start + start*self.note_length
        dur_sec = dur*self.note_length
        return start_sec, dur_sec

    def make_zoom_file(self, start, dur):
        force = 0.0
        # TODO: generalize
        starthop = int((start-self.note_start) * HOP_SECONDS)
        endhop = starthop+int( dur * HOP_SECONDS )
        for i in range(starthop, endhop):
            force += self.note_forces[i][1]
        force /= (endhop - starthop)
        audio_params = vivi_types.AudioParams(
            self.note_st, self.note_finger, self.note_pos,
            force, self.note_vel)
        filename = dirs.files.make_zoom_filename(audio_params)

        # create .wav
        cmd = 'sox %s %s trim %f %f' % (
            self.basename+'.wav', filename+'.wav', start, dur)
        os.system(cmd)
        # create .actions
        out = open(filename+'.actions', 'w')
        out.write(self.note_prelim_line)
        # TODO: clean this up!
        first_seconds = -1
        for line in self.note_lines:    
            splitline = line.split()
            seconds = float(splitline[1])
            if seconds >= start:
                if first_seconds < 0:
                    first_seconds = seconds
                seconds = seconds - first_seconds
                 if seconds <= dur:
                    splitline[1] = str(seconds)
                    done_line = "\t".join(splitline) + "\n"
                    out.write(done_line)
        out.close()

        return filename


