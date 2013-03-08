#!/usr/bin/env python

import os
TMPDIR = "/tmp/vivi-cache/experiments"
if not os.path.exists(TMPDIR):
    os.makedirs(TMPDIR)

import sys
# TODO: hack for current build system.
sys.path.append('../python/')
sys.path.append('../build/python/')
sys.path.append('../build/swig/')
import glob

import numpy

import note_actions_cats
import vivi_defines
import vivi_controller
import utils
import dynamics

NOTE_LENGTH = 1.0

STEPS_X = 100
STEPS_Y = 50


#STEPS_X = 10
#STEPS_Y = 10
REPS = 1


PARAMS = {
    'cello-c-double-fb': {'inst_type': 2, 'st': 0,
        'fbmin': 2.0, 'fbmax': 20.0, 'fbi': 12.0,
        'prev_fmi': 0.0, 'prev_dyn': 0,
        },
    'cello-c-double-fb-prev-0': {'inst_type': 2, 'st': 0,
        'fbmin': 2.0, 'fbmax': 20.0, 'fbi': 12.0,
        'prev_fmi': 0.0, 'prev_dyn': 0,
        },
    'cello-c-double-fb-prev-1': {'inst_type': 2, 'st': 0,
        'fbmin': 1.0, 'fbmax': 15.0, 'fbi': 9.0,
        'prev_fmi': 1.0, 'prev_dyn': 0,
        },
    'cello-c-double-fb-prev-6': {'inst_type': 2, 'st': 0,
        'fbmin': 1.0, 'fbmax': 15.0, 'fbi': 8.0,
        'prev_fmi': 6.0, 'prev_dyn': 0,
        },
    'cello-c-double-fb-prev-0-mp': {'inst_type': 2, 'st': 0,
        'fbmin': 1.0, 'fbmax': 15.0, 'fbi': 5.0,
        'prev_fmi': 0.0, 'prev_dyn': 3,
        },
    'cello-c-double-fb-prev-1-mp': {'inst_type': 2, 'st': 0,
        'fbmin': 1.0, 'fbmax': 15.0, 'fbi': 5.0,
        'prev_fmi': 1.0, 'prev_dyn': 3,
        },
    'cello-c-double-fb-prev-6-mp': {'inst_type': 2, 'st': 0,
        'fbmin': 1.0, 'fbmax': 15.0, 'fbi': 4.0,
        'prev_fmi': 6.0, 'prev_dyn': 3,
        },

    'violin-e-double-fb': {'inst_type': 0, 'st': 3,
        'fbmin': 0.2, 'fbmax': 1.5, 'fbi': 0.0,
        'prev_fmi': 0.0, 'prev_dyn': 0,
        },
    }

