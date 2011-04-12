#!/usr/bin/env python
""" Manipulating files in the training directory. """
import os.path
import shared

class TrainingDir:
	""" convenience class for training directory. """
	def __init__(self, training_dir):
		self.dir = training_dir

	def get_mf_filename(self, st, cats_type, dyn):
		""" marsyas collection .mf file. """
		basename = 'coll_%i_%s_%i.mf' % (st,
			cats_type, dyn)
		filename = os.path.join(self.dir, basename)
		return filename

	def get_arff_filename(self, st, cats_type, dyn):
		""" weka training .arff file. """
		basename = 'coll_%i_%s_%i.arff' % (st,
			cats_type, dyn)
		filename = os.path.join(self.dir, basename)
		return filename

	def get_mpl_filename(self, st, cats_type, dyn):
		""" saved MarSystems (for training) .mpl file. """
		basename = 'coll_%i_%s_%i.mpl' % (st,
			cats_type, dyn)
		filename = os.path.join(self.dir, basename)
		return filename

	def get_forces_filename(self, st, dyn):
		""" initial bow forces .forces file. """
		basename = 'coll_%i_%i.forces' % (st, dyn)
		filename = os.path.join(self.dir, basename)
		return filename

	def make_audio_filename(self, params):
		""" audio .wav file. """
		basename = "audio_%i_%.3f_%.3f_%.3f_%.3f.wav" % (
			params.st, float(params.finger),
			params.bow_position, params.bow_force,
			params.bow_velocity)
		filename = os.path.join(self.dir, basename)
		return filename

	def get_audio_params(self, filename):
		""" parameters extracted from a .wav filename. """
		basename = os.path.splitext(os.path.basename(filename))[0]
		params = basename.split('_')[1:]
		audio_params = shared.AudioParams(
			int(params[0]), float(params[1]),
			float(params[2]), float(params[3]), float(params[4]))
		return audio_params

	def make_zoom_filename(self, params):
		""" save "zoomed" audio to a .wav file. """
		base_basename = "audio_%i_%.3f_%.3f_%.3f_%.3f_z_" % (
			params.st, float(params.finger),
			params.bow_position, params.bow_force,
			params.bow_velocity)
		count = 0
		potential_filename = os.path.join(self.dir, base_basename)
		while os.path.exists(potential_filename+'%04i'%count+'.wav'):
			count += 1
			if count >= 1000:
				print "Vivi error: training_dir: 999 files!"
				break
		filename = potential_filename + ('%04i' % count) + '.wav'
		return filename


