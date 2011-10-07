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
    #csv.write("finger,bow-bridge-distance,force,velocity\n")
    csv.write("st,finger,bow-bridge-distance,velocity\n")
    
    prev_time = 0.0
    for line in open(actions_filename).read().splitlines():
        if line[0] == '#':
            continue
        split = line.split()
        action_time = float( split[1] )
        if action_time > prev_time:
            csv.write("%i,%.3f,%.3f,%.3f\n" % (
                params.string_number,
                params.finger_position,
                params.bow_bridge_distance,
                #params.bow_force,
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
        elif split[0] == 'b':
            params.string_number = int(split[2])
            params.bow_bridge_distance = float(split[3])
            params.bow_force = float(split[4])
            params.bow_velocity = abs(float(split[5]))
        else:
            print "Error! unrecognized: %s in file %s" %(
                split, actions_filename)
    
    csv.close()
    #print "... done"


if __name__ == "__main__":
    main(sys.argv[1])

