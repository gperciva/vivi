#!/usr/bin/env python

import dirs

import vivi_controller
import dynamics
import controller_params

import basic_training # for FINGER_MIDIS
import utils

class Note():
    def __init__(self, begin=None, duration=0, pizz=False,
            end=None, point_and_click=None, details=None):
        self.begin = begin
        self.duration = duration
        self.pizz = pizz
        self.end = end
        self.point_and_click = point_and_click
        self.details = details
class Rest():
    def __init__(self, duration=0):
        self.duration = duration

class StyleBase():
    def __init__(self):
        self.notes = None
        self.last_seconds = 0.0

        self.controller_params = []
        for st in range(4):
            st_controllers = []
            for dyn in range(4):
                dyn_filename = dirs.files.get_dyn_vivi_filename(st, dyn)
                st_controllers.append(controller_params.ControllerParams(dyn_filename))
            self.controller_params.append(st_controllers)
        self.reload_params()

    @staticmethod
    def is_note(note):
        return isinstance(note, Note)

    def reload_params(self):
        for st in range(4):
            for dyn in range(4):
                self.controller_params[st][dyn].load_file()

    def plan_perform(self, events):
        """ main method which turns events into self.notes """
        pass

    def get_details(self, note, text):
        details = []
        for detail in note.details:
            if detail[0] == text:
                details.append(detail[1])
        return details

    @staticmethod
    def pair(values):
        return zip(values[:-1], values[1:])



    def get_simple_force(self, st, finger_position, dyn):
        # TODO: this function is icky
        low_index = 0
        high_index = 0
        # ASSUME: FINGER_MIDIS is already sorted
        fm = utils.pos2midi(finger_position)
        for i, val in enumerate(basic_training.FINGER_MIDIS):
            if fm >= val:
                low_index = i
                high_index = i+1
        if high_index >= len(basic_training.FINGER_MIDIS):
            high_index = len(basic_training.FINGER_MIDIS) - 1
        force = utils.interpolate(fm,
            basic_training.FINGER_MIDIS[low_index],
            self.controller_params[st][int(dyn+0.5)].get_attack_force(low_index),
            basic_training.FINGER_MIDIS[high_index],
            self.controller_params[st][int(dyn+0.5)].get_attack_force(high_index))
        return force

    def get_finger(self, pitch, which_string):
        finger_semitones = pitch - (55 + 7*which_string)
        position = self.semitones(finger_semitones)
        return position

    def get_naive_string(self,pitch):
        if (pitch < 62):
            return 0
        elif (pitch < 69):
            return 1
        elif (pitch < 76):
            return 2
        else:
            return 3

    def semitones(self, num):
        return 1.0 - 1.0 / (1.05946309**num)


