#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import dyn_train_gui

import collection

import scipy

import basic_training

import os # to delete audio files whose judgement was cancelled

#import levels
import utils
import vivi_types

# TODO: **must** import ears first, then controller.  No clue why.
#import ears

import dirs
# TODO: **must** import this first, then controller.  No clue why.
import vivi_controller
import dynamics
import controller_params
#import vivi_controller

#import utils
import shared

import state

import dyn_backend
#import ears

import examine_auto_widget
import compare_coll


# just for BASIC_PARAMS; iffy; icky
#import performer
#BASIC_PARAMS = performer.BasicParams(force_std=0.01, velocity_std=0.01,
#	duration_settle=1.0, duration_play=0.5)
BASIC_SECONDS = 0.3
BASIC_SKIP = 0.5

#NEEDS_BASIC_COLOR = "pink"
NEEDS_BASIC_COLOR = "red"


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

		#self.mousePressEvent = self.click
		self.ui.modify.clicked.connect(self.set_modified)
		self.ui.force_factor.clicked.connect(self.click_force_factor)
		self.ui.accuracy_label.clicked.connect(self.click_accuracy)
		self.ui.force_init1.clicked.connect(self.click_force1)
		self.ui.force_init2.clicked.connect(self.click_force2)
		self.ui.force_init3.clicked.connect(self.click_force3)

		### setup variables
		self.judged_main_num = 0
		self.accuracy = -1.0

		self.level = utils.dyn_to_level(self.dyn)

		self.modified_training = False
		self.modified_accuracy = False
		self.modified_stable = False
		self.modified_attack = False

		self.coll = collection.Collection()

		self.basic_trained = False

		self.force_init = []
		self.controller_params = controller_params.ControllerParams(
			dirs.files.get_dyn_vivi_filename(self.st, self.dyn))
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
		# (after self.read() !)
		self.dyn_backend = dyn_backend.DynBackend(
			self.st, self.dyn, self.level, self.accuracy, self.force_init,
			self.force_factor,
			self.controller, self.practice)
		self.dyn_backend.process_step.connect(self.process_step_emit)

		self.state = state.State()
		self.state.next_step.connect(self.next_step)
		self.state.finished_step.connect(self.finished_step)


		self.examine = examine_auto_widget.ExamineAutoWidget(self)
		self.examine.select_note.connect(self.examine_auto_select_note)

		self.compare = compare_coll.CompareColl()
		self.compare.row_delete.connect(self.delete_file)
		self.compare.row_retrain.connect(self.retrain_file)


		self.cancel_will_delete = True

		self.display()



#		try:
#			filename = dirs.files.get_forces_filename(self.st, self.dyn)
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
			self.ui.dyn_type.setText(utils.dyn_to_text(self.dyn))
			self.ui.num_trained_label.setText("")
			self.ui.accuracy_label.setText("")
			self.ui.force_factor.setText("")
			self.ui.force_init1.setText("")
			self.ui.force_init2.setText("")
			self.ui.force_init3.setText("")
			return

		if self.basic_trained:
			self.ui.dyn_type.setText(utils.dyn_to_text(self.dyn))
		else:
			self.ui.dyn_type.setText(
				"<font color=\"%s\">%s</font>" %
				(NEEDS_BASIC_COLOR, utils.dyn_to_text(self.dyn)))

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
			# TODO: really bad way of highlighting!
			# but QPushButtons don't seem
			# to have a nice way to highlight!
			self.ui.accuracy_label.setStyleSheet(
				"background-color: darkBlue; color: white;")
		else:
			self.ui.accuracy_label.setStyleSheet("")

		if self.modified_stable:
			self.ui.force_factor.setStyleSheet(
				"background-color: darkBlue; color: white;")
		else:
			self.ui.force_factor.setStyleSheet("")

		if self.modified_attack:
			self.ui.force_init1.setBackgroundRole(
				QtGui.QPalette.Highlight)
			self.ui.force_init2.setBackgroundRole(
				QtGui.QPalette.Highlight)
			self.ui.force_init3.setBackgroundRole(
				QtGui.QPalette.Highlight)
			# TODO: really bad way of highlighting!
			# but QPushButtons don't seem
			# to have a nice way to highlight!
			self.ui.force_init1.setStyleSheet(
				"background-color: darkBlue; color: white;")
			self.ui.force_init2.setStyleSheet(
				"background-color: darkBlue; color: white;")
			self.ui.force_init3.setStyleSheet(
				"background-color: darkBlue; color: white;")
		else:
			self.ui.force_init1.setBackgroundRole(
				QtGui.QPalette.Window)
			self.ui.force_init2.setBackgroundRole(
				QtGui.QPalette.Window)
			self.ui.force_init3.setBackgroundRole(
				QtGui.QPalette.Window)
			# TODO: really bad way of highlighting!
			# but QPushButtons don't seem
			# to have a nice way to highlight!
			self.ui.force_init1.setStyleSheet(
				"")
			self.ui.force_init2.setStyleSheet(
				"")
			self.ui.force_init3.setStyleSheet(
				"")

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
			filename = dirs.files.get_mf_filename(
				self.st, cat_text, self.dyn)
			self.coll.add_mf_file(filename)
		self.judged_main_num = self.coll.num_main()
		### read forces
		self.controller_params.load_file()
		self.force_init = []
		for i in range(3):
			self.force_init.append(
				self.controller_params.get_attack_force(i))
		self.force_factor = self.controller_params.stable_K
		self.accuracy = self.controller_params.accuracy
