#!/usr/bin/env python

import sys
# TODO: hack for current build system.
sys.path.append('python/')
sys.path.append('build/python/')
sys.path.append('build/swig/')

import vivi_controller

def main(actions_filename):
    params = vivi_controller.PhysicalActions()
    
    csv_filename = actions_filename.replace(".actions", ".csv")
    #print "writing %s..." % csv_filename
    csv = open(csv_filename, 'w')
    csv.write("st,finger,bow-bridge-distance,force,velocity\n")
    
    prev_time = 0.0
    lines = open(actions_filename).read().splitlines()
    for line in lines:
        if line[0] == '#':
            continue
        split = line.split()
        action_time = float( split[1] )
        if action_time > prev_time:
            csv.write("%i,%.5f,%.5f,%.5f,%.5f\n" % (
                params.string_number,
                params.finger_position,
                params.bow_bridge_distance,
                params.bow_force,
                params.bow_velocity
                ))
            prev_time = action_time
        if split[0] == 'f':
            params.string_number = int(split[2])
            params.finger_position = float(split[3])
        elif split[0] == 'p':
            continue
        elif split[0] == 'w':
            continue
        elif split[0] == 'b' or split[0] == 'a':
            params.string_number = int(split[2])
            params.bow_bridge_distance = float(split[3])
            params.bow_force = float(split[4])
            params.bow_velocity = abs(float(split[5]))
        else:
            print "Error! unrecognized: %s in file %s" %(
                split, actions_filename)
    if True:
        csv.write("%i,%.5f,%.5f,%.5f,%.5f\n" % (
                params.string_number,
                params.finger_position,
                params.bow_bridge_distance,
                params.bow_force,
                params.bow_velocity
                ))
    
    csv.close()
    #print "... done"


def main_inst_dir(actions_dir, inst):
    inst = int(inst)
    if inst == 0:
        insttext = "violin"
    elif inst == 1:
        insttext = "viola"
    elif inst == 2:
        insttext = "cello"
    import glob
    filenames = glob.glob("train-data/%s/*.actions" % insttext)
    for filename in filenames:
        main(filename)


if __name__ == "__main__":
    main(sys.argv[1])
    #main_inst_dir(sys.argv[1], sys.argv[2])


