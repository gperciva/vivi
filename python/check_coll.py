#!/usr/bin/env python

import collection

import utils
import shared

class CheckColl:
	def __init__(self):
		self.data = []

	def check(self, coll, st, dyn):
		self.data = []

		cats_type = collection.CATS_MAIN
		cat_text = "main"
		training_file = shared.files.get_mf_filename(
			st, cat_text, dyn).replace(".mf", ".mpl")

		for coll_index,pair in enumerate(coll.coll):
			cat = int(pair[1][0])
			if coll.is_cat(pair[1], cats_type):
				self.judge_wav_file(pair[0], cat)

	def judge_wav_file(self, wavfile, user_cat):
		compare_cat = user_cat-1
		cats = [0]*5

		# TODO: need to generalize
		cat_out = wavfile.replace(".wav", ".cats")
		cat_out = cat_out.replace("train/", "cache/")
		cat_lines = open(cat_out).readlines()
		for line in cat_lines:
			if line[0] == '#':
				continue
			splitline = line.split()
			cat = int( splitline[2].rstrip() )
			if cat != shared.vivi_controller.CATEGORY_NULL:
				cats[cat] += 1

		cats_sum = float(sum(cats))
		for i in range(len(cats)):
			cats[i] /= cats_sum
		#print cats
		datum = (str(user_cat), self.visualize_cats(cats,user_cat-1,10),
			wavfile, cats)
		self.data.append(datum)

	def visualize_cats(self, cats, target, length=8):
		cats_string = ''
		for i,c in enumerate(cats):
			if i == target:
				sym = '-'
			else:
				sym = '*'
			stars = int(round(c*length))
			cats_string += sym*stars
			cats_string += ' '*(length-stars)
			cats_string += ' '*(length/4)
		return cats_string

	def get_filename(self, index):
		return self.data[index][2]

