#!/usr/bin/env python


class NotesInfo():
    def __init__(self):
        self.info = {}

    def load_file(self, filename):
        read_info = open(filename).readlines()
        for line in read_info:
            pnc = line.split('\t')[0]
            data = map(float, line.split('\t')[1:])
            self.info[pnc] = data

    def get_pncs(self):
        pncs = self.info.keys()
        def sort_pncs(name):
            split = name.split()
            return (int(split[2]), int(split[1]))
        pncs.sort(key=sort_pncs)
        return pncs

    def add(self, key, value):
        try:
            self.info[key].append(value)
        except:
            self.info[key] = [value]

    def write_file(self, filename):
        out = open(filename, 'w')
        for key in sorted(self.info.keys(),
                key=lambda x: (int(x.split()[2]),
                           int(x.split()[1]) ) ):
            out.write("%s" % key)
            for x in self.info[key]:
                if x == int(x):
                    out.write("\t% .0f" % x)
                else:
                    out.write("\t% .3f" % x)
            out.write("\n")
        out.close()


