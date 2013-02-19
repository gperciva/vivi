#!/bin/sh
for f in train/*.actions
do
	python/actions2csv.py $f
done

#for i in 0 1 2 3
#do
#	cat train/${i}_?.mf > train/${i}.mf
#done


