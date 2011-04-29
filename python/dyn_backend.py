#!/usr/bin/env python

import subprocess
#import levels

#import utils
import shared

#import check_coll
#import attacks
import vivi_controller

import utils

#import scipy
import operator

import math
import scipy

CALCULATE_TRAINING = 1
CHECK_ACCURACY = 2
LEARN_ATTACKS = 3
LEARN_STABLE = 4

ATTACK_FORCE_STEPS = 10

STABLE_STEPS = 3
STABLE_REPS = 3
STABLE_MIN = 1.00
STABLE_MAX = 1.20

from PyQt4 import QtCore

class DynBackend(QtCore.QThread):
	process_step = QtCore.pyqtSignal()

	def __init__(self, st, dyn, level, accuracy, force_init, force_factor, controller, practice):
		QtCore.QThread.__init__(self)

		self.st = st
		self.dyn = dyn
		self.level = level
		#self.performer = performer
		#self.ears = shared.listen[self.st][self.dyn]
		self.controller = controller
		self.ears = self.controller.getEars(self.st, self.dyn)

		#self.practice = practice


		#self.check_coll = check_coll.CheckColl(ears)
		self.accuracy = -1.0

		#self.attacks = attacks.Attacks(self.st,
	#		self.dyn, self.level, performer)
		self.force_init = force_init
		self.force_factor = force_factor


		self.mutex = QtCore.QMutex()
		self.condition = QtCore.QWaitCondition()
		self.state = 0
		self.did = 0
		self.start()

	def reload_ears(self):
#		self.ears = shared.listen[self.st][self.dyn]
		self.ears.reset()

	def run(self):
		while True:
			self.mutex.lock()
			self.condition.wait(self.mutex)
			self.did = 0
			if self.state == CALCULATE_TRAINING:
				self.compute_thread()
			elif self.state == CHECK_ACCURACY:
				self.check_accuracy_thread()
			elif self.state == LEARN_ATTACKS:
				self.learn_attacks_thread()
			elif self.state == LEARN_STABLE:
				self.learn_stable_thread()
			self.did = self.state
			self.state = 0
			self.process_step.emit()
			self.mutex.unlock()

	def compute_training_steps(self):
		return 1 

	def compute_training(self, mf_filename):
		self.state = CALCULATE_TRAINING
		self.mf_filename = mf_filename
		self.condition.wakeOne()

	def compute_thread(self):
		self.ears.reset()
		arff_filename = shared.files.get_arff_filename(
			self.st, 'main', self.dyn)
		mpl_filename = shared.files.get_mpl_filename(
			self.st, 'main', self.dyn)

		self.ears.set_training(self.mf_filename, arff_filename)
		self.ears.processFile()
		#self.process_step.emit()
		self.ears.saveTraining(mpl_filename)

		self.accuracy = -1.0

	def check_accuracy_steps(self, coll):
		self.coll_accuracy = coll
		return 2 + len(self.coll_accuracy.coll)

	def check_accuracy(self):
		self.state = CHECK_ACCURACY
		self.condition.wakeOne()

	def check_accuracy_thread(self):
		### find overall 10-fold cross-validation accuracy
		cmd = "kea -cl SVM -w %s" % (
			shared.files.get_arff_filename(
				self.st, 'main', self.dyn))
		process = subprocess.Popen(cmd, shell=True,
			stdout=subprocess.PIPE)
		kea_output = process.communicate()
		self.process_step.emit()
		# could be done better
		for line in kea_output[0].split('\n'):
			if line.find("Correctly Classified Instances") >= 0:
				splitline = line.split()
				self.accuracy = float(splitline[4])
		### calculate cats for each file
		mpl_filename = shared.files.get_mpl_filename(
			self.st, 'main', self.dyn)
		self.ears.reset()
		self.ears.set_predict_wavfile(mpl_filename)
		for pair in self.coll_accuracy.coll:
			filename = pair[0]
			cat_out = shared.files.get_cats_name(filename[0:-4])+'.cats'
			#
			self.ears.predict_wavfile(filename, cat_out)
			self.process_step.emit()


	def learn_attacks_steps(self):
		return 3*2*ATTACK_FORCE_STEPS + 1

	def learn_attacks(self, min_force, max_force):
		self.performer.load_forces()
		self.attack_min = min_force
		self.attack_max = max_force
		self.state = LEARN_ATTACKS
		self.condition.wakeOne()

	def learn_stable_steps(self):
		#return 2 * STABLE_STEPS + 1
		return (STABLE_STEPS * STABLE_REPS * 3) + 1

	def learn_stable(self, stable_forces):
		self.state = LEARN_STABLE
		self.stable_forces = stable_forces
		self.condition.wakeOne()

	def learn_stable_thread(self):
		mpl_filename = shared.files.get_mpl_filename(
			self.st, 'main', self.dyn)
		self.controller.load_ears_training(self.st, self.dyn,
			mpl_filename)

		for K in scipy.linspace(STABLE_MIN, STABLE_MAX, STABLE_STEPS):
			# start counting at 1 due to "if 0" in training_dir
			for count in range(1,STABLE_REPS+1):
				for fi in range(3):
					bow_direction = 1
					bow_force = self.stable_forces[fi]
					# FIXME: oh god ick
					ap = shared.AudioParams( self.st, 0,
						shared.dyns.get_distance(self.dyn),
						bow_force,
						bow_direction*shared.dyns.get_velocity(self.dyn))
					stable_filename = shared.files.make_stable_filename(
						ap, K, count)

					self.controller.filesNew(stable_filename)
					for fmi, finger_midi in enumerate(shared.basic_training.finger_midis):
						self.controller.comment("stable st %i dyn %i finger_midi_index %i finger_midi %.3f"
							% (self.st, self.dyn, fmi, finger_midi))
						self.make_stable(K, count, bow_force, finger_midi, bow_direction)
						bow_direction *= -1
					self.controller.filesClose()
					self.process_step.emit()



	def make_stable(self, K, count, bow_force, finger_midi, bow_direction):
		PLAY_LENGTH = 0.75
		params = vivi_controller.PhysicalActions()
		params.string_number = self.st
		params.dynamic = self.dyn
		params.finger_position = utils.midi2pos(finger_midi)
		params.bow_force = bow_force
		params.bow_bridge_distance = shared.dyns.get_distance(self.dyn)
		params.bow_velocity = bow_direction * shared.dyns.get_velocity(self.dyn)

		self.controller.note(params, K, PLAY_LENGTH)

