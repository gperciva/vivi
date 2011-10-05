#!/bin/sh
sh make-all-strings.sh

for i in 0 1 2 3
do
	build/src/test-gextract train/${i}.mf
	kea -w train/${i}.arff > ${i}-results.txt
done

cat train/?.mf > train/combo.mf
build/src/test-gextract train/combo.mf
kea -w train/combo.arff > combo-results.txt


