#!/usr/bin/env python
if __name__ == "__main__":
    import sys
    sys.path.append('../')
    sys.path.append('../../build/swig/')
    sys.path.append('python/')
    sys.path.append('build/swig/')
    PLOT = True
else:
    PLOT = False

import numpy
import math
import scipy.stats
import scipy.signal

import task_base
import vivi_defines

import note_actions_cats
import dynamics
import vivi_controller

import utils
import vivi_types
import basic_training

import collection
import pylab

STABLE_LENGTH = 1.0
TOO_SMALL_TO_CARE_CAT = 0.25

STEPS_X = 3  # forces per finger
STEPS_Y = 7
REPS = 3


class TaskStable(task_base.TaskBase):

    def __init__(self, controller, emit):
        task_base.TaskBase.__init__(self, controller, emit,
            "stable")
        #self.STEPS_X = STEPS_X * len(basic_training.FINGER_MIDIS)
        self.STEPS_X = STEPS_X
        self.STEPS_Y = STEPS_Y
        self.REPS = REPS
        self.second_pass = False

        self.LOW_INIT = 1.0 # blah numbers to start with
        self.HIGH_INIT = 1.5

        self.stable_forces = None

        # TODO: eliminate this
        self.most_stable = 1.0
        self.notes = None

    def set_data(self, inst_type, st, dyn, force_init, files):
        task_base.TaskBase.set_data(self, inst_type, st, dyn, files)
        self.forces_initial = force_init

    @staticmethod
    def steps_full():
        #print "STEPS:", STEPS_X*STEPS_Y*REPS + 1
        return STEPS_X*STEPS_Y*REPS + 1
        #return 1 * (STEPS * REPS)

    def _make_files(self):
        self._setup_controller()

        #Ks = numpy.linspace(1.0, 2.5, STEPS_X)
        # skip K=1.0
        #Ks = numpy.exp(numpy.linspace(
        #    numpy.log(self.LOW_INIT),
        #    numpy.log(self.HIGH_INIT),
        #    STEPS_X+1))[1:]
        Ks = numpy.exp(numpy.linspace(
            numpy.log(self.LOW_INIT),
            numpy.log(self.HIGH_INIT),
            STEPS_Y))

        #f = self.force_init
        #forces = [ 0.25*f, 0.5*f, f, 2*f, 4*f ]
        #forces = [ 0.5*f, f, 2*f ]
        #forces = self._make_forces(self.force_init, num=9)
        #forces = [forces[3], forces[4], forces[5]]
        #forces = numpy.linspace(forces[4], forces[5], num=3)
        #self.forces_initial = forces
        #print forces
        self.forces_init_used = []

        #emits = 0
        for fmi, finger_midi in enumerate(basic_training.FINGER_MIDIS):
            #forces = self._make_forces(self.forces_initial[fmi], 9)
            #forces = numpy.linspace(forces[4], forces[6], num=3,
            #    endpoint=True)
            #forces = [1.2, 1.35, 1.5]
            forces = numpy.linspace(
                self.forces_initial[fmi][1],
                self.forces_initial[fmi][1] + self.forces_initial[fmi][0],
                num=3, endpoint=True)
            #print forces
            self.forces_init_used.extend(forces)
            for K in Ks:
                for bow_force in forces:
                    for count in range(self.REPS):
                        audio_params = vivi_types.AudioParams(
                                    self.st, finger_midi,
                                    dynamics.get_distance(self.inst_type,
                                        self.dyn),
                                    bow_force,
                                    dynamics.get_velocity(self.inst_type,
                                        self.dyn))
                        stable_filename = self.files.make_stable_filename(
                                audio_params,
                                K, count+1)
                        self.controller.set_stable_K(self.st, self.dyn, K)
                        self.controller.filesNew(stable_filename)
                        self.controller.comment(
                                "stable inst %i st %i dyn %i finger_midi %.3f"
                                % (self.inst_type, self.st, self.dyn, finger_midi))
                        begin = vivi_controller.NoteBeginning()
                        vivi_types.audio_params_to_physical(
                                audio_params, self.dyn, begin.physical)
                        end = vivi_controller.NoteEnding()
                        #end.keep_bow_velocity = True
                        for bow_direction in [1, -1]:
                           begin.physical.bow_velocity *= bow_direction
                           self.controller.note(begin, STABLE_LENGTH, end)
                        self.controller.filesClose()
                    #emits += 1
                    #print "emit: %i / %i" % (emits, self.steps_full())
                    self.process_step.emit()

    def get_stable_files_info(self):
        files = self._get_files()

        self._setup_lists_from_files(files)

        # ASSUME: no screw-ups in the file creation
        self.num_rows = len(self.counts[0]) * len(self.extras[0])
        #self.num_cols = len(self.forces_initial[0])*len(self.finger_midis)
        self.num_cols = len(self.forces_initial[0])
        self.num_counts = len(self.counts[0])
        #self.num_rows = STEPS_X
        #self.num_cols = STEPS_Y

        # initialize 3d array
        self.notes = []
        for fmi in range(len(self.finger_midis)):
            self.notes.append([])
            for i in range(self.num_rows):
                self.notes[fmi].append([])
                for j in range(self.num_cols):
                    self.notes[fmi][i].append(None)
        
        for filename in files:
            params, extra, count = self.files.get_audio_params_extra(filename)
            finger_midi = params.finger_midi
            force = params.bow_force
            fmi = self.finger_midis.index(finger_midi)
            K_i = self.extras[finger_midi].index(extra)
            force_i = self.forces_initial[finger_midi].index(force)

            # and setup self.examines
            row = (
                    self.num_counts*self.extras[finger_midi].index(extra)
                    + self.counts[finger_midi].index(count)
                    )
            col = (
                    #len(self.finger_midis) * 
                    self.forces_initial[finger_midi].index(force)
                    #+ self.finger_midis.index(finger_midi)
                    )
            nac = note_actions_cats.NoteActionsCats()
            nac.load_file(filename[0:-4], self.files)
            #to_find = "finger_midi %i" % fm
            to_find = "finger_midi"
            nac.load_note(to_find, full=True)
            #print nac.note_cats_means
            #print nac.note_forces


            #stability = self.get_stability(nac.note_cats_means,
            #    nac.note_forces)
            cats = [ b for a,b in nac.get_note_cats() ]
            stability = self.get_cost(cats)

            #self.notes[fmi][K_i][force_i] = (nac, stability)
            #print fmi, row, col
            self.notes[fmi][row][col] = (nac, stability)

    def _examine_files(self):
        self.get_stable_files_info()

        num_Ks = len(self.extras[0])
        num_cols = 9
        num_counts = REPS
        #print "num Ks:", num_Ks
        # find "most stable" rows
        stability = numpy.zeros( (num_Ks, num_cols) )
        stds = numpy.zeros( (num_Ks, num_cols) )
        #print '---'
        #print num_Ks, num_cols, num_counts
        for K_i in range(num_Ks):
            for col in range(num_cols):
                stabs = []
                for count in range(num_counts):
                    row = K_i*num_counts + count
                    fmi = col / 3
                    note_stability = self.notes[fmi][row][col%3][1]
                    #print fmi, row, col, K_i, note_stability
                    #stability[K_i][col] += (note_stability / self.num_cols)
                    stabs.append(note_stability)
                stability[K_i][col] = numpy.mean(stabs)
                #stability[K_i][col] = max(stabs)
                stds[K_i][col] = numpy.std(stabs)
        mstab = stability.mean(axis=1)
        mstds = stds.mean(axis=1)
        #print stability.mean(axis=1)
        #print stds.mean(axis=1)
        check = mstab + mstds

        stable_file = open('stable.txt', 'w')
        for K_i in range(num_Ks):
            for col in range(self.num_cols):
                stable_file.write("%g %g %g\n" % (
                        self.extras[0][K_i],
                        self.forces_initial[0][col],
                        stability[K_i][col]))
            stable_file.write("\n")
        stable_file.close()
        #stable_index = numpy.unravel_index(
        #        numpy.argmin(stability), stability.shape)[0]
        #K = self.extras[0][stable_index]
        #print "stable index %i, K = %.2f " %(stable_index, K)
        #stable_means = numpy.mean(, axis=1)
        #print stable_means
        #for i,s in enumerate(check):
        #    print self.extras[0][i], s
        #print check
        stable_index = numpy.argmin(check)
        #print self.extras[0], stable_index
        K = self.extras[0][stable_index]
        #print "stable index %i, K = %.2f " %(stable_index, K)
        self.process_step.emit()
        return stable_index, K

        #for fmi in range(len(self.finger_midis)):
        #    attack = attacks[fmi]
        #    att_index = numpy.unravel_index(
        #        numpy.argmin(attack), attack.shape)
        #    print att_index
        #    att_index = att_index[1]
        #    att_force = self.forces_initial[0][att_index]
        #    print "attack index %i, force %.3f N" %(att_index, att_force)


        #for row in range(self.num_rows):
        #    vals = []
        #    for col in range(self.num_cols):
        #        for fmi in range(len(self.finger_midis)):
        #            cv = self.notes[fmi][row][col][1]
