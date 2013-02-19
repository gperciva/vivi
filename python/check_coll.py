#!/usr/bin/env python

import collection

import utils
import shared
import vivi_defines

class CheckColl:
    def __init__(self, files):
        self.data = []
        self.files = files

    def check(self, coll, st):
        self.data = []

        training_file = self.files.get_mpl_filename(st)

        for coll_index,pair in enumerate(coll.coll):
            cat = pair[1]
            if coll.is_cat_valid(cat):
                self.judge_wav_file(pair[0], cat)

    def judge_wav_file(self, wavfile, user_cat):
        cats = []
        cat_out = self.files.get_cats_name(wavfile[0:-4])
        try:
            cat_lines = open(cat_out+'.cats').readlines()
            for line in cat_lines:
                if line[0] == '#':
                    continue
                splitline = line.split()
                cat = float( splitline[2].rstrip() )
                if cat != vivi_defines.CATEGORY_NULL:
                    cats.append(cat)
        except:
            cats = []
        self.data.append( (wavfile, user_cat, cats) )

    def get_filename(self, index):
        return self.data[index][0]



