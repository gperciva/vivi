#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import dyn_train_gui

import collection

import os # to delete audio files whose judgement was cancelled

#import levels
import utils

# TODO: **must** import ears first, then controller.  No clue why.
#import ears

#import utils
import shared

import state

import dyn_backend
#import ears



# just for BASIC_PARAMS; iffy; icky
#import performer
#BASIC_PARAMS = performer.BasicParams(force_std=0.01, velocity_std=0.01,
#	duration_settle=1.0, duration_play=0.5)
BASIC_SECONDS = 0.3
BASIC_SKIP = 0.5


STATE_NULL = 0
STATE_BASIC_TRAINING = 1j




OPINION_END = 1
OPINION_CONTINUE = 2
OPINION_QUIT = 3


class DynTrain(QtGui.QFrame):
	process_step = QtCore.pyqtSignal()

	def __init__(self, parent, st, dyn, controller, practice):
		QtGui.QFrame.__init__(self)
		self.st = st
		self.dyn = dyn
		self.controller = controller
		self.practice = practice

		### setup GUI
		self.ui = dyn_train_gui.Ui_dyn_train_box()
		self.ui.setupUi(self)
		parent.addWidget(self)
		if self.dyn == 0:
			text = 'f'
		elif self.dyn == 1:
			text = 'mf'
		elif self.dyn == 2:
			text = 'mp'
		elif self.dyn == 3:
			text = 'p'
		self.ui.dyn_type.setText(text)

		self.mousePressEvent = self.click
		self.ui.toolButton.clicked.connect(self.set_modified)


		### setup variables
		self.judged_main_num = 0
		self.accuracy = -1.0

		if self.dyn == 0:
			self.level = 0
		elif self.dyn == 1:
			self.level = 2
		elif self.dyn == 2:
			self.level = 3
		elif self.dyn == 3:
			self.level = 1

		self.modified_training = False
		self.modified_accuracy = False
		self.modified_stable = False
		self.modified_attack = False

		self.coll = collection.Collection()

		self.basic_trained = False

		self.read()
#		self.levels = levels.Levels()
#		self.levels.set_coll(self.coll)

#		if self.judged_main_num > 0:
#			self.ears = ears.Ears()
		#	shared.listen[self.st][self.dyn] = self.ears
#		else:
#			self.ears = None
		#	shared.listen[self.st][self.dyn] = None
#		shared.listen[self.st][self.dyn] = self.ears

		### setup backend
		self.dyn_backend = dyn_backend.DynBackend(
			self.st, self.dyn, self.level, self.force_init,
			self.force_factor,
			self.controller, self.practice)
		self.dyn_backend.process_step.connect(self.process_step_emit)

		self.state = state.State()
		self.state.next_step.connect(self.next_step)
		self.state.finished_step.connect(self.finished_step)

		self.display()