#
#                    vals.append(cv)
            #print "%.2f\t%.3f" % (self.extras[block], scipy.stats.gmean(block_vals)),
            #print
            #print "\t%.3f" % (scipy.std(block_vals))
            #candidates.append( 
            #    (scipy.stats.gmean(block_vals), self.extras[0][block], block) )
        #candidates.sort()
        #print candidates
        #most_stable = candidates[0][1]
        #index = candidates[0][2]
        index = 9
        most_stable = 1.0
        return index, most_stable


    @staticmethod
    def get_cost(values):
        if len(values) == 0:
            return 0
        examine = filter(lambda x: x != vivi_defines.CATEGORY_NULL, values)
        examine = filter(lambda x: x != vivi_defines.CATEGORY_WAIT, examine)
        dexamine = numpy.array(examine[1:]) - numpy.array(examine[:-1])
        examine = numpy.array([
                c if abs(c) > TOO_SMALL_TO_CARE_CAT else 0
                for c in examine])
        #print examine
        #for i in range(vivi_defines.ATTACK_HARSH_HOPS):
        #    #if 0 < examine[i] < 1.5:
        #    #    examine[i] = 0
        #    examine[i] -= 1
        total_abs = 0
        for i, c in enumerate(examine):
            if c > 0:  
                total_abs += i
                #total += i**2
            elif c < 0:
                total_abs += i
                #total += i**2
        total_abs /= float(len(examine)*(len(examine)+1)/2.0)
        total_deriv = sum(abs(dexamine)) / float(len(dexamine))
        total = (total_abs + total_deriv) / 2.0
        #print examine
        #total = sum(map(lambda x: x*x, examine))
        return total

    @staticmethod
    def get_stability(cats, forces, plot=False, name="", good_flag=False):
        #print forces
        notes = [[], []]
        #notes_forces = [[],[]]
        if True:
            notes_i = -1
            prev = None
            for i, cat in enumerate(cats):
                if cat == vivi_defines.CATEGORY_NULL:
                    prev = None
                    continue
                if cat == vivi_defines.CATEGORY_WAIT:
                    prev = None
                    continue
                if prev is None:
                    notes_i += 1
                prev = cat
                notes[notes_i].append(cat)
                #notes_forces[notes_i].append(forces[i][1])

        #tot = 0.0
        #for ni, note_cats in enumerate(notes):
        #    #notes[ni] = numpy.array(note_cats)
        #    for j, cat in enumerate(note_cats):
        #        err = cat**2
        #        weight = j
        #        tot += err*weight
        #return tot


        tot = 0.0
        global good, bad
        for ni, note_cats in enumerate(notes):
            #print ni, note_cats
            #threshold = numpy.array([
            #    c if abs(c) > TOO_SMALL_TO_CARE_CAT else 0
            #    for c in note_cats])
            #note_cats = threshold

            #b, a = scipy.signal.iirdesign(
            #    wp=[0.10],
            #    ws=[0.05],
            #    gpass=3, gstop=12,
            #    ftype='butter')
            b, a = scipy.signal.butter(N=2, Wn=0.2, btype='high')
            filt_note_cats = scipy.signal.filtfilt(b, a, note_cats)

            if plot:
                data = note_cats
                if good_flag:
                    #good.plot(data_orig)
                    good.plot(data, color="blue", label="orig")
                    good.plot(filt_note_cats, color="red", label="filt")
                else:
                    #bad.plot(data_orig)
                    bad.plot(data, color="blue", label="orig")
                    bad.plot(filt_note_cats, color="red", label="filt")

            tot += sum(filt_note_cats**2)
            continue
 
        #for ni, note_cats in enumerate(notes):
            #pylab.plot(threshold)
            #pylab.show()

            areas = []
            direction = math.copysign(1, note_cats[0])
            area = None
            for cat in note_cats:
                if cat == 0:
                    if area is None:
                        pass
                    else:
                        areas.append(numpy.array(area))
                        area = None
                elif cat * direction > 0:
                    if area is None:
                        area = []
                    area.append(cat)
                    #print cat
                    #print cat, direction, cat * direction
                else:
                    #print '------'
                    if area is None:
                        pass
                    else:
                        areas.append(numpy.array(area))
                    area = []
                    area.append(cat)
                    #print cat, direction, cat * direction
                    #print cat
                    direction = math.copysign(1, cat)
                    #pylab.plot(area)
            if area is not None:
                areas.append(numpy.array(area))
            #print '---'
            #for a in areas:
            #    print a
            #print '---'

            #total = sum(abs(note_cats))

            #print '-----'
            sum_areas = []
            for area in areas:
                a = sum(area)
                #a = len(area)
                sum_areas.append(a)
            sum_areas = sum_areas + [0]
            sum_areas = numpy.array(sum_areas)
            #tot *= (1+sum_areas)

            #print sum_areas
            d_areas = abs(sum_areas[1:] - sum_areas[:-1])
            #print d_areas

            prods = 0.0
            prev = 1.0
            #print '----'
            for a in d_areas:
            #    print a
                prods += prev*abs(a)
                prev = abs(a)
            #print "prods:", prods
            tot += prods
            #print d_areas
            #if False:
            #    pylab.figure()
            #    pylab.plot(sum_areas)
            #    pylab.plot(d_areas)
            #    pylab.title("d_areas")
            #x = sum(d_areas)
            #x = sum(abs(sum_areas))


            #rms = math.sqrt(sum(note_cats*note_cats) / len(note_cats))
            #flatness = (scipy.stats.gmean(sum_areas) /
            #    scipy.mean(sum_areas) )
            #print rms, flatness
            #prods += x

        #if plot:
        #    pylab.show()

        #zzz
        return tot
        ######################################

        RMS = False
        if RMS:
            # split into notes
            notes = [[], []]
            notes_forces = [[],[]]
            notes_i = -1
            prev = None
            for i, cat in enumerate(cats):
                if cat == vivi_defines.CATEGORY_NULL:
                    prev = None
                    continue
                if cat == vivi_defines.CATEGORY_WAIT:
                    prev = None
                    continue
                if prev is None:
                    notes_i += 1
                prev = cat
                notes[notes_i].append(cat)
                notes_forces[notes_i].append(forces[i][1])

            for ni, note_cats in enumerate(notes):
                notes_forces[ni] = numpy.array(notes_forces[ni])
            
            rmss = []
            for ni, note_cats in enumerate(notes):
                rms = 0.0
                #weights = (numpy.log(
                #    numpy.linspace(0, 1, len(note_cats))+1)
                #    / len(note_cats)
                #    )
                #print weights
                #pylab.plot(weights)
                #pylab.show()
                #exit(1)
                weights = numpy.linspace(0, 1, len(note_cats))
                for i, cat in enumerate(note_cats):
                    rms += cat*cat*weights[i]
                rms /= sum(weights)
                rms = math.sqrt(rms)
                rmss.append(rms)
            #print "\trms: %.3f" % rms
            rms = sum(rmss)

            filt = 0
            #N, Wn = scipy.signal.buttord(
            #    wp=[0.08, 0.5],
            #    ws=[0.04, 0.6],
            #    gpass=3, gstop=12)
            #print "order:", N,  "\tWn:", Wn
            #b, a = scipy.signal.butter(N, Wn, btype='bandpass')
            b, a = scipy.signal.iirdesign(
                wp=[0.4],
                ws=[0.5],
                gpass=3, gstop=12,
                ftype='butter')
            w, h = scipy.signal.freqz(b, a)
            print "order:", len(b)+1
            
            #pylab.plot(w/max(w), abs(h))
            #pylab.show()
            #exit(1)
            #b, a = scipy.signal.butter(N, Wn, btype='low')
            flats = 0.0
            for ni, note_cats in enumerate(notes):
                #signal = notes_forces[ni] / max(notes_forces[ni])
                signal = notes_forces[ni]
                forces_filt = scipy.signal.filtfilt(b, a,
                    signal)
                resi = math.sqrt(
                    sum(forces_filt**2)/len(forces_filt))
                #print "\tnote %i high freqs:\t%.3f" % (ni, resi)
                filt += resi
                if plot:
                    #global good, bad
                    #pylab.plot([87*ni+4+x for x in range(len(cats_filt))],
                    #    cats_filt)
                    #pylab.figure()
                    #pylab.plot(abs(scipy.fftpack.fft(note_cats)[:len(note_cats)/2]))
                    #signal = numpy.array(notes_forces[ni])
                    #signal -= numpy.mean(signal)
                    #signal_rms = math.sqrt(sum(signal**2)/len(signal))
                    #signal -= signal_rms
                    #signal = forces_filt
                    fft = abs(scipy.fftpack.fft(signal)[:len(signal)/2])
                    fft_power = fft**2
                    data = 20*numpy.log10(fft)
                    #data /= max(data)
                    data_orig = data
                    data_orig = signal

                    signal = numpy.array(forces_filt)
                    #signal_rms = math.sqrt(sum(signal**2)/len(signal))
                    #signal -= signal_rms
                    #signal = forces_filt
                    data = abs(scipy.fftpack.fft(signal)[:len(signal)/2])
                    data = 20*numpy.log10(data)
                    #data /= max(data)
                    data = forces_filt

                    #flatness = (scipy.stats.gmean(fft_power) / fft_power.mean() )
                    flatness = (scipy.stats.gmean(data_orig) /
                        data_orig.mean() )
                    flats += flatness
                    #data = signal * (1.0 / (numpy.linspace(
                    #    1, 2, len(signal))))
                    continue
                    if good_flag:
                        #good.plot(data_orig)
                        good.plot(data)
                    else:
                        #bad.plot(data_orig)
                        bad.plot(data)
                    #good.title(name + " FFT %i" % ni)
                    #pylab.ylim([-1, 1])
                    #good.ylim([0, 20])

                    #pylab.title(name + " time")
                    #pylab.plot(note_cats)
                    #pylab.plot(note_cats_filt)
                # FIXME: debug only
                #return rms+filt

            #return rms+filt
            return flats
            #return filt

        bad = 0
        total_non_null = 0
        for cat in cats:
            if cat == vivi_defines.CATEGORY_NULL:
                continue
            if cat == vivi_defines.CATEGORY_WAIT:
                continue
            if abs(cat) > 0.5:
                bad += 1
            total_non_null += 1
        return float(bad) / total_non_null


        direction = 1
        areas = []
        area = []

        modcats = []
        oldval = 0.0
        alpha = 0.3
        xs = []
        origcats = []
        zero = []
        for i, cat in enumerate(cats):
            if cat < -10:
                continue
            origcats.append(cat)
            newval = alpha*cat + (1.0-alpha)*oldval
            modcats.append(newval)
            oldval = newval
            xs.append(i)
            zero.append(0)

        if PLOT:
            pylab.figure()
            pylab.plot(xs, origcats)
            pylab.plot(xs, modcats)
            pylab.plot(xs, zero)
            pylab.ylim([-2, 2])
    
        for cat in modcats:
            if cat == vivi_defines.CATEGORY_NULL:
                continue
            if cat == vivi_defines.CATEGORY_WAIT:
                continue
            #err = cat*cat
            if abs(cat) < TOO_SMALL_TO_CARE_CAT:
                continue
            if cat * direction > 0:
                area.append(abs(cat))
                #area.append(err)
            else:
                if area:
                    areas.append(area)
                area = []
                area.append(abs(cat))
                #area.append(err)
                direction = math.copysign(1, cat)
        if area:
            areas.append(area)
        stable = 1.0
        scale_factor = 1.0
        #scale_factor *= math.sqrt(sum([cat*cat for cat in cats])) / float(len(cats))
        scale_factor *= sum([abs(cat) for cat in cats]) / float(len(cats))
        #scale_factor *= 1.0 / float(len(cats))
        scale_factor *= 1.0e-4
        for a in areas:
            #area_fitness = sum(a) * sum(a) / float(len(a))
            #area_fitness = sum(a) / math.sqrt(len(a))
            #area_fitness = 1.0 / math.sqrt(len(a))
            #area_fitness = len(a) * sum(a) / all_bad
            area_fitness = len(a)
            #area_fitness = sum(a) * len(a)
            stable *= area_fitness
            #print area_fitness, stable
        stable *= scale_factor
        return stable

