#!/usr/bin/env python


import os # FIXME: temp for debugging
import glob

import sys # FIXME: temp for debugging

GRACE_DUR_FRACTION = 0.5

class Event:
	def __init__(self, onset=0, duration=0, details=None):
		self.onset = onset
		self.duration = duration
		if not details:
			self.details = []
		else:
			self.details = list(details)
	def __str__(self):
		return "%s\t%s\t%s" % (self.onset, self.duration, self.details)

class MusicEvents():

	def __init__(self):
		self.events = None

	def load_file(self, filenames):
		self.events = []

		events = {}
		# FIXME: only handle one staff right now
		filename = filenames[0]
		lines = open(filename).read().splitlines()
		for line in lines:
			splitline = line.split()
			bar_time_with_grace = splitline[0]
			event_type = splitline[1]
			params = splitline[2:]
			if not bar_time_with_grace in events:
				events[bar_time_with_grace] = Event(onset=bar_time_with_grace)
			events[bar_time_with_grace].details.append( (event_type, params) )

		def _sort_music_events(x):
			if x[0] == 'note':
				return 0
			elif x[0] == 'rest':
				return 1
			else:
				return 2
		def _sort_with_grace(x):
			# TODO: this is icky!
			split_x = x.split('-')
			if len(split_x) == 1:
				return split_x[0]+'-999'
			else:
				return split_x[0] + str(999-float(split_x[1]))
		def _make_event(dict_key, value):
			details = sorted(value.details,
						key=_sort_music_events)
			return Event(onset=dict_key, duration=self.get_duration(details), details=details)

		self.events = map(lambda(dict_key):_make_event(dict_key, events[dict_key]),
			sorted(events.keys(),key=_sort_with_grace))
		# strip grace notes for now
		self.events = filter(lambda(event): event.onset.find('-')<0, self.events)
		#self.adjust_grace()

		self.sanity_bar_time_test()

	def sanity_bar_time_test(self):
		bar_time = 0.0
		for event in self.events:
			if float(event.onset) != bar_time:
				print "ERROR: bar times do not agree", event, bar_time
				sys.exit(1)
			bar_time += event.duration

	@staticmethod
	def get_duration(details):
		if details[0][0] == 'note':
			return float(details[0][1][2])
		else:
			return float(details[0][1][1])


	def adjust_grace(self):
		# ASSUME: "on the beat" grace notes
		delay_dur = 0
		for i, event in enumerate(self.events):
			onset = event.onset.split('-')
			main_onset = float(onset[0])
			if len(onset) == 1:
				event.onset = main_onset + delay_dur
				delay_dur = 0
			else:
				grace_dur = GRACE_DUR_FRACTION * float(onset[1])
				delay_dur = grace_dur
				event.onset = main_onset + delay_dur
			print
			#print event.onset


	def print_events(self):
		print "--------- events"
		for event in self.events:
			print event