#		try:
#			filename = shared.files.get_forces_filename(self.st, self.dyn)
#			att = open(filename).readlines()
#			self.force_init = []
#			for i in range(3):
#				self.force_init.append(float( att[i].rstrip() ))
#			self.force_factor = float( att[3].rstrip() )
#		except:
#			self.force_init = [-1.0, -1.0, -1.0]
#			self.force_factor = 1.0


	def select(self, enable):
		if enable:
			self.ui.dyn_type.setBackgroundRole(
					QtGui.QPalette.Highlight)
					#QtGui.QPalette.AlternateBase)
		else:
			self.ui.dyn_type.setBackgroundRole(
					QtGui.QPalette.Window)

	def display(self):
		if not self.judged_main_num:
			self.setEnabled(False)
			self.ui.num_trained_label.setText("")
			self.ui.accuracy_label.setText("")
			self.ui.force_factor.setText("")
			self.ui.force_init1.setText("")
			self.ui.force_init2.setText("")
			self.ui.force_init3.setText("")
			return
		self.setEnabled(True)
		self.ui.num_trained_label.setText(str(self.judged_main_num))
		if self.accuracy >= 0:
			# round number
			self.ui.accuracy_label.setText(
				str("%.0f%%")%(self.accuracy+0.5))
		else:
			self.ui.accuracy_label.setText("")
		if self.force_factor > 1.0:
			self.ui.force_factor.setText(
				str("%.2f")%self.force_factor)
		else:
			self.ui.force_factor.setText("")
		if self.force_init[0] >= 0:
			self.ui.force_init1.setText(
				str("%.1f N")%self.force_init[0])
		else:
			self.ui.force_init1.setText("")
		if self.force_init[1] >= 0:
			self.ui.force_init2.setText(
				str("%.1f N")%self.force_init[1])
		else:
			self.ui.force_init2.setText("")
		if self.force_init[2] >= 0:
			self.ui.force_init3.setText(
				str("%.1f N")%self.force_init[2])
		else:
			self.ui.force_init3.setText("")
	
		if self.modified_training:
			self.ui.num_trained_label.setBackgroundRole(
				QtGui.QPalette.Highlight)
		else:
			self.ui.num_trained_label.setBackgroundRole(
				QtGui.QPalette.Window)
		if self.modified_accuracy:
			self.ui.accuracy_label.setBackgroundRole(
				QtGui.QPalette.Highlight)
		else:
			self.ui.accuracy_label.setBackgroundRole(
				QtGui.QPalette.Window)
		if self.modified_stable:
			self.ui.force_factor.setBackgroundRole(
				QtGui.QPalette.Highlight)
		else:
			self.ui.force_factor.setBackgroundRole(
				QtGui.QPalette.Window)
		if self.modified_attack:
			self.ui.force_init1.setBackgroundRole(
				QtGui.QPalette.Highlight)
			self.ui.force_init2.setBackgroundRole(
				QtGui.QPalette.Highlight)
			self.ui.force_init3.setBackgroundRole(
				QtGui.QPalette.Highlight)
		else:
			self.ui.force_init1.setBackgroundRole(
				QtGui.QPalette.Window)
			self.ui.force_init2.setBackgroundRole(
				QtGui.QPalette.Window)
			self.ui.force_init3.setBackgroundRole(
				QtGui.QPalette.Window)

	def set_modified(self):
		self.modified_training = True
		self.modified_accuracy = True
		self.modified_stable = True
		self.modified_attack = True
		self.display()

	def read(self):
		### read collection
		for cat_type in [collection.CATS_MAIN, collection.CATS_WEIRD]:
			cat_text = self.coll.get_cat_text(cat_type)
			filename = shared.files.get_mf_filename(
				self.st, cat_text, self.dyn)
			self.coll.add_mf_file(filename)
		self.judged_main_num = self.coll.num_main()
		### read forces
		filename = shared.files.get_forces_filename(self.st, self.dyn)
		try:
			att = open(filename).readlines()
			for i in range(3):
				self.force_init.append(float( att[i].rstrip() ))
			self.force_factor = float( att[3].rstrip() )
		except:
			# we don't care if we can't read the forces file.
			self.force_init = [-1.0, -1.0, -1.0]
			self.force_factor = 1.0
		# do we need any basic training?
		shared.basic.set_collection(self.st, self.dyn, self.coll)
		if not shared.basic.get_next_basic():
			self.basic_trained = True
		self.display()

	def write(self):
		### write collection
		for cat_type in [collection.CATS_WEIRD, collection.CATS_MAIN]:
			cat_text = self.coll.get_cat_text(cat_type)
			filename = shared.files.get_mf_filename(
				self.st, cat_text, self.dyn)
			self.coll.write_mf_file(filename, cat_type)
		#self.modified = False
		### write forces
		filename = shared.files.get_forces_filename(self.st, self.dyn)
		att = open(filename, 'w')
		for i in range(3):
			att.write(str("%.3f\n" % self.force_init[i]))
		att.write(str("%.3f\n" % self.force_factor))
		att.close()

	### bulk processing state
	def process_step_emit(self):
		self.process_step.emit()
		self.state.step()

	def start(self):
		self.state.start()

	def next_step(self, job_type, job_index):
		if job_type == state.SVM:
			cat_text = self.coll.get_cat_text(
				collection.CATS_MAIN)
			mf_filename = shared.files.get_mf_filename(
				self.st, cat_text, self.dyn)
			self.dyn_backend.compute_training(mf_filename)
		elif job_type == state.ACCURACY:
			self.dyn_backend.check_accuracy(self.coll)
		elif job_type == state.STABLE:
			low_force = min(self.get_forces(2))
			# get mean.  TODO: use a library or util function
			middle_force_list = self.get_forces(3)
			middle_force = sum(middle_force_list) / len(middle_force_list)
			#
			high_force = max(self.get_forces(4))
			self.dyn_backend.learn_stable([low_force, middle_force, high_force])
		elif job_type == state.ACCURACY:
			self.learn_accuracy()
		else:
			print "ERROR dyn_train: job type not recognized!"


	def finished_step(self, job_type, job_index):
		if job_type == state.SVM:
			self.modified_training = False
		elif job_type == state.ACCURACY:
			self.accuracy = self.dyn_backend.accuracy
			self.modified_accuracy = False
		self.display()


	### basic training
	def has_basic_training(self):
		return self.basic_trained

