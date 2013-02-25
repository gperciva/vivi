#!/usr/bin/python

import os
import dynamics

import collection
import vivi_defines

import numpy

import utils
import vivi_types

HOP_SECONDS = 22050.0 / vivi_defines.HOPSIZE

class NoteActionsCats:
    def __init__(self):
        self.basename = None
        self.lines = []
        self.cat_lines = []
        self.cat_new_notes = []
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

    def load_file(self, filename, files=None):
        self.basename = filename
        self.lines = open(self.basename+'.actions').readlines()
        if files:
            cats_name = files.get_cats_name(filename)
        else:
            cats_name = filename
        try:
            self.cat_lines = open(cats_name+'.cats').readlines()
        except:
            self.cat_lines = []
        self.reset_note()

        # find notes
        self.cat_new_notes = []
        for line in self.cat_lines:
            if line.startswith("#\tnote"):
                self.cat_new_notes.append(line)
            if line[0] != '#':
                self.cat_new_notes.append(None)

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
        self.note_inst = int(note_prelim_info[3])
        self.note_st = int(note_prelim_info[5])
        self.note_dyn = float(note_prelim_info[7])
        self.note_finger = round(float(note_prelim_info[9]))
        self.note_pos = dynamics.get_distance(self.note_inst, self.note_dyn)
        self.note_vel = dynamics.get_velocity(self.note_inst, self.note_dyn)
        # find beginning of real actions
        while self.lines[i].startswith('#'):
            i += 1
        i += 1

        while (not self.lines[i].startswith('#')) or (full):
            if not self.lines[i].startswith('#'):
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

        
        cat_note_begin = None
        cat_note_end = len(self.cat_new_notes)
        for i, line in enumerate(self.cat_new_notes):
            if line is None:
                continue
            else:
                if line.find(note_text) >= 0:
                    cat_note_begin = i
                elif cat_note_begin is not None:
                    cat_note_end = i
                    break
        #print "from notes:", cat_note_begin, cat_note_end
        #print "from orig :", self.note_start, note_end

        for line in self.cat_lines:
            if line[0] != '#':
                splitline = line.split()
                seconds = float(splitline[1])
                if seconds >= self.note_start and seconds <= note_end:
                    self.note_cat_lines.append(line)
            #if line.startswith("#\tnote"):
            #    self.note_cat_lines.append(line)
        #print len(self.note_cat_lines)

        self.note_forces = self.get_note_forces()
        self.note_cats = self.get_note_cats()
        self.note_cats_means = self.get_note_cats_means(self.note_cats)
        #print len(self.note_forces), len(self.note_cats)

        # no clue why I wrote this, so I'm scared to remove it.  :(
        #if len(self.note_cats) < len(self.note_forces):
        #    self.note_cats.append((0, vivi_defines.CATEGORY_NULL))

        #print len(self.note_cats), len(self.note_forces)
        #print '----'
        #print self.note_cats[0], self.note_cats[-1]
        #print '----'
        #print self.note_forces[1], self.note_forces[-1]
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
            if line[0] == 'b' or line[0] == 'a':
                splitline = line.split()
                seconds = float(splitline[1])
                force = float(splitline[4])
                note_forces.append( (seconds, force) )
        return note_forces

    def get_note_cats(self):
        cats = []
        if not self.note_cat_lines:
            return cats
        seconds = 0.0
        for line in self.note_cat_lines:
            if line[0] == 'c':
                splitline = line.split()
                seconds = float(splitline[1])
                cat = float(splitline[2])
                cats.append( (seconds, cat) )
            if line.startswith("#\tnote"):
                cats.append( (seconds+0.001, None) )
        return cats

    def get_note_cats_means(self, cats):
        return [b for a,b in cats]
        # get cat_means
        note_cats_means = []
        length = vivi_defines.CATS_MEAN_LENGTH
        filt = [vivi_defines.CATEGORY_NULL] * length
        filt_index = 0
        for seconds, c in cats:
            if c == vivi_defines.CATEGORY_NULL or c == vivi_defines.CATEGORY_WAIT:
                note_cats_means.append(vivi_defines.CATEGORY_NULL)
                continue
            #if c == vivi_defines.CATEGORY_WEIRD:
            #    # do rest of loop with this
            #    c = 0
            filt[filt_index] = c
            filt_index += 1
            if filt_index == length:
                filt_index = 0
            #if c == vivi_defines.CATEGORY_WEIRD:
                # don't use averaged value, though
            #    note_cats_means.append(vivi_defines.CATEGORY_WEIRD)
            if vivi_defines.CATEGORY_NULL in filt:
                note_cats_means.append(vivi_defines.CATEGORY_NULL)
            else: 
                mean = float(sum(filt)) / length
                note_cats_means.append(mean)
        return note_cats_means

    def get_seconds(self, start, dur):
        start_sec = self.note_start + start*self.note_length
        dur_sec = dur*self.note_length
        return start_sec, dur_sec

    def check_rel_range(self, start, dur):
        #print
        #print "check rel range, start dur", start, dur
        #print "note start, len in hops", self.note_start, len(self.note_cats)
        conv = len(self.note_cats)
        start *= conv
        dur *= conv
        #print start, self.note_start
        #starthop = int((start-self.note_start))
        #endhop = int((start+dur-self.note_start))
        starthop = int(round(start))
        endhop = int(round(start+dur))
        endhop = min(endhop, len(self.note_cats)-1)
        #print "starhop, endhop", starthop, endhop
        #check = [ b for a,b in self.note_cats[starthop:endhop] ]
        # strip beginning
        while True:
        #    print "starthop:", starthop
            #print self.note_cats[starthop]
            if (self.note_cats[starthop][1] == vivi_defines.CATEGORY_NULL
                or self.note_cats[starthop][1] == vivi_defines.CATEGORY_WAIT
                or self.note_cats[starthop][1] == None):
                starthop += 1
            else:
                break
            if starthop >= endhop:
                return -1, -1
        # strip ending
        while True:
            #print "endhop:", starthop
            if (self.note_cats[endhop][1] == vivi_defines.CATEGORY_NULL
                or self.note_cats[endhop][1] == vivi_defines.CATEGORY_WAIT
                or self.note_cats[endhop][1] == None):
                endhop -= 1
            else:
                break
            if starthop >= endhop:
                return -1, -1
        for c in self.note_cats[starthop:endhop]:
            if (c[1] == vivi_defines.CATEGORY_NULL
                or c[1] == vivi_defines.CATEGORY_WAIT
                or c[1] == None):
                return -1, -1
        #print "starhop, endhop", starthop, endhop
        start = starthop/float(conv)
        dur = (endhop-starthop)/float(conv)
        #print "ending, start dur", start, dur
        return start, dur

    def make_zoom_file(self, start, dur, files):
        #print "make_zoom_file  %.3f  %.3f" % (start, dur)
        self.files = files
        force = 0.0
        ### get params from note
        #print starthop, endhop

        ### quantify based on hopsize
        starthop = int((start-self.note_start) * HOP_SECONDS)
        endhop = int((start+dur-self.note_start) * HOP_SECONDS)
        # no, *don't* make this based on the note,
        # otherwise it won't work in music!
        start = float(int(start * HOP_SECONDS)) / HOP_SECONDS
        dur = float( int(endhop-starthop)) / HOP_SECONDS

        #print "starthop, endhop:\t%i\t%i" % (starthop, endhop)
        print "Should have lines:\t%i" %(endhop-starthop)
        #print "start, dur:\t%i\t%i" % (start, dur)

        #for l in self.note_lines:
        #    print l

        #print start, dur
        ### initial note estimates
        # assume string doesn't change
        fm = self.note_finger
        bbd = 0.0
        force = 0.0
        bv = 0.0
        #for i in range(0, starthop+1):
        for i in range(0, starthop+1):
            line = self.note_lines[i].split()
            if line[0] == 'b' or line[0] == 'a':
                bbd = float(line[3])
                force = float(line[4])
                bv = float(line[5])
            if line[0] == 'f':
                fm = utils.pos2midi(float(line[3]))
        bbd = [bbd]
        force = [force]
        bv = [bv]
        for i in range(0, starthop+1):
            line = self.note_lines[i].split()
            if line[0] == 'b' or line[0] == 'a':
                bbd.append( float(line[3]) )
                force.append( float(line[4]) )
                bv.append( float(line[5]) )
            if line[0] == 'f':
                fm = utils.pos2midi(float(line[3]))
        audio_params = vivi_types.AudioParams(
            self.note_st, fm,
                numpy.median(bbd),
                numpy.median(force),
                numpy.median(bv))

        ### filename
        filename = self.files.make_zoom_filename(audio_params)
        print "ZOOM file:\t", filename

        # create .wav
        cmd = 'sox %s -t wavpcm %s trim %f %f' % (
            self.basename+'-s%i.wav' % (self.note_st),
            filename+'.wav', start, dur)
        print cmd
        os.system(cmd)
        # create .forces..wav
        cmd = 'sox %s -t wavpcm %s trim %f %f' % (
            self.basename+'-s%i.forces.wav' % (self.note_st),
            filename+'.forces.wav', start, dur)
        #print cmd
        os.system(cmd)
        # create .actions
        out = open(filename+'.actions', 'w')
        out.write(self.note_prelim_line)
        # TODO: clean this up!
        first_seconds = -1
        printed_finger = False
        #num_lines = 0
        for line in self.note_lines:    
            splitline = line.split()
            seconds = float(splitline[1])
            if line[0] == 'f':
                fm = float(splitline[3])
            if seconds >= (start - 0.001):
                if first_seconds < 0:
                    first_seconds = seconds
                seconds = seconds - first_seconds
                if seconds <= (start + dur + 0.001):
                    splitline[1] = str(seconds)
                    if not printed_finger:
                        if splitline[0][0] == 'f':
                            pass
                        else:
                            data = ['f', str(seconds),
                                str(self.note_st),
                                str(utils.midi2pos(fm))]
                            finger_line = "\t".join(data) + "\n"
                            out.write(finger_line)
                        printed_finger = True
                    done_line = "\t".join(splitline) + "\n"
                    out.write(done_line)
        out.close()

        return filename


