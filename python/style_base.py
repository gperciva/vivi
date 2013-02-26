#!/usr/bin/env python

import vivi_controller
import dynamics
import controller_params

import basic_training # for FINGER_MIDIS
import utils

import instrument_numbers

class Note():
    def __init__(self, begin=None, duration=0, pizz=False,
            end=None, point_and_click=None, details=None):
        self.begin = begin
        self.duration = duration
        self.pizz = pizz
        self.end = end
        self.point_and_click = point_and_click
        self.details = details
        self.let_string_vibrate = False

class Rest():
    def __init__(self, duration=0):
        self.duration = duration

class StyleBase():
    def __init__(self, inst_type, inst_num, files):
        self.inst_type = inst_type
        self.inst_num = inst_num
        self.files = files
        self.notes = None
        self.last_seconds = 0.0

        self.controller_params = []
        for st in range(4):
            st_controllers = []
            for dyn in range(dynamics.NUM_DYNAMICS):
                dyn_filename = self.files.get_dyn_vivi_filename(st, dyn,
                    inst_num)
                st_controllers.append(controller_params.ControllerParams(dyn_filename))
            self.controller_params.append(st_controllers)
        self.reload_params()

    @staticmethod
    def is_note(note):
        return isinstance(note, Note)

    def reload_params(self):
        for st in range(4):
            for dyn in range(dynamics.NUM_DYNAMICS):
                self.controller_params[st][dyn].load_file()
                #print self.controller_params[st][dyn].get_attack_force(0)

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
        #print force
        return force

    def get_finger(self, pitch, which_string):
        string_pitch = instrument_numbers.INSTRUMENT_TYPE_STRING_PITCHES[
            self.inst_type][which_string]
        finger_semitones = pitch - string_pitch
        position = self.semitones(finger_semitones)
        return position

    def get_naive_string(self,pitch):
        return instrument_numbers.get_string(
            self.inst_type, pitch)

    def semitones(self, num):
        return 1.0 - 1.0 / (1.05946309**num)


