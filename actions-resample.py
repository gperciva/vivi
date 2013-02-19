#!/usr/bin/env python

import sys


actions_filename = sys.argv[1]
output_filename = sys.argv[2]

HOPSIZE_time = 256.0 / 22050.0
FACTOR = 4 # 1024 -> 256
#out_time = 0.0
#prev_params = None

actions = open(actions_filename).readlines()
out = open(output_filename, 'w')
for line in actions:
    if not line.startswith('b'):
        out.write(line)
    else:
        line_time = float(line.split()[1])
#        while line_time > (out_time+HOPSIZE_time):
#            new_line = "b\t%f\t%s\n" % (out_time, "\t".join(prev_params))
#            out_time += HOPSIZE_time
#            out.write(new_line)
        out.write(line)
        prev_params = line.split()[2:]
#        out_time = line_time + HOPSIZE_time
        for i in range(FACTOR-1):
            new_time = line_time + HOPSIZE_time * i
            new_line = "b\t%f\t%s\n" % (new_time, "\t".join(prev_params))
            out.write(new_line)



