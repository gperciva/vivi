#!/usr/bin/env python

USE_RMS = True


def get_cost(cats):
    filt = [ c for c in cats if -5 < c < 5 ]
    total = 0.0
    if USE_RMS:
        for c in filt:
            total += c**2
        import math
        total = math.sqrt(total / float(len(cats)) )
    else:
        for c in filt:
            total += abs(c)
        total /= float(len(cats))
    return total


def get_cats(filename):
    lines = open(filename).readlines()
    cats = []
    for line in lines:
        if line[0] == '#':
            continue
        cat = float( line.split('\t')[2] )
        cats.append(cat)
    return cats


def get_cat_cost(filename):
    cats = get_cats(filename)
    cost = get_cost(cats)
    return cost

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    cost = get_cat_cost(filename)
    print "%s\t%f" % (filename, cost)

