#!/usr/bin/env python
""" Manipulating files in the training directory. """
import os
import shared  # for AudioParams
import glob # for lists of files and dyns
import shutil # for cross-device move

class TrainingDir:
	""" convenience class for training directory. """
	def __init__(self, training_dirname, cache_dirname, final_dirname):
		def ensure_dir_exists(x):
			if not os.path.isdir(x):
				os.makedirs(x)
		map(ensure_dir_exists, [training_dirname] + [final_dirname] +
							   map(lambda(x): os.path.join(cache_dirname, x),
						 	       ["", "other", "inter", "works"]))
		self.train_dir = os.path.normpath(training_dirname)
		self.final_dir = os.path.normpath(final_dirname)
		self.inter_dir = os.path.join(cache_dirname, "inter")
		self.works_dir = os.path.join(cache_dirname, "works")

	def get_basename(self, st, cats_type, dyn):
		if cats_type == 'main':
			basename = '%i_%i.' % (st, dyn)
		else:
			basename = 'weird_%i_%i.' % (st, dyn)
		return basename

	def get_mf_filename(self, st, cats_type, dyn):
		""" marsyas collection .mf file. """
		filename = os.path.join(self.train_dir,
			self.get_basename(st, cats_type, dyn)
			+ 'mf')
		return filename

	def get_arff_filename(self, st, cats_type, dyn):
		""" weka training .arff file. """
		filename = os.path.join(self.inter_dir,
			self.get_basename(st, cats_type, dyn)
			+ 'arff')
		return filename

	def get_mpl_filename(self, st, cats_type, dyn):
		""" saved MarSystems (for training) .mpl file. """
		filename = os.path.join(self.final_dir,
			self.get_basename(st, cats_type, dyn)
			+ 'mpl')
		return filename

	def get_dyn_data_filename(self, st, dyn):
		""" trained dynamic .data file. """
		filename = os.path.join(self.final_dir,
			self.get_basename(st, 'main', dyn)
			+ 'data')
		return filename

	def basename_params(self, base, params, extra=None, count=None):
		basename = "%s_%i_%.3f_%.3f_%.3f_%.3f" % (
			base,
			params.string_number,
			float(params.finger_midi),
			params.bow_bridge_distance,
			params.bow_force,
			params.bow_velocity)
		if extra:
			basename += "_%.3f" % (extra)
		if count:
			basename += "_%i" % (count)
		# the .wav is added in ViviController
		#basename += ".wav"
		return basename

	def make_stable_filename(self, params, K, count):
		""" .wav file for automatic training of stable K."""
		basename = self.basename_params("stable", params, K, count)
		return os.path.join(self.works_dir, basename)

	def make_attack_filename(self, params, count):
		""" .wav file for automatic training of initial Fb."""
		basename = self.basename_params("attack", params, count)
		return os.path.join(self.works_dir, basename)

	def make_audio_filename(self, params):
		""" audio .wav file. """
		basename = self.basename_params("audio", params)
		filename = os.path.join(self.works_dir, basename)
		return filename

	def get_audio_params(self, filename):
		""" parameters extracted from a .wav filename. """
		basename = os.path.splitext(os.path.basename(filename))[0]
		params = basename.split('_')[1:]
		audio_params = shared.AudioParams(
			int(params[0]), float(params[1]),
			float(params[2]), float(params[3]), float(params[4]))
		return audio_params

	def get_audio_params_extra(self, filename):
		audio_params = self.get_audio_params(filename)
		basename = os.path.splitext(os.path.basename(filename))[0]
		params = basename.split('_')[1:]
		extra = float(params[5])
		count = int(params[6])
		return audio_params, extra, count

	def make_zoom_filename(self, params):
		""" save "zoomed" audio to a .wav file. """
		base_basename = "audio_%i_%.3f_%.3f_%.3f_%.3f_z_" % (
			params.string_number,
			float(params.finger_midi),
			params.bow_bridge_distance,
			params.bow_force,
			params.bow_velocity)
		count = 0
		potential_filename = os.path.join(self.works_dir, base_basename)
		train_dir_filename = os.path.join(self.train_dir, base_basename)
		# resolve any "hash" collisions
		while ( os.path.exists(potential_filename+'%04i'%count+'.wav') or
				os.path.exists(train_dir_filename+'%04i'%count+'.wav')):
			count += 1
			if count >= 1000:
				print "Vivi error: training_dir: 999 files with same params!"
				break
		filename = potential_filename + ('%04i' % count)
		return filename

	def move_works_to_train(self, src):
		dest = src.replace(self.works_dir, self.train_dir)
		shutil.move(src+'.wav', dest+'.wav')
		shutil.move(src+'.actions', dest+'.actions')
		return dest

	def get_cats_name(self, filename):
		if filename.startswith(self.train_dir):
			dest = filename.replace(self.train_dir, self.works_dir)
		else:
			dest = filename
		return dest

	def get_stable_files(self, st, dyn):
		bbd = shared.dyns.get_distance(dyn)
		bv  = shared.dyns.get_velocity(dyn)
		filename_pattern = str("stable_%i_0.000_%.3f_?????_%.3f_*.wav"
			% (st, bbd, bv))
		files = glob.glob(os.path.join(self.works_dir, filename_pattern))
		files.sort()
		return files

