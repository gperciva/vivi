#!/usr/bin/env python

import subprocess
import os.path

import vivi_defines

def get_steps(job):
    return 2 + len(job.coll)

def calculate(job, process_step):
    process_step.emit()
    job.accuracy = cross_fold_accuracy(job.arff_filename)
    process_step.emit()
    make_cats_files(job.controller, job.st, job.mpl_filename,
        job.coll.coll, job.cats_dir, process_step)
    return job

def cross_fold_accuracy(arff_filename):
    if vivi_defines.REGRESSION:
        cmd = "kea -cl SVM -svm_svm NU_SVR -sC %.1f -sk RBF -w %s" % (
            vivi_defines.SVM_C, arff_filename)
    else:
        cmd = "kea -cl SVM -sk RBF -sC %.1f -w %s" % (
            vivi_defines.SVM_C, arff_filename)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    kea_output = process.communicate()
    # find relevent portion of stdout
    if vivi_defines.REGRESSION:
        for line in kea_output[0].split('\n'):
            if line.find("Correlation coefficient") >= 0:
                splitline = line.split()
                return float(splitline[2])
    else:
        for line in kea_output[0].split('\n'):
            if line.find("Correctly Classified Instances") >= 0:
                splitline = line.split()
                return float(splitline[4])

def make_cats_files(controller, st, mpl_filename, coll, cats_dir, process_step):
    ### calculate cats for each file
    ears = controller.getEars(st)
    ears.set_predict_wavfile(mpl_filename)
    for pair in coll:
        wav_filename = pair[0]
        cats_filename = os.path.join( cats_dir,
            os.path.basename(os.path.splitext(wav_filename)[0] + ".cats"))
        ears.predict_wavfile(wav_filename, cats_filename)
        process_step.emit()

