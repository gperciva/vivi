#!/usr/bin/env python
""" Basic driver for Vivi."""
import sys

# TODO: hack for current build system.
sys.path.append('python/')
sys.path.append('build/python/')
sys.path.append('build/swig/')
import vivi_mainwindow

#import gc
#gc.set_debug(gc.DEBUG_LEAK)

def get_options():
	""" Gets options from command line."""
	import optparse
	parser = optparse.OptionParser()
	parser.add_option("-c", "--cache_dir", dest="cache_dir",
		default="/tmp/vivi-cache/",
		help="Directory for cache of automatic training files", metavar="DIR")
	parser.add_option("-f", "--final_dir", dest="final_dir",
		default="final/",
		help="Directory for output of training", metavar="DIR")
	parser.add_option("-d", "--dir", dest="train_dir",
		default="train/",
		help="Directory for training files", metavar="DIR")
	parser.add_option("-l", "--lily", dest="lily_file",
		help="LilyPond file to practice", metavar="FILE")
	parser.add_option("-s", "--skill", dest="skill",
		help="Skill level (-1 is best, 0 is worst)",
		default=-1, metavar="NUMBER"),
	(options, args) = parser.parse_args()
	return options, args

def main():
	""" Runs Vivi."""
	opts, args = get_options()

	vivi_main = vivi_mainwindow.ViviMainwindow(
		opts.train_dir, opts.cache_dir, opts.final_dir,
		opts.lily_file, int(opts.skill))
	sys.exit(vivi_main.app.exec_())

if __name__ == "__main__":
	main()