# FIXME: need to revise basic trainig for new State() object
	def basic_train(self):
		if self.basic_trained:
			self.process_step.emit()
			return
		shared.basic.set_collection(self.st, self.dyn, self.coll)
		shared.judge.judged_cat.connect(self.judged_cat)
		self.state = STATE_BASIC_TRAINING
		self.basic_train_next()

	def basic_train_next(self):
		# FIXME: train_params now only gives force and finger_midi
		train_params = shared.basic.get_next_basic()
		if not train_params:
			return self.basic_train_end()
		print train_params
		# FIXME: train_params now only gives force and finger_midi
		self.train_filename = shared.files.make_audio_filename(params)
		physical = self.controller.get_physical_params(params)
		self.controller.basic(
			physical, BASIC_SECONDS, BASIC_SKIP,
			self.train_filename[0:-4])
		shared.judge.user_judge(self.train_filename)

	def basic_train_end(self):
		self.basic_trained = True
		self.state = STATE_NULL
		shared.judge.judged_cat.disconnect(self.judged_cat)
		shared.judge.display(show=False)
		self.process_step.emit()

	def judged_cat(self, cat):
		if self.state == STATE_BASIC_TRAINING:
			if cat >= 0:
				self.coll.add_item(self.train_filename,
					collection.categories[cat-1])
				if cat <= 5:
					self.judged_main_num += 1
					self.set_modified()
				self.basic_train_next()
			else:
				os.remove(self.train_filename)
				os.remove(self.train_filename.replace(".wav",
					".actions"))
				self.basic_train_end()


#		if not self.ears:
#			if self.judged_main_num > 0:
#				self.ears = ears.Ears()
#				shared.listen[self.st][self.dyn] = self.ears
#				self.dyn_backend.reload_ears()

