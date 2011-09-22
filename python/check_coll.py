#!/usr/bin/env python

import collection

import utils
import shared
import dirs

class CheckColl:
	def __init__(self):
		self.data = []

	def check(self, coll, st, dyn):
		self.data = []

		cats_type = collection.CATS_MAIN
		cat_text = "main"
		training_file = dirs.files.get_mf_filename(
			st, cat_text, dyn).replace(".mf", ".mpl")

		for coll_index,pair in enumerate(coll.coll):
			cat = int(pair[1][0])
			if coll.is_cat(pair[1], cats_type):
				self.judge_wav_file(pair[0], cat)

	def judge_wav_file(self, wavfile, user_cat):
		compare_cat = user_cat-1
		cats = [0]*5

		cat_out = dirs.files.get_cats_name(wavfile[0:-4])
		cat_lines = open(cat_out+'.cats').readlines()
		for line in cat_lines:
			if line[0] == '#':
				continue
			splitline = line.split()
			cat = float( splitline[2].rstrip() )
			if cat != shared.vivi_controller.CATEGORY_NULL:
				cat_int = int(round(cat))
				if cat_int > 4:
					cat_int = 4
				if cat_int < 0:
					cat_int = 0
				cats[cat_int] += 1
				#print user_cat, "\t", cat+1, '\t', cat_int+1

		# TODO: ick, why is this necessary?
		cats_sum = float(sum(cats))
		if cats_sum > 0:
			for i in range(len(cats)):
				cats[i] /= cats_sum
		else:
			for i in range(len(cats)):
				cats[i] = 0.0
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