#zz
	### interface with controller
	def get_physical_params(self, audio_params):
		physical = vivi_controller.PhysicalActions()
		physical.string_number = audio_params.string_number
		physical.dynamic = self.dyn
		physical.finger_position = utils.midi2pos(audio_params.finger_midi)
		physical.bow_bridge_distance = audio_params.bow_bridge_distance
		physical.bow_force = audio_params.bow_force
		physical.bow_velocity = audio_params.bow_velocity
		return physical



		return

		self.practice.set_string_dyn(self.st, self.dyn,
			mpl_filename)

		lp = levels.level_params[self.level][0]
		bow_position = lp.bow_position
		bow_velocity = lp.bow_velocity

		ff_stats = []
		mult_stable = (STABLE_MAX/STABLE_MIN)**(1.0/ (
			STABLE_STEPS-1))
		#step_size = (STABLE_MAX-STABLE_MIN)/float(STABLE_STEPS)
		for f in range(STABLE_STEPS):
			#ff = STABLE_MIN + (f)*step_size
			ff = STABLE_MIN * mult_stable ** (f)
			med = self.practice.stable(
				self.dyn,
				bow_position,
				bow_velocity,
				ff,
				self.force_max)
			self.process_step.emit()
			ff_stats.append( (med, ff) )
		ff_stats.sort()

		# get biggest
#		ff_min = ff_stats[-1][1] / mult_stable
#		ff_max = ff_stats[-1][1] * mult_stable
#		if ff_min < STABLE_MIN:
#			ff_min = STABLE_MIN
#		if ff_max > STABLE_MAX:
#			ff_max = STABLE_MAX

		## zoom in
