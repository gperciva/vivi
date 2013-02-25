#!/usr/bin/env python
""" Manipulating files in Vivi's directories. """
import os
import shutil
import glob

import vivi_types
import actions2csv

class ViviDirs:
    """ Convenience class for directories and files. """
    def __init__(self, training_dirname, cache_dirname,
            final_dirname, instrument_name=""):
        """ constructor """
        self.ly_original = None
        self.ly_basename = None
        self.instrument_name = instrument_name
        self.train_dir = os.path.join(
            os.path.normpath(training_dirname), instrument_name)
        self.final_dir = os.path.join(
            os.path.normpath(final_dirname), instrument_name)
        self.inter_dir = os.path.join(cache_dirname, "inter",
            instrument_name)
        self.works_dir = os.path.join(cache_dirname, "works",
            instrument_name)
        self.music_dir = os.path.join(cache_dirname, "music")
        self.hills_dir = os.path.join(cache_dirname, "hills")
        self.movie_dir = os.path.join(cache_dirname, "movie")
        def _ensure_dir_exists(dirname):
            """ create the dirname if it does not exist """
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
        map(_ensure_dir_exists, [self.train_dir, self.final_dir,
             self.inter_dir, self.works_dir, self.music_dir,
             self.hills_dir])

    @staticmethod
    def _get_basename(st, dyn):
        """ used internally to construct 0_0. or wierd_0_0. """
        #basename = '%i_%i.' % (st, dyn)
        basename = '%i.' % (st)
        return basename

    def get_string_filename(self, st):
        """ marsyas collection .vivi file. """
        filename = os.path.join(self.final_dir,
            '%i.vivi' % (st))
        return filename

    def get_mf_filename(self, st):
        """ marsyas collection .mf file. """
        filename = os.path.join(self.train_dir,
            '%i.mf' % (st))
        return filename

    def get_arff_filename(self, st):
        """ weka training .arff file. """
        filename = os.path.join(self.inter_dir,
            '%i.arff' % (st))
        return filename

    def get_mpl_filename(self, st):
        """ saved MarSystems (for training) .mpl file. """
        filename = os.path.join(self.final_dir,
            '%i.mpl' % (st))
        return filename

    def get_dyn_vivi_filename(self, st, dyn, inst_num):
        """ trained dynamic .vivi file. """
        filename = os.path.join(self.final_dir,
            #self._get_basename(st, dyn)
            "%i_%i_%i." % (inst_num, st, dyn)
            + 'vivi')
        return filename

    @staticmethod
    def basename_params(base, params):
        """ used internally to construct various filenames """
        basename = "%s_%i_%.3f_%.3f_%.3f_%.3f" % (
            base,
            params.string_number,
            float(params.finger_midi),
            params.bow_bridge_distance,
            params.bow_force,
            params.bow_velocity)
        # the .wav is added in ViviController
        #basename += ".wav"
        return basename

    def make_verify_filename(self, taskname, params, count):
        """ .wav file for verify training."""
        basename = self.basename_params(taskname, params)
        basename += "_%i" % count
        return os.path.join(self.works_dir, basename)

    def make_stable_filename(self, params, stable_K, count):
        """ .wav file for automatic training of stable K."""
        basename = self.basename_params("stable", params)
        basename += "_%.3f" % stable_K
        basename += "_%i" % count
        return os.path.join(self.works_dir, basename)

    def make_attack_filename(self, taskname, params, count):
        """ .wav file for automatic training of initial Fb."""
        basename = self.basename_params(taskname, params)
        basename += "_%i" % count
        return os.path.join(self.works_dir, basename)

    def make_dampen_filename(self, taskname, params, dampen, count):
        """ .wav file for automatic dampening training."""
        basename = self.basename_params(taskname, params)
        basename += "_%.3f" % dampen
        basename += "_%i" % count
        return os.path.join(self.works_dir, basename)

    def make_audio_filename(self, params):
        """ audio .wav file. """
        basename = self.basename_params("audio", params)
        filename = os.path.join(self.works_dir, basename)
        return filename

    @staticmethod
    def get_audio_params(filename):
        """ parameters extracted from a .wav filename. """
        basepath = os.path.basename(filename)
        try:
            float( os.path.splitext(basepath)[1] )
            basename = os.path.splitext(basepath)[0]
        except:
            basename = basepath
        params = basename.split('_')[1:]
        audio_params = vivi_types.AudioParams(
            int(params[0]), float(params[1]),
            float(params[2]), float(params[3]), float(params[4]))
        return audio_params

    def get_audio_params_extra(self, filename):
        """ parameters extracted from a .wav filename, including
            extra and count. """
        if filename[-4:] == '.wav':
            filename = filename[:-4]
        audio_params = self.get_audio_params(filename)
        basepath = os.path.basename(filename)
        try:
            float( os.path.splitext(basepath)[1] )
            basename = os.path.splitext(basepath)[0]
        except:
            basename = basepath
        params = basename.split('_')[1:]
        if len(params) == 7:
            extra = float(params[5])
        else:
            extra = None
        count = int(params[-1])
        return audio_params, extra, count

    def get_audio_params_count(self, filename):
        """ parameters extracted from a .wav filename, including
            count. """
        audio_params = self.get_audio_params(filename)
        basename = os.path.splitext(os.path.basename(filename))[0]
        params = basename.split('_')[1:]
        count = int(params[5])
        return audio_params, count


    def make_zoom_filename(self, params):
        """ save "zoomed" audio to a .wav file. """
        base_basename = "audio-9_%i_%.3f_%.3f_%.3f_%.3f_z_" % (
            params.string_number,
            float(params.finger_midi),
            params.bow_bridge_distance,
            params.bow_force,
            params.bow_velocity)
        count = 0
        potential_filename = os.path.join(self.works_dir, base_basename)
        train_dir_filename = os.path.join(self.train_dir, base_basename)
        # resolve any "hash" collisions
        # really ugly hack!
        #print potential_filename
        while ( os.path.exists(potential_filename+'%04i'%count+'.wav') or
                os.path.exists(train_dir_filename+'%04i'%count+'.wav') or 
                os.path.exists(os.path.join(self.train_dir,'violin',
                    base_basename+'%04i'%count+'.wav')) or
                os.path.exists(os.path.join(self.train_dir,'viola',
                    base_basename+'%04i'%count+'.wav')) or
                os.path.exists(os.path.join(self.train_dir,'cello',
                    base_basename+'%04i'%count+'.wav'))
                ):
            count += 1
            if count >= 1000:
                print "Vivi error: training_dir: 999 files with same params!"
                break
        filename = potential_filename + ('%04i' % count)
        #print filename
        return filename

    def move_works_to_train(self, src):
        """ moves a file from works dir to train dir. """
        dest = os.path.join(self.train_dir,
            os.path.basename(src))
        shutil.move(src+'.wav', dest+'.wav')
        shutil.move(src+'.actions', dest+'.actions')
        shutil.move(src+'.forces.wav', dest+'.forces.wav')
        actions2csv.main(dest+'.actions')
        return dest

    def get_cats_dir(self):
        return self.works_dir

    def get_cats_name(self, filename):
        """ Gets the basename of the .cats file corresponding to a
            .wav file.  They might both be in the works dir, but
            if the original .wav file was in the train dir, then
            the .cats file will be in the works dir instead. """
        if filename.startswith(self.train_dir):
            dest = filename.replace(self.train_dir, self.works_dir)
        else:
            dest = filename
        return dest

    def get_task_files(self, taskname, st, bow_bridge_distance, bow_velocity):
        """ gets stable or attack files. """
        filename_pattern = str("%s_%i_*_%.3f_*_%.3f_*.wav"
            % (taskname, st, bow_bridge_distance, bow_velocity))
        task_files = glob.glob(os.path.join(self.works_dir, filename_pattern))
        task_files = filter(lambda x: ".forces" not in x, task_files)
        task_files = filter(lambda x: "-s0.wav" not in x,
            task_files)
        task_files = filter(lambda x: "-s1.wav" not in x,
            task_files)
        task_files = filter(lambda x: "-s2.wav" not in x,
            task_files)
        task_files = filter(lambda x: "-s3.wav" not in x,
            task_files)

        def sort_task_files(filename):
            split = filename.split('_')
            combo = []
            # ick this is ugly!
            for y in split:
                try:
                    combo.append(float(y))
                except:
                    combo.append(y)
            return combo
        task_files.sort(key=sort_task_files)
        return task_files

    @staticmethod
    def delete_files(files_to_delete):
        """ deletes files, used to clean out parts of the working dir """
        for filename in files_to_delete:
            os.remove(filename)

    def get_music_dir(self):
        return self.music_dir

    def get_ly_movie_dir(self):
        return os.path.join(self.movie_dir,
            self.ly_basename)

    def get_ly_movie_preview(self):
        return os.path.join(self.movie_dir,
            self.ly_basename + "-preview.avi")

    def get_ly_movie(self):
        return os.path.join(self.movie_dir,
            self.ly_basename + "-movie.avi")

    def get_notes_files(self):
        notes_files = glob.glob(os.path.join(self.music_dir,
            self.ly_basename + '*.notes'))
        notes_files.sort()
        return notes_files

    def set_ly_basename(self, ly_filename):
        filename = os.path.relpath(ly_filename)
        self.ly_original = ly_filename
        self.ly_basename = filename.replace(".ly", "")

    def get_ly_original(self):
        return self.ly_original

    def get_ly_extra(self, extension=""):
        return os.path.join(self.music_dir,
                self.ly_basename + extension)

    def get_ly_basename(self):
        return self.ly_basename

    def set_notes_from_ly(self):
        search = os.path.join(self.music_dir,
                self.ly_basename + "*.notes")
        filenames = glob.glob(search)
        filenames.sort()
        # TODO: function-ify
        self.notes_all = []
        for filename in filenames:
            filename = filename.replace(".notes", "")
            filename = filename.replace(self.music_dir, "")
            if filename[0] == '/':
                filename = filename[1:]
            self.notes_all.append(filename)

    def set_notes_index(self, index):
        self.notes = self.notes_all[index]

    def get_notes(self):
        return os.path.join(self.music_dir, self.notes + ".notes")

    def get_notes_ext(self, extension=""):
        return os.path.join(self.music_dir, self.notes + extension)

    def make_notes_next(self, extension=""):
        latest = self.get_notes_last(extension)
        if latest:
            if extension:
                latest = latest.replace(extension, "")
            number = int(latest[-3:])
            latest = latest[:-4]
            if extension == ".alterations":
                number += 1
        else:
            latest = os.path.join(self.music_dir, self.notes)
            number = 0
        number_text = "_%03i" % number
        if extension:
            filename = latest + number_text + extension
        else:
            filename = latest + number_text
        return filename

    def get_notes_last(self, extension="", penultimate=False):
        search = os.path.join(self.music_dir,
                self.notes + "*" + extension)
        filenames = glob.glob(search)
        filenames.sort()
        if not filenames:
            return None
        if penultimate:
            if len(filenames) >= 2:
                filename = filenames[-2]
            else:
                return None
        else:
            filename = filenames[-1]
        if not extension:
            filename = os.path.splitext(filename)[0]
        return filename

    def get_hills_last(self, extension=""):
        search = os.path.join(self.hills_dir,
                self.notes + "*" + extension)
        filenames = glob.glob(search)
        filenames.sort()
        if filenames:
            return filenames[-1]
        else:
            return None

    def make_hills_next(self, extension=""):
        latest = self.get_hills_last(extension)
        if latest:
            if extension:
                latest = latest.replace(extension, "")
            number = int(latest[-3:])
            latest = latest[:-4]
            if extension == ".alterations":
                number += 1
        else:
            latest = os.path.join(self.hills_dir, self.notes)
            number = 0
        number_text = "_%03i" % number
        if extension:
            filename = latest + number_text + extension
        else:
            filename = latest + number_text
        filename_dirname = os.path.dirname(filename)
        if not os.path.isdir(filename_dirname):
            os.makedirs(filename_dirname)
        return filename