#
#	def has_basic_level(self):
#		return self.levels.hasLevel(self.level)
#
#	def get_train_level(self):
#		self.levels.set_level(self.level)
#		return self.basic_train_next()
#
#	def basic_train_next(self):
#		lp, force = self.levels.basic_train_next()
#		params = shared.AudioParams(self.st, lp.finger,
#			lp.bow_position, force, lp.bow_velocity)
#		return [params]
#
#	def train_init(self, audio_params):
#		actions = vivi_controller.PhysicalActions()
#		actions.string_number = audio_params.st
#		actions.finger_midi = audio_params.finger
#		actions.bow_bridge_distance = audio_params.bow_position
#		actions.bow_force = audio_params.bow_force
#		actions.bow_velocity = audio_params.bow_velocity
#
#		self.actions = actions
#		self.train_filename = shared.files.make_audio_filename(audio_params)
#		self.controller.basic(
#			self.actions, BASIC_SECONDS, BASIC_SKIP,
#			self.train_filename[0:-4])
#		#self.train_filename = self.perform.make_basic_audio(
#		#	audio_params, BASIC_PARAMS)
#
#		shared.judge.user_judge(self.train_filename, self.coll)
#
#	def train_reinit(self, wavfile):
#		self.train_filename = wavfile
#
#	def train_end(self):
#		self.train_filename = ''
#		self.judged_main = self.coll.num_main()
#
#	def opinion(self, key):
#		if (key > '0') and (key < str(len(collection.categories)+1)):
#			cat = int(key)
#			self.coll.add_item(self.train_filename,
#				collection.categories[cat-1])
#			self.set_modified()
#			#if self.coll.is_cat(key, collection.CATS_MAIN):
#			#	self.modified_out = True
#			self.train_end()
#			return OPINION_END
#		if (key == '9'):
#			self.train_end()
#			return OPINION_QUIT
#		return OPINION_CONTINUE
#
##	def get_cat_message(self):
##		if not self.train_filename:
##			return "Oops!  Can't train nothing"
##		text = ''
##		text += "   This violin note needs ______ bow force.\n"
##		text += " "
##		for i in range(len(collection.categories)):
##			text += "  "+ collection.categories[i]
##		text += "\n"
##		#text += "        (numbers 2 and 4 are identical)\n"
##		text += "        9 will quit"
##		return text
#
	def compute_training_steps(self):
		if self.judged_main_num == 0:
			return 0
		elif not self.modified_training:
			return 0
		num_steps = self.dyn_backend.compute_training_steps()
		self.state.prep(state.SVM, [num_steps])
		return num_steps

	def check_accuracy_steps(self):
		if self.judged_main_num == 0:
			return 0
		elif not self.modified_accuracy:
			return 0
		num_steps = self.dyn_backend.check_accuracy_steps()
		self.state.prep(state.ACCURACY, [num_steps])
		return num_steps

	def learn_attacks_steps(self):
		if self.judged_main_num == 0:
			return 0
		elif not self.modified_attack:
			return 0
		num_steps = self.dyn_backend.learn_attacks_steps()
		self.state.prep(state.ACCURACY, [num_steps])
		return num_steps

	def learn_stable_steps(self):
		if self.judged_main_num == 0:
			return 0
		elif not self.modified_stable:
			return 0
		num_steps = self.dyn_backend.learn_stable_steps()
		self.state.prep(state.STABLE, [num_steps])
		return num_steps

#	def learn_attacks(self):
#		if self.judged_main_num == 0:
#			return 0
#		elif not self.modified_attack:
#			return 0
#		print "Learning attacks dyn train", self.st, self.dyn
		#matches = self.levels.get_pairs_on_level(self.level)
#		print matches
#		force_max = 0.01
#		force_min = 100.0
#		for pair in matches:
#			audio_params = shared.files.get_audio_params(pair[0])
#			force = audio_params.bow_force
#			if force_max < force:
#				force_max = force
#			if force_min > force:
#				force_min = force
#		self.dyn_backend.learn_attacks(force_min, force_max)

	def get_forces(self, cat):
		forces = map(
			lambda(x): shared.files.get_audio_params(x[0]).bow_force,
			self.coll.get_items(cat))
		return forces



#	def process_step_emit(self):
#		if self.dyn_backend.state > 0:
#			self.process_step.emit()
#			return
#
#		if self.dyn_backend.did == dyn_backend.CALCULATE_TRAINING:
#			self.modified_training = False
#		if self.dyn_backend.did == dyn_backend.CHECK_ACCURACY:
#			self.accuracy = self.dyn_backend.accuracy
#			self.accuracy_data = self.dyn_backend.accuracy_data
#			self.modified_accuracy = False
#		if self.dyn_backend.did == dyn_backend.LEARN_STABLE:
#			self.force_factor = self.dyn_backend.force_factor
#			self.modified_stable = False
#		if self.dyn_backend.did == dyn_backend.LEARN_ATTACKS:
#			self.force_init = self.dyn_backend.force_init
#			self.modified_attack = False
#
#		self.display()
#		self.process_step.emit()
#
	def click(self, event):
		print "dynamic clicked"
#		shared.compare.compare(self.st, self.dyn,
#			self.accuracy, self.coll)
#

#	def delete_file(self, wavfile):
#		self.coll.delete(wavfile)
#		self.set_modified()
#		self.display()
#


