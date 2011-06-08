#!/usr/bin/env python
""" base class for Task_* """

import dynamics
import dirs

class TaskBase():
	""" base class for Task_* """

	def __init__(self, st, dyn, controller, emit, taskname):
		""" constructor """
		self.st = st
		self.dyn = dyn
		self.controller = controller
		self.process_step = emit
		self.taskname = taskname

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
		self._remove_previous_files()
		self._make_files()
		final_answer = self._examine_files()
		return final_answer

	def _make_files(self):
		pass

	def _examine_files(self):
		pass

	def _get_files(self):
		return dirs.files.get_task_files(self.taskname, self.st,
			dynamics.get_distance(self.dyn), dynamics.get_velocity(self.dyn))

	def _setup_controller(self):
		self.controller.load_ears_training(self.st, self.dyn,
			dirs.files.get_mpl_filename(self.st, 'main', self.dyn))