def process(name):
    print "Starting %s..." % (name)
    this = PARAMS[name]
    
    inst_type = this['inst_type']
    st = this['st']
    fbmin = this['fbmin']
    fbmax = this['fbmax']
    fbi = this['fbi']
    prev_fmi = this['prev_fmi']
    prev_dyn = this['prev_dyn']
    
    dyn = 0
    finger_midi = 0
    fmi = 0
    
    controller = vivi_controller.ViviController(inst_type, 0)
    
    def get_training_filename(inst_type, st):
        filename = "../final/"
        if inst_type == 0:
            filename += "violin/"
        if inst_type == 1:
            filename += "viola/"
        if inst_type == 2:
            filename += "cello/"
        filename += "%i.mpl" % (st)
        return filename
    
    controller.load_ears_training(st, get_training_filename(inst_type, st))
    
    
    def single_file(filename, x):
        controller.reset()
        controller.filesNew(filename, st)
    
        finger_midi = 0
        controller.comment("attack inst %i st %i dyn %i finger_midi %.3f"
                % (inst_type, st, dyn, finger_midi))
    
        #prev_dyn = 3 # mp
        begin = vivi_controller.NoteBeginning()
        begin.physical.string_number = st
        begin.physical.bow_force = fbi
        begin.physical.dynamic = prev_dyn
        begin.physical.bow_bridge_distance = dynamics.get_distance(
            inst_type, prev_dyn)
        begin.physical.bow_velocity = dynamics.get_velocity(
            inst_type, prev_dyn)
        end = vivi_controller.NoteEnding()
    
        for i in range(REPS):
            controller.reset(True)
            finger_midi = prev_fmi
            begin.physical.finger_position = utils.midi2pos(finger_midi)
            controller.note(begin, NOTE_LENGTH, end)
            #controller.rest(0.1)
            begin.physical.dynamic = dyn
            begin.physical.bow_bridge_distance = dynamics.get_distance(
                inst_type, dyn)
            begin.physical.bow_velocity = dynamics.get_velocity(
                inst_type, dyn)
            finger_midi = 0.0
            begin.physical.finger_position = utils.midi2pos(finger_midi)
            begin.physical.bow_force = x
            begin.physical.bow_velocity *= -1
            controller.note(begin, NOTE_LENGTH, end)
        controller.filesClose()
    
        #kept_files.append(filename)
    
    def get_costs(cats):
        cats = [ c for c in cats if -5 < c < 5 ]
        total = 0.0
        for c in cats:
            total += abs(c)
        total /= float(len(cats))
        return total
    
    def main():
        x_range = numpy.linspace(fbmin, fbmax, STEPS_X)
        y_range = range(STEPS_Y)
    
        costs = numpy.zeros( (STEPS_Y, STEPS_X) )
        for ix, x in enumerate(x_range):
            for iy, y in enumerate(y_range):
                filename = os.path.join(TMPDIR,
                    "%i-%i-x%.3f-y%.3f" % (ix, iy, x, y))
                K_attack = 0.0
                K_main = 0.0
                K_velocity = 0.0
    
                controller.set_stable_K(st, dyn, 0, K_attack)
                controller.set_stable_K_main(st, dyn, 0, K_main)
                controller.set_stable_K(st, dyn, 1, K_attack)
                controller.set_stable_K_main(st, dyn, 1, K_main)
                controller.set_stable_K(st, dyn, 2, K_attack)
                controller.set_stable_K_main(st, dyn, 2, K_main)
                controller.set_K_velocity(K_velocity)
        
                single_file(filename, x)
                nac = note_actions_cats.NoteActionsCats()
                nac.load_file(filename, None)
                to_find = "finger_midi"
                nac.load_note(to_find, full=True)
                cats = [ b for a,b in nac.get_note_cats() ]
                cats = cats[len(cats)/2:] # only take second note
                cost = get_costs(cats)
                costs[iy][ix] = cost
    
            #print "Done %i / %i" % (ix+1, STEPS_X)
            # clean up
            remove_these = glob.glob(os.path.join(TMPDIR,"*"))
            for r in remove_these:
                os.remove(r)
        #print costs
    
        stable_file = open('%s.txt' % (name), 'w')
        for ix, x in enumerate(x_range):
            for iy, y in enumerate(y_range):
                stable_file.write("%g\t%g\t%g\n" % (
                    x, y, costs[iy][ix]))
            stable_file.write("\n")
        stable_file.close()
    
        means = numpy.mean(costs, axis=0)
        stable_file = open('%s-means.txt' % (name), 'w')
        for ix, x in enumerate(x_range):
            #for iy, y in enumerate(y_range):
                stable_file.write("%g\t%g\n" % (
                    x, means[ix]))
            #stable_file.write("\n")
        stable_file.close()

        lows = numpy.percentile(costs, 25, axis=0)
        highs = numpy.percentile(costs, 75, axis=0)
        stable_file = open('%s-lows.txt' % (name), 'w')
        for ix, x in enumerate(x_range):
                stable_file.write("%g\t%g\n" % (
                    x, lows[ix]))
        stable_file.close()
        stable_file = open('%s-highs.txt' % (name), 'w')
        for ix, x in enumerate(x_range):
                stable_file.write("%g\t%g\n" % (
                    x, highs[ix]))
        stable_file.close()

    main()
    

def main():
    process("cello-c-double-fb")
    #process("cello-c-double-fb-prev-1")
    #process("cello-c-double-fb-prev-6")
    #process("cello-c-double-fb-prev-0-mp")
    #process("cello-c-double-fb-prev-1-mp")
    #process("cello-c-double-fb-prev-6-mp")
    process("violin-e-double-fb")


main()