fig = pylab.figure()
pylab.title("good")
pylab.xlabel("time (hops)")
pylab.ylabel("sound quality judgements")
#pylab.ylim([0, 7])
#pylab.ylim([0, 1])
#pylab.ylim([0, 25])
pylab.ylim([-2, 2])
good = fig.add_subplot(111)

fig = pylab.figure()
pylab.title("bad")
pylab.xlabel("time (hops)")
pylab.ylabel("sound quality judgements")
#pylab.ylim([0, 7])
pylab.ylim([-2, 2])
#pylab.ylim([0, 25])
bad = fig.add_subplot(111)


if __name__ == "__main__":
    import os.path
    def try_file(descr, filename, good_flag=False):
        #pylab.figure()
        nac = note_actions_cats.NoteActionsCats()
        nac.load_file(filename[0:-5], None)
        nac.load_note("finger_midi", full=True)

        cats = nac.note_cats_means
        #print cats
        #cats = [c for t,c in nac.note_cats]
        # remove weird final (0,0)
        if nac.note_cats[-1][0] == 0:
            cats = cats[:-1]
        title = filename[-12:-7]
        stability = TaskStable.get_stability(cats,
            nac.note_forces,
            plot=True,
            name=descr, good_flag=good_flag)

        #plot_cats = [c for c in cats if c > -10]
        #cats = numpy.array(plot_cats)
        #pylab.title(descr + " " + title)
        #pylab.legend()
        print "%s final:\t%s\t%.2f" % (descr, title, stability)

    goods = [
        "stable_0_0.000_0.092_2.878_0.400_1.260_2.cats",
        #"",
        #"stable_0_0.000_0.100_0.244_0.400_1.355_1.cats",
        #".cats",
    ]
    bads = [
        "stable_0_0.000_0.092_1.551_0.400_2.000_2.cats",
    ]
    for g in goods:
        try_file("good", os.path.join(
        "/tmp/vivi-cache/works/violin",
        g
        ), good_flag=True)
    for b in bads:
        try_file("bad", os.path.join(
        "/tmp/vivi-cache/works/violin",
        b
        ))
    pylab.show()



