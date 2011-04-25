#!/usr/bin/python

import os
import math

import utils
import shared

#import ears
EARS_HOPSIZE = 256

#import levels


def pos2midi(pos):
	return 12.0*math.log(1.0/(1.0 - pos)) / math.log(2.0)


class ExamineNote:
	def __init__(self):
		self.lines = []
		self.note_lines = []
		self.note_force_cat = []


	def load_file(self, filename):
		#print filename
		# it's a .wav
		self.basename = filename[:-4]
		#print "examine note:", self.basename
		self.wavfile = self.basename+'.wav'
		self.lines = open(self.basename+'.actions').readlines()

#		self.note_cats_out = []
#		self.note_forces = []
#		for line in self.lines:
#			ni = line.split()
#			if line.startswith("cat"):
#				self.note_cats_out.append(int(ni[2]))
#			if line.startswith("b"):
#				self.note_forces.append( float(ni[4]) )
#				self.bow_lines.append(ni)
		#if os.path.exists('ly/violin-1.log'):
	#		self.lines = open('ly/violin-1.log').readlines()
#		else:
#			self.lines = []
		#print self.note_cats_out
		#print self.note_forces
		self.note_lines = []
		self.note_force_cat = []

#		self.note_start = 0
#		self.note_length = (float(self.lines[-1].split()[1])
#			- self.note_start)

#		self.judging = False



	### old function
	#def load_note(self, lily_line, lily_col):
	#	if not self.lines:
	#		return False
	#	self.note_lines = []
	#	text = 'point-and-click %i %i' % (lily_col, lily_line)
	#	i = 0
	def load_note(self, text):
		if not self.lines:
			return False
		self.note_lines = []
		i = 0
		while not self.lines[i].find(text) >= 0:
			i += 1
			if i >= len(self.lines):
				#print "Item not found"
				return False

#		i += 1
		note_prelim_info = self.lines[i].split()
		self.note_st = int(note_prelim_info[4])
		self.note_dyn = float(note_prelim_info[6])
		self.note_finger = round(
			float(note_prelim_info[10]))
		self.note_pos = shared.dyns.get_distance(self.note_dyn)
		self.note_vel = shared.dyns.get_velocity(self.note_dyn)
		#self.note_pos = float(note_prelim_info[6])
		#self.note_vel = float(note_prelim_info[8])
		i += 1
		i += 1

		while not self.lines[i].startswith('#'):
			self.note_lines.append( self.lines[i] )
			i += 1
			if i >= len(self.lines):
				break

		self.note_start = float(self.note_lines[0].split()[1])
		self.note_length = (float(self.note_lines[-1].split()[1])
			- self.note_start)

		self.note_info()
		return True

	def note_info(self):
		self.note_force_cat = []
		i = 0
		while (i < len(self.note_lines)):
			line = self.note_lines[i].split()
			#print line
			if line[0][0] == 'b':
				force = float(line[4])
			#	print force
				cat = -1
				i += 1
				if i < len(self.note_lines):
					line = self.note_lines[i].split()
					if line[0] == "cat":
						cat = int(line[2])
						i += 1 
				self.note_force_cat.append( (force, cat) )
			else:
				# skip
				i += 1
		#print self.note_force_cat

	def potential_add(self, force, prev_force):
		audio_params = shared.AudioParams(
			self.note_st, self.note_finger, self.note_pos,
			force, self.note_vel)
		if prev_force == 0:
			self.train_list.append(audio_params)
			return force
		if force > prev_force:
			if (force/prev_force) > self.force_min_factor:
				self.train_list.append(audio_params)
				return force
		else:
			if (prev_force/force) > self.force_min_factor:
				self.train_list.append(audio_params)
				return force
		return prev_force

	def get_train_list(self):
		self.train_list = []

		sort_forces = list(self.note_forces)
		sort_forces.sort()
		l = len(sort_forces)
		force_median = sort_forces[ l/2 ]
		force = self.potential_add(force_median, 0)
		# add forces if there's a sufficiently larger factor
		force = self.potential_add(sort_forces[int(0.25*l)], force)
		force = self.potential_add(sort_forces[int(0.05*l)], force)
		force = force_median
		force = self.potential_add(sort_forces[int(0.75*l)], force)
		force = self.potential_add(sort_forces[int(0.95*l)], force)
		return self.train_list

	def get_seconds(self, start, dur):
		num_bins = len(self.note_forces)
		#seconds = num_bins * ears.EARS_HOPSIZE / 44100.0
		# TODO: generalize this
		seconds = num_bins * 256 / 44100.0
		start_sec = self.note_start + start*seconds
		dur_sec = dur*seconds
		return start_sec, dur_sec

	def make_zoom_file(self, start, dur):
		force = 0.0
		# TODO: generalize
		starthop = int((start-self.note_start)
				*44100.0/256)
				#*44100.0/ears.EARS_HOPSIZE)
		endhop = starthop+int( dur
				*44100.0/256)
				#*44100.0/ears.EARS_HOPSIZE)
		for i in range(starthop, endhop):
			print self.bow_lines[i][4]
			force += float(self.bow_lines[i][4])
		force /= (endhop - starthop)
		audio_params = shared.AudioParams(
			self.note_st, self.note_finger, self.note_pos,
			force, self.note_vel)
		filename = shared.files.make_zoom_filename(audio_params)
		cmd = 'sox %s %s trim %f %f' % (self.wavfile, filename, start, dur)
		os.system(cmd)
		return filename


