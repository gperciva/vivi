#!/bin/bash
rm -f *.png *.html *.dot
GOOD_MODULES=" \
  ../python/judge_audio.py \
  ../python/table_play_widget.py \
  ../python/basic_training.py \
  ../python/collection.py \
  ../python/dirs.py \
  ../python/vivi_types.py \
  ../python/utils.py
"

pylint $GOOD_MODULES
for f in *.dot; do dot -Tpng $f > $f.png ; done;

