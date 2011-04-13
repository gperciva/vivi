#!/usr/bin/env python
""" Manipulating files in the training directory. """
import os
import shared  # for AudioParams

class TrainingDir:
	""" convenience class for training directory. """
	def __init__(self, training_dirname):
		if not os.path.isdir(training_dirname):
			os.makedirs(training_dirname)
		self.dir = training_dirname

#	def get_dirname(self):
#		""" gets absolute location of training dir. """
#		return os.path.abspath(self.dir)

	def get_basename(self, st, cats_type, dyn):
		if cats_type == 'main':
			basename = '%i_%i.' % (st, dyn)
		else:
			basename = 'weird_%i_%i.' % (st, dyn)
		return basename

	def get_mf_filename(self, st, cats_type, dyn):
		""" marsyas collection .mf file. """
		filename = os.path.join(self.dir,
			self.get_basename(st, cats_type, dyn)
			+ 'mf')
		return filename

	def get_arff_filename(self, st, cats_type, dyn):
		""" weka training .arff file. """
		filename = os.path.join(self.dir,
			self.get_basename(st, cats_type, dyn)
			+ 'arff')
		return filename

	def get_mpl_filename(self, st, cats_type, dyn):
		""" saved MarSystems (for training) .mpl file. """
		filename = os.path.join(self.dir,
			self.get_basename(st, cats_type, dyn)
			+ 'mpl')
		return filename

	def get_forces_filename(self, st, dyn):
		""" initial bow forces .forces file. """
		filename = os.path.join(self.dir,
			self.get_basename(st, 'main', dyn)
			+ 'forces')
		return filename

	def make_audio_filename(self, params):
		""" audio .wav file. """
		basename = "audio_%i_%.3f_%.3f_%.3f_%.3f.wav" % (
			params.string_number,
			float(params.finger_midi),
			params.bow_bridge_distance,
			params.bow_force,
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
			params.string_number,
			float(params.finger_midi),
			params.bow_position,
			params.bow_force,
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


