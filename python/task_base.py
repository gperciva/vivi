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
		bbd = dynamics.get_distance(self.dyn)
		bv  = dynamics.get_velocity(self.dyn)
		dirs.files.delete_files(
			dirs.files.get_task_files(self.taskname, self.st, bbd, bv))

	def calculate_full(self):
		""" does a full (re)calculation of the task """
		self._remove_previous_files()
		self._make_files()
		final_answer = self._examine_files()
		return final_answer



