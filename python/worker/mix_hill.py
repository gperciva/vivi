#!/usr/bin/env python

import copy

import render_audio
import vivi_defines

import notes_info
import note_actions_cats

import os

import scipy.stats

P_SIGNIFICANT = 0.01
#P_SIGNIFICANT = 0.10

def get_steps(job):
    return 1

def alteration_filename(alteration):
    if alteration < 0:
        return "_alter_%.3f" % alteration
    elif alteration == 0:
        return "_alter_1.0"
    else:
        return "_alter_+%.3f" % alteration


def calculate(job, process_step):

    info = notes_info.NotesInfo()
    info.load_file(job.alterations_filename)
    pncs = info.get_pncs()

    evals = []
    for alteration in job.alterations:
        # setup filenames
        alteration_base_audio_filename = (job.audio_filename +
           alteration_filename(alteration))
        alteration_base_audio_filename = alteration_base_audio_filename.replace(
            job.files.music_dir, job.files.hills_dir)
        dirname = os.path.dirname(alteration_base_audio_filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        this_alterations_filename = (alteration_base_audio_filename+".alterations")
        # reload old, write new .alterations file
        info.load_file(job.alterations_filename)
        pncs = info.get_pncs()
        for pnc in pncs:
            prev = info.info[pnc][-1]
            info.add(pnc, prev * alteration)
        info.write_file(this_alterations_filename)
        alteration_costs = []
        for i in range(job.count):
            # generate audio using new file
            this_job = copy.copy(job)
            this_job.audio_filename = alteration_base_audio_filename + "_hill_%04i" % i
            this_job.alterations_filename = this_alterations_filename
            # DONE IN HILL_CLIMBING NOW
#            render_audio.calculate(this_job, process_step)

            note_costs = get_notes_costs(this_job.audio_filename, pncs)
            alteration_costs.append(note_costs)

        #print alteration
        #for nc in alteration_costs:
        #    print nc
        evals.append( (alteration, alteration_costs) )

        process_step.emit()
    evals.sort()
    alter = calc_next_alts(evals, pncs)
    process_step.emit()

    info.load_file(job.alterations_filename)
    for i, pnc in enumerate(pncs):
        prev = info.info[pnc][-1]
        info.add(pnc, prev * alter[i])
    info.write_file(job.alterations_filename)
    process_step.emit()
    return job


def get_notes_costs(audio_basename, pncs):
    nac = note_actions_cats.NoteActionsCats()
    nac.load_file(audio_basename)
    note_costs = []
    for pnc in pncs:
        nac.load_note(pnc)
        cats = map(lambda x: x[1], nac.note_cats)
        filt = filter(lambda x: x != vivi_defines.CATEGORY_NULL, cats)
        filt = filter(lambda x: x != vivi_defines.CATEGORY_WAIT, filt)
        cost = sum(map(lambda x: x*x, filt))
        note_costs.append(cost)
    return note_costs


def calc_next_alts(evaluations, pncs):
    alts = []
    #print '======'
    for pnc_index, pnc in enumerate(pncs):
        evals = []
        for test_alt, info in evaluations:
            note_eval = map(lambda x: x[pnc_index], info)
            evals.append( (test_alt, note_eval) )

        #print '-----', pnc
        #for test_alt, e in evals:
        #    print 'alt: %.4f\tmean: %.4f\tmedian: %.4f\tstandard error: %.4f' % (test_alt, scipy.mean(e), scipy.median(e), scipy.std(e))
        #    print "p-values for below / above:"

        alt_index = 0
        # find index of 1
        for i, vals in enumerate(evals):
            if vals[0] == 1.0:
                midpoint = i

        best_index = midpoint # initialize to middle
        best_value = scipy.median(evals[midpoint][1])
        #print "midpoint:", evals[midpoint][0], best_value
        for test_alt, e in evals:
            if alt_index != midpoint:
                #print "try"
                #print e
                #print evals[midpoint][1]
                #print
                median = scipy.median(e)
                if median < best_value:
                    (h, p) = scipy.stats.kruskal(
                        scipy.array(e),
                        scipy.array(evals[best_index][1]))
                    if p < P_SIGNIFICANT:
                        #print "better value!"
                        print "note %i\t this %.5f\t best %.5f\t p %.5f\t alt %.3f" % (
                            pnc_index,
                            scipy.median(e), best_value, p, test_alt
                            )
                        best_index = alt_index
                        best_value = scipy.median(evals[alt_index][1])
                    else:
                        print "note %i\t p \t%.4f\t" % (
                            pnc_index, p)
            alt_index += 1
        alts.append( evals[best_index][0] ) 
    return alts

