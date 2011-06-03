#!/bin/sh
rm -f *.png *.html *.dot

pylint $@
for f in *.dot; do dot -Tpng $f > $f.png ; done;

