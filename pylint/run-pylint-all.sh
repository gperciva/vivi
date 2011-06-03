#!/bin/sh
rm -f *.png *.html *.dot

pylint ../python/*.py
for f in *.dot; do dot -Tpng $f > $f.png ; done;