#		print "%i zooming in on: %.2f %.2f" %(self.st, ff_min, ff_max)
#		step_size = (ff_max-ff_min)/float(STABLE_STEPS)
#		for f in range(STABLE_STEPS):
#			ff = ff_min + (f)*step_size
#			med = self.practice.stable(
#				self.dyn,
#				bow_position,
#				bow_velocity,
#				ff,
#				self.force_min, self.force_max)
#			self.process_step.emit()
#			ff_stats.append( (med, ff) )
#		ff_stats.sort()

		#print "st %i force_factor:\t%.3f" % (self.st, lowest_ff)
		# get biggest
#		self.force_factor = ff_stats[-1][1]
		# get smallest
		self.force_factor = ff_stats[0][1]

		#print "st %i force_factor %.3f" %(self.st, self.force_factor)
#		lowest_std = 999.0 # infinity
#		for stats in ff_stats:
#			if lowest_std > stats[2]:
#				lowest_std = stats[2]
#		lowest_force =
#		for stats in ff_stats:
#			if stats[2] > lowest_std*2:
#				continue
				
		log = open('stable-%i-%i.txt'%(self.st, self.dyn), 'w')
		logdata = str("# forces:\t%.3f\t%.3f\n" % (
			self.force_min, self.force_max))
		log.write(logdata)
		log.write("#st\tff\tmedian\tvalues\n")
		ff_stats = sorted(ff_stats, key=operator.itemgetter(1))
		for stats in ff_stats:
			ff = stats[1]
			med = stats[0]
			logdata = str("%i\t%.3f\t%.3g\t" % (
				self.st, ff, med))
			log.write(logdata)
			#for fr in stats[2]:
			#	log.write(str("%.3g\t"%fr))
			log.write('\n')
		log.close()




	def learn_attacks_thread(self):
		return
		# need to reload training files from disk
		mpl_filename = shared.files.get_mpl_filename(
			self.st, 'main', self.dyn)
		self.practice.set_string_dyn(self.st, self.dyn,
			mpl_filename)
#		self.performer.make_listen()

		# extra [0] because lp is currently a list
		# of singleton lists.  :(
		# however, both items in the list have the same
		# position and velocity
		lp = levels.level_params[self.level][0]
		bow_pos = lp.bow_position
		bow_vel = lp.bow_velocity

		#print "# learning attacks\t%i\t%.3f\t%.3f" % (st,
		#	bow_pos, bow_vel)
		self.bow_st = self.st
		self.bow_position = bow_pos
		self.target_velocity = bow_vel

		for fi, finger in enumerate([0, 4, 7]):
			hops_list = []
			min_force = self.attack_min
			max_force = self.attack_max
			mult_force = (max_force/min_force)**(1.0/ (
				ATTACK_FORCE_STEPS-1))
			#add_force = (max_force-min_force) / (force_steps-1)

			for i in range(ATTACK_FORCE_STEPS):
				force = min_force * mult_force**(i)
#				print self.st, self.dyn, force
				num = self.practice.attack(self.dyn,
					self.bow_position, force,
					self.target_velocity,
					self.force_factor,
					finger)
				hops_list.append( (num, force) )
				self.process_step.emit()
			hops_list.sort()

			# get smallest
			max_force = hops_list[0][1] * mult_force
			min_force = hops_list[0][1] / mult_force
			#print self.st, max_force, min_force
			if min_force < self.attack_min:
				min_force = self.attack_min
			if max_force > self.attack_max:
				max_force = self.attack_max

			#mult_force = (max_force/min_force)**(1.0/(force_steps-1))
			add_force = (max_force-min_force) / (
				ATTACK_FORCE_STEPS-1)
			for i in range(ATTACK_FORCE_STEPS):
				#force = min_force * mult_force**(i)
				force = min_force + add_force*(i)
				num = self.practice.attack(self.dyn,
					self.bow_position, force,
					self.target_velocity,
					self.force_factor,
					finger)
				hops_list.append( (num, force) )
				self.process_step.emit()

			log = open('attack-%i-%i-%i.txt'%(
				self.st, self.dyn, finger), 'w')
			tolog = sorted(hops_list, key=operator.itemgetter(1))
			for t in tolog:
				log.write("%.3f\t%.3f\n" %(
					t[1], t[0]))
			log.close()
			hops_list.sort()
			if hops_list[0][0] == 0:
				self.force_init[fi] = -1.0
			else:
				self.force_init[fi] = hops_list[0][1]

