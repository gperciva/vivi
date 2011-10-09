#!/usr/bin/env python

import os
import sys
import glob

DIR = "/tmp/vivi-cache/movie/"

filenames = glob.glob(DIR+"1/*.tga")
filenames.sort()
for filename in filenames:
    other = filename.replace("/1/", "/2/")
    cmd = "convert %s %s +append %s" % (
        filename, other,
        DIR+os.path.basename(filename))
    os.system(cmd)

