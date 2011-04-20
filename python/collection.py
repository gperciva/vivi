#!/usr/bin/env python

import operator

categories = [
	'1_more_more_force',
	'2_more_force',
	'3_ok',
	'4_less_force',
	'5_less_less_force',
	'6__unknown',
]

CATS_ALL = 0
CATS_WEIRD = 1
CATS_MAIN = 2

class Collection:
	def __init__(self):
		self.coll = []

	def sort(self):
		self.coll = sorted(self.coll, key=operator.itemgetter(1,0))

	def add_mf_file(self, filename):
		try:
			lines = open(filename).readlines()
		except:
			return
		for line in lines:
			splitline = line.split()
			self.add_item(splitline[0], splitline[1], False, False)
		self.sort()

	def write_mf_file(self, filename):
		self.sort()
		outfile = open(filename, 'w')
		for pair in self.coll:
			outfile.write(pair[0] + '\t' + pair[1] + '\n')
		outfile.close()

	def write_mf_file(self, filename, inout):
		self.sort()
		outfile = open(filename, 'w')
		for pair in self.coll:
			wavfile = pair[0]
			judgement = pair[1]
			if self.is_cat(judgement, inout):
				outfile.write(wavfile+'\t'+judgement+'\n')
		outfile.close()

	def get_cat_text(self, cat_type):
		if cat_type == CATS_ALL:
			return 'all'
		elif cat_type == CATS_WEIRD:
			return 'weird'
		elif cat_type == CATS_MAIN:
			return 'main'
		return None

	def is_cat(self, judgement, cat_type):
		cat = judgement[0]
		if cat_type == CATS_ALL:
			return True
		elif cat_type == CATS_WEIRD:
			if (cat=='6'):
				return True
		elif cat_type == CATS_MAIN:
			if ((cat>='1') and (cat<='5')):
				return True
		return False

	def get_items(self, cat):
		self.sort()
		to_return = []
		for pair in self.coll:
			if int(pair[1][0]) == cat:
				to_return.append(pair)
		return to_return

	def add_item(self, filename, judgement, replace=False, warning=True):
		new_pair = (filename, judgement)
		for i, pair in enumerate(self.coll):
			if pair[0] == filename:
				if (not replace) and warning:
					print "Warning: Collection: replacing a previous item"
				self.coll[i] = new_pair
				return
		if replace and warning:
			print "Warning: Collection: original item not found"
		self.coll.append(new_pair)

	def replace(self, filename, judgement):
		add_item(filename, judgement, True)

	def delete(self, filename):
		for i, pair in enumerate(self.coll):
			if pair[0] == filename:
				self.coll.pop(i)
				return
		print "Warning: Collection: failed to delete %s" % filename

	def num_main(self):
		number = 0
		for pair in self.coll:
			cat = pair[1][0]
			if ((cat>='1') and (cat<='5')):
				number += 1
		return number

def self_test(filename):
	coll = Collection()
	coll.add_mf_file(filename)
	coll.write_mf_file(filename, CATS_ALL)

if __name__ == "__main__":
	import sys
	self_test(sys.argv[1])


