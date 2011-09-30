#!/usr/bin/env python
""" base class for Task_* """

import dynamics
import dirs
import scipy

class TaskBase():
	""" base class for Task_* """

	def __init__(self, st, dyn, controller, emit, taskname):
		""" constructor """
		self.st = st
		self.dyn = dyn
		self.controller = controller
		self.process_step = emit
		self.taskname = taskname

		self.STEPS = 10 # even number to avoid picking the
				# same value on second pass
		self.REPS = 2

		self.LOW_INIT = 0.0 # blah numbers to start with
		self.HIGH_INIT = 1.0
		self.low_variable = self.LOW_INIT
		self.high_variable = self.HIGH_INIT
		self.test_range = None

	def _remove_previous_files(self):
		""" remove files from previous computation of task """
		dirs.files.delete_files(
			dirs.files.get_task_files(self.taskname, self.st,
				dynamics.get_distance(self.dyn),
				dynamics.get_velocity(self.dyn)))

	def steps_full(self):
		return 0

	def calculate_full(self):
		""" does a full (re)calculation of the task """
		self._init_range()
		self._remove_previous_files()
		self._make_files()
		first_answer_index, first_answer = self._examine_files()
		self._zoom_range(first_answer_index)
		self._make_files()
		# TODO: second_answer_index is not trustworthy!
		second_answer_index, second_answer = self._examine_files()
		return second_answer

	def _init_range(self):
		self.low_variable = self.LOW_INIT
		self.high_variable = self.HIGH_INIT
		self.test_range = scipy.linspace(self.low_variable,
                                self.high_variable, self.STEPS)

	def _make_files(self):
		pass

	def _examine_files(self):
		pass

	def _zoom_range(self, index):
		# only update if it's in the range
		if (index-1) > 0:
			self.low_variable = self.test_range[index-1]
		if (index+1) < len(self.test_range)-1:
			self.high_variable = self.test_range[index+1]
		#print self.st, self.test_range
		#print self.st, index
		self.test_range = scipy.linspace(self.low_variable,
                                self.high_variable, self.STEPS)
		#print self.st, self.test_range

	def _get_files(self):
		return dirs.files.get_task_files(self.taskname, self.st,
			dynamics.get_distance(self.dyn), dynamics.get_velocity(self.dyn))

	def _setup_controller(self):
		self.controller.load_ears_training(self.st, self.dyn,
			dirs.files.get_mpl_filename(self.st, self.dyn))


