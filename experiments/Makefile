

all: generate copy

copy:
	cp *-means.txt ~/src/papers/acmmm2013/data/
	cp *-lows.txt ~/src/papers/acmmm2013/data/
	cp *-highs.txt ~/src/papers/acmmm2013/data/

generate:
	./x-force.py
	./x-double-force.py
	./x-guess-feedback.py
	./x-double-guess-feedback.py

clean:
	rm -f *.txt


