#!/bin/bash
rm -f *.png *.html *.dot
GOOD_MODULES=" \
  ../python/dirs.py \
  ../python/utils.py
"
  #../python/judge_audio.py \
  #../python/shared.py "

pylint $GOOD_MODULES
for f in *.dot; do dot -Tpng $f > $f.png ; done;