#		filename = dirs.files.get_dyn_data_filename(self.st, self.dyn)
#		try:
#			att = open(filename).readlines()
#			for i in range(3):
#				self.force_init.append(float( att[i].rstrip() ))
#			self.force_factor = float( att[3].rstrip() )
#			self.accuracy = float( att[4].rstrip() )
#		except:
#			# we don't care if we can't read the forces file.
#			self.force_init = [-1.0, -1.0, -1.0]
#			self.force_factor = 1.0
		# do we need any basic training?
		if not basic_training.get_next_basic(self.dyn, self.coll):
			self.basic_trained = True
		self.display()

	def write(self):
		### write collection
		for cat_type in [collection.CATS_WEIRD, collection.CATS_MAIN]:
			cat_text = self.coll.get_cat_text(cat_type)
			filename = dirs.files.get_mf_filename(
				self.st, cat_text, self.dyn)
			self.coll.write_mf_file(filename, cat_type)
		#self.modified = False
		### write forces
		for i in range(3):
			self.controller_params.set_force(i, self.force_init[i])
		self.controller_params.stable_K = self.force_factor
		self.controller_params.accuracy = self.accuracy
		self.controller_params.write_file()
#		filename = dirs.files.get_dyn_data_filename(self.st, self.dyn)
#		att = open(filename, 'w')
#		for i in range(3):
#			att.write(str("%.3f\n" % self.force_init[i]))
#		att.write(str("%.3f\n" % self.force_factor))
#		att.write(str("%.3f\n" % self.accuracy))
#		att.close()

	### bulk processing state
	def process_step_emit(self):
		self.process_step.emit()
		#print "dyn train emit", self.st, self.dyn, self.state.jobs, self.state.job_index
		self.state.step()

	def start(self):
		self.state.start()

	def next_step(self, job_type, job_index):
		if job_type == state.BASIC_TRAINING:
			self.basic_train()
		elif job_type == state.SVM:
			cat_text = self.coll.get_cat_text(
				collection.CATS_MAIN)
			mf_filename = dirs.files.get_mf_filename(
				self.st, cat_text, self.dyn)
			self.dyn_backend.compute_training(mf_filename)
		elif job_type == state.ACCURACY:
			self.dyn_backend.check_accuracy()
		elif job_type == state.STABLE:
			finger_forces = []
			for fm in [0, 4, 7]:
				low_force = max(self.get_forces_finger(1, fm))
				middle_force = scipy.mean(self.get_forces_finger(3,fm))
				high_force = min(self.get_forces_finger(5, fm))
				finger_forces.append( [low_force, middle_force, high_force] )
			self.dyn_backend.learn_stable(finger_forces)
		elif job_type == state.ATTACKS:
			finger_forces = []
			for fm in [0, 4, 7]:
				# yes, reversed
				low_force = min(self.get_forces_finger(1, fm))
				middle_force = scipy.mean(self.get_forces_finger(3,fm))
				high_force = max(self.get_forces_finger(5, fm))
				finger_forces.append( [low_force, middle_force, high_force] )
			self.dyn_backend.task_attack.set_K(self.force_factor)
			self.dyn_backend.learn_attacks(finger_forces)
		else:
			print "ERROR dyn_train: job type not recognized!"


	def finished_step(self, job_type, job_index):
		if job_type == state.SVM:
			self.modified_training = False
		elif job_type == state.ACCURACY:
			self.accuracy = self.dyn_backend.accuracy
			self.modified_accuracy = False
		elif job_type == state.STABLE:
			self.force_factor = self.dyn_backend.most_stable
			self.modified_stable = False
		elif job_type == state.ATTACKS:
			# TODO
			self.force_init = self.dyn_backend.best_attack
			self.modified_attack = False
		self.display()


	### basic training
	def has_basic_training(self):
		return self.basic_trained

	def basic_prep(self):
		if self.basic_trained:
			return 0
		num_steps = 1
		self.state.prep(state.BASIC_TRAINING, [num_steps])
		return num_steps

	def basic_train(self):
		shared.judge.judged_cat.connect(self.judged_cat)
		self.basic_train_next()


	def basic_train_next(self):
		train_params = basic_training.get_next_basic(self.dyn, self.coll)
		if not train_params:
			return self.basic_train_end()
		params = vivi_types.AudioParams(
			self.st, train_params[1],
			dynamics.get_distance(self.dyn),
			train_params[0],
			dynamics.get_velocity(self.dyn))

		self.train_filename = dirs.files.make_audio_filename(params)
		physical = self.dyn_backend.get_physical_params(params)
		self.controller.basic(
			physical, BASIC_SECONDS, BASIC_SKIP,
			self.train_filename)
		shared.judge.user_judge(self.train_filename)

	def basic_train_end(self):
		self.basic_trained = True
		self.display()
		shared.judge.judged_cat.disconnect(self.judged_cat)
		shared.judge.display(show=False)
		self.process_step.emit()

	def train_over(self):
		shared.judge.judged_cat.disconnect(self.judged_cat)
		shared.judge.display(show=False)

	def judged_cat(self, cat):
		if cat >= 0:
			self.train_filename = dirs.files.move_works_to_train(
				self.train_filename)
			if self.cancel_will_delete:
				self.coll.add_item(self.train_filename+'.wav',
					collection.CATEGORIES[cat-1])
			else:
				self.coll.add_item(self.train_filename+'.wav',
					collection.CATEGORIES[cat-1], replace=True)
				self.compare.compare(self.st, self.dyn,
					self.accuracy, self.coll)
			if cat <= 5:
				self.judged_main_num = self.coll.num_main()
				self.set_modified()
		else:
			if self.cancel_will_delete:
				os.remove(self.train_filename+".wav")
				os.remove(self.train_filename+".actions")
		if self.state.job_type == state.BASIC_TRAINING:
			if cat >= 0:
				self.basic_train_next()
			else:
				self.basic_train_end()
		else:
			self.train_over()

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
#		self.train_filename = dirs.files.make_audio_filename(audio_params)
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
#		if (key > '0') and (key < str(len(collection.CATEGORIES)+1)):
#			cat = int(key)
#			self.coll.add_item(self.train_filename,
#				collection.CATEGORIES[cat-1])
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
##		for i in range(len(collection.CATEGORIES)):
##			text += "  "+ collection.CATEGORIES[i]
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
		num_steps = self.dyn_backend.check_accuracy_steps(self.coll)
		self.state.prep(state.ACCURACY, [num_steps])
		return num_steps

	def learn_attacks_steps(self):
		if self.judged_main_num == 0:
			return 0
		elif not self.modified_attack:
			return 0
		num_steps = self.dyn_backend.learn_attacks_steps()
		self.state.prep(state.ATTACKS, [num_steps])
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
#			audio_params = dirs.files.get_audio_params(pair[0])
#			force = audio_params.bow_force
#			if force_max < force:
#				force_max = force
#			if force_min > force:
#				force_min = force
#		self.dyn_backend.learn_attacks(force_min, force_max)

	def get_forces_finger(self, cat, finger_midi):
		forces = map(
			lambda(x): dirs.files.get_audio_params(x[0]).bow_force,
			filter(lambda(y):
				dirs.files.get_audio_params(y[0]).finger_midi == finger_midi,
				self.coll.get_items(cat)))
		return forces

	def get_forces(self, cat):
		forces = map(
			lambda(x): dirs.files.get_audio_params(x[0]).bow_force,
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
	def click_accuracy(self, event):
		self.compare.compare(self.st, self.dyn,
			self.accuracy, self.coll)

	def click_force_factor(self, event):
		self.examine.examine("stable", self.st, self.dyn,
			self.dyn_backend.task_stable)

	def examine_auto_select_note(self):
		note_filename_text = self.examine.get_selected_filename()
		if note_filename_text:
			shared.examine_main.load_file(note_filename_text[0])
			shared.examine_main.load_note(note_filename_text[1])


	def train_zoom(self, wavfile, cancel_will_delete=True):
		self.cancel_will_delete = cancel_will_delete
		self.train_filename = wavfile
		shared.judge.judged_cat.connect(self.judged_cat)
		shared.judge.display()
		shared.judge.user_judge(wavfile)

	def delete_file(self, filename):
		self.coll.delete(filename+'.wav')
		self.judged_main_num = self.coll.num_main()
		self.set_modified()
		if not basic_training.get_next_basic(self.dyn, self.coll):
			self.basic_trained = True
		else:
			self.basic_trained = False
		self.display()

	def retrain_file(self, filename):
		# TODO: passing a python string through a signal turns it into a
		# QString.  This changes it back to a python string
		wavfile = str(filename)
#		self.train_zoom(str(filename), cancel_will_delete=False)
		self.cancel_will_delete = False
		self.train_filename = wavfile
		shared.judge.judged_cat.connect(self.judged_cat)
		shared.judge.display(self.compare.ui.verticalLayout)
		shared.judge.user_judge(wavfile)
#zzz


	def click_force1(self):
		self.examine.examine("attack", self.st, self.dyn,
			self.dyn_backend.task_attack, 1)

	def click_force2(self):
		self.examine.examine("attack", self.st, self.dyn,
			self.dyn_backend.task_attack, 2)

	def click_force3(self):
		self.examine.examine("attack", self.st, self.dyn,
			self.dyn_backend.task_attack, 3)

