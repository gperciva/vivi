#!/bin/sh
for i in 0 1 2 3
do
	./vivi.py -l ly/example-input.ly -p -i ${i}
	mv \
		/tmp/vivi-cache/music/ly/example-input-unnamed-staff.wav \
		example-input-${i}.wav
done

