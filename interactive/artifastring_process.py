#!/usr/bin/env python

### load artifastring from build dir if exists
import sys
sys.path.append('../build/swig')
sys.path.append('../build/.libs')

import artifastring_instrument
ARTIFASTRING_SAMPLE_RATE = artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE
HAPTIC_DOWNSAMPLE_FACTOR = artifastring_instrument.HAPTIC_DOWNSAMPLE_FACTOR

import vivi_controller

import actions_file
import collections
import monowav
import midi_pos

import enum
COMMANDS = enum.enum('BOW', 'FINGER', 'TENSION', 'UNSAFE', 'RESET')

ArtifastringInit = collections.namedtuple('ArtifastringInit', """
    instrument_type,
    instrument_number,
    """)

HOPSIZE = artifastring_instrument.NORMAL_BUFFER_SIZE;


import os
### portaudio should use plughw
os.environ['PA_ALSA_PLUGHW'] = '1'
import pyaudio

def make_audio_stream():
    pyaudio_obj = pyaudio.PyAudio()
    audio_stream = pyaudio_obj.open(
        rate = ARTIFASTRING_SAMPLE_RATE,
        channels = 1,
        format = pyaudio.paInt16,
        input=False,
        output = True,
        #output_device_index = 0,
        frames_per_buffer=HOPSIZE,
        )
    return pyaudio_obj, audio_stream

def handle_command(vivi, commands_pipe, logfile, samples):
    command = commands_pipe.recv()
    #print command
    if command[0] == COMMANDS.RESET:
        vivi.reset(True)
        return None
    params = command[1]
    return params

def violin_process(artifastring_init, commands_pipe, audio_pipe):
    try:
        pyaudio_obj, audio_stream = make_audio_stream()
    except:
        pyaudio_obj = None
        audio_stream = None

    vivi = vivi_controller.ViviController(
        artifastring_init.instrument_type,
        artifastring_init.instrument_number)
    if artifastring_init.instrument_type == 0:
        base_midi = 55
        inst = "violin"
    elif artifastring_init.instrument_type == 1:
        base_midi = 48
        inst = "viola"
    elif artifastring_init.instrument_type == 2:
        base_midi = 36
        inst = "cello"
    vivi.filesNew("test-interactive")
    for st in range(4):
        vivi.load_ears_training(st, "../final/%s/%i.mpl" % (inst, st))
        for dyn in range(4):
            for fmi in range(3):
                vivi.set_stable_K(st, dyn, fmi, 1.2)
    audio_buf = monowav.shortArray(HOPSIZE)

    samples = 0

    logfile = actions_file.ActionsFile("log-interactive.actions")
    physical = vivi_controller.PhysicalActions()
    params = None
    while commands_pipe.poll():
        params = handle_command(vivi, commands_pipe, logfile, samples)
        if params is None:
            continue
        physical.string_number = params.violin_string
        physical.finger_position = params.finger_position
        physical.bow_force = params.force
        physical.dynamic = 0
        physical.bow_bridge_distance = params.bow_position
        physical.bow_velocity = params.velocity

        midi_target = base_midi + (7*params.violin_string
                + midi_pos.pos2midi(physical.finger_position))

    #pc = violin.get_physical_constants(params.violin_string)
    #commands_pipe.send( (TENSION, pc.T) )

    while True:

        while commands_pipe.poll():
            params = handle_command(vivi, commands_pipe, logfile, samples)
            #vivi.comment("st, force: %i %.3f" % 
            #    (params.violin_string, params.force))
            if params is None:
                continue
            physical.string_number = params.violin_string
            physical.finger_position = params.finger_position
            physical.bow_force = params.force
            physical.dynamic = 0
            physical.bow_bridge_distance = params.bow_position
            physical.bow_velocity = params.velocity

            midi_target = base_midi + (7*params.violin_string
                + round(midi_pos.pos2midi(physical.finger_position)))
            vivi.continuous(audio_buf.cast(), physical, midi_target, False)
        arr, forces = audio_pipe.recv()
        if arr is None:
            # poison pill
            break

        if physical.string_number >= 0:
            vivi.comment("new force: %.3f" % physical.bow_force)
        vivi.continuous(audio_buf.cast(), physical, midi_target, True)
        physical.string_number = -1
        for i in xrange(HOPSIZE):
            arr[i] = audio_buf[i]
           # vivi_controller.buffer_get(audio_buf, i)

        #vivi.wait_samples_forces_python(arr, forces)
        #unsafe = violin.wait_samples_forces_python(arr, forces)
        #params_log.write("unsafe: %i" % unsafe)
        #commands_pipe.send( (COMMANDS.UNSAFE, unsafe) )
        if audio_stream is not None:
            audio_stream.write( arr.tostring(), HOPSIZE )
        audio_pipe.send( (arr, forces) )
        samples += HOPSIZE
    logfile.wait(float(samples)/ARTIFASTRING_SAMPLE_RATE)
    logfile.close()

    if pyaudio_obj is not None:
        audio_stream.close()
        pyaudio_obj.terminate()

