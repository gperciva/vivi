#!/usr/bin/env python
""" deals with .mf collections of string-dynamic .wav files """

import operator

import vivi_defines

class Collection:
    """ a .mf collection of string-dynamic .wav files with judgements """
    def __init__(self):
        self.coll = []
        self.modified = False

    def __len__(self):
        return self.num_main()

    def _sort(self):
        """ sorts by category """
        self.coll = sorted(self.coll, key=operator.itemgetter(1, 0))

    def add_mf_file(self, filename):
        """ adds data from a .mf file to the collection """
        try:
            lines = open(filename).readlines()
        except IOError:
            return
        for line in lines:
            splitline = line.split()
            self.add_item(splitline[0],
                int(splitline[1]) - vivi_defines.CATEGORY_POSITIVE_OFFSET,
                False, False)
        self._sort()
        # ASSUME: only reading from a single file
        self.modified = False

    def write_mf_file(self, filename):
        """ writes a mf file with all items with the appropriate inout categories """
        self._sort()
        outfile = open(filename, 'w')
        for pair in self.coll:
            wavfile = pair[0]
            judgement = pair[1] + vivi_defines.CATEGORY_POSITIVE_OFFSET
            if self.is_cat_valid(judgement):
                outfile.write(wavfile+'\t'+str("%03i" % judgement)+'\n')
            else:
                outfile.write('#'+wavfile+'\t'+str("%03i" % judgement)+'\n')
        outfile.close()
        self.modified = False

    @staticmethod
    def is_cat_valid(judgement):
        """ is the judgement non-unknown? """
        if judgement is None:
            return False
        elif judgement is vivi_defines.CATEGORY_NULL:
            return False
        else:
            return True

    def get_items_cat(self, cat):
        """ returns all pairs matching the category """
        return filter(lambda x: x[1] == cat, self.coll)

    def get_items_cat_finger(self, cat, finger):
        """ returns all pairs matching the category """
        return filter(
            lambda x: int(float(x[0].split('_')[2])) == finger,
                self.get_items_cat(cat))

    def get_items_cat_bp(self, cat, bp):
        """ returns all pairs matching the category """
        return filter(
            lambda x: float(x[0].split('_')[3]) - bp < 1e-2,
                self.get_items_cat(cat))

    def get_items_cat_finger_bp(self, cat, finger, bp):
        """ returns all pairs matching the category """
        return filter(
            lambda x: float(x[0].split('_')[3]) - bp < 1e-2,
                self.get_items_cat_finger(cat, finger))

    def add_item(self, filename, judgement, replace=False, warning=True):
        """ adds a (filename, judgement) pair """
        new_pair = (filename, judgement)
        if filename[0] == '#':
            filename = filename[1:]
        for i, pair in enumerate(self.coll):
            if pair[0] == filename:
                if (not replace) and warning:
                    print "Warning: Collection: replacing a previous item"
                self.coll[i] = new_pair
                self.modified = True
                return
        if replace and warning:
            print "Warning: Collection: original item not found"
        self.coll.append(new_pair)
        self.modified = True

    def replace(self, filename, judgement):
        """ replaces a (filename, judgement) pair with a new judgement """
        self.add_item(filename, judgement, replace=True)

    def delete(self, filename):
        """ removes a (filename, judgement) pair """
        for i, pair in enumerate(self.coll):
            if pair[0] == filename:
                self.coll.pop(i)
                self.modified = True
                return
        print "Warning: Collection: failed to delete %s" % filename

    def num_main(self):
        """ number of files which have 'main' categories """
        number = 0
        for pair in self.coll:
            if pair[1] is not vivi_defines.CATEGORY_NULL:
                number += 1
        return number

    def need_save(self):
        return self.modified

    def set_modified(self):
        self.modified = True

def self_test(filename):
    """ basic test of collection, not very good """
    coll = Collection()
    coll.add_mf_file(filename)
    coll.write_mf_file(filename, CATS_ALL)

if __name__ == "__main__":
    import sys
    self_test(sys.argv[1])


