#!/usr/bin/env python

import pstats

stats = pstats.Stats("profile.stats")

stats.strip_dirs().sort_stats('time').print_stats(6)




