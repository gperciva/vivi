#!/usr/bin/env python
""" deals with basic training of dynamics in training collection """

import dynamics
import utils

import vivi_defines

#FINGER_MIDIS = [0.0, 4.0, 6.0]
FINGER_MIDIS = [0, 1, 6]

def _get_matching_fingers(inst_type, dyn, coll, files):
    """ finds all items in coll that match the dynamic.  Splits
        matching items into lists matching FINGER_MIDIS pitches."""
    ### get all items on the right level
    def is_level_match(pair, level_bbd, level_bv):
        """ does a collection pair match the level parameters? """
        params = files.get_audio_params(pair[0])
        return (utils.almost_equals(params.bow_bridge_distance, level_bbd) and
            utils.almost_equals(params.bow_velocity, level_bv))
    # "level" parameters
    bbd = dynamics.get_distance(inst_type, dyn)
    bv  = dynamics.get_velocity(inst_type, dyn)
    match_level = filter(lambda(pair): is_level_match(pair, bbd, bv),
                        coll.coll)

    ### split forces+cats into fingers
    def is_finger_match(pair, finger_midi, files):
        """ does a collection pair match the level parameters? """
        params = files.get_audio_params(pair[0])
        return utils.almost_equals(params.finger_midi, finger_midi)
    # actual splitting
    forces = [[], [], []]
    cats = [[], [], []]
    unknowns = [[], [], []]
    for pair in match_level:
        params = files.get_audio_params(pair[0])
        for i, fm in enumerate(FINGER_MIDIS):
            if is_finger_match(pair, fm, files):
                cat = pair[1]
                if coll.is_cat_valid(cat):
                    cats[i].append(cat)
                    forces[i].append(params.bow_force)
                else:
                    unknowns[i].append(params.bow_force)
    return forces, cats, unknowns

def _get_between(forces, cats, cat, unknowns):
    """ finds a force between the boundaries """
    # get extremes
    combo = zip(forces, cats)
    higher_force = min(map(lambda(x):x[0],
                           filter(lambda(x):x[1]>cat, combo)))
    lower_force  = max(map(lambda(x):x[0],
                           filter(lambda(x):x[1]<cat, combo)))
    # deal with unknowns
    unknown_between = filter(lambda(x):x>lower_force and x<higher_force,
                             unknowns)
    between = [lower_force] + unknown_between + [higher_force]
    distances = [y-x for x, y in zip(between[:-1], between[1:])]
    biggest_distance = max(distances)
    biggest_distance_index = distances.index(biggest_distance)
    force = between[biggest_distance_index] + biggest_distance/2.0
    return force

def unfulfilled(cat, cats, need):
   if not cat in cats and cat in need:
       return True
   else:
       return False

def _get_missing_cat(forces, cats, unknowns, need=None):
    """ finds the 'next missing force' to get, according to the
        basic training plan. """
    if not need:
        return None

    ### start in the "middle-ish"
    if not forces:
        force = 1.0
    ### get extremes
    elif unfulfilled(vivi_defines.CATEGORIES_EXTREME, cats, need):
        return vivi_defines.CATEGORIES_EXTREME
        force = 2.0 * max(forces+unknowns)
    elif unfulfilled(-vivi_defines.CATEGORIES_EXTREME, cats, need):
        return -vivi_defines.CATEGORIES_EXTREME
        force = 0.5 * min(forces+unknowns)
    ### find center
    elif unfulfilled(0, cats, need):
        return 0
        # we need the extremes to calculate the force!
        if not vivi_defines.CATEGORIES_EXTREME in cats:
            force = 2.0 * max(forces+unknowns)
        elif not -vivi_defines.CATEGORIES_EXTREME in cats:
            force = 0.5 * max(forces+unknowns)
        else:
            force = _get_between(forces, cats, 0, unknowns)
    ### no forces needed
    else:
        force = None
    return force

def get_next_basic(inst_type, dyn, coll, files):
    """ the 'main' function of Basic; it returns the
        (force, finger_midi) that should next be judged by the
        human, or None if no training is needed. """
    ### at least one of each cat
    all_cats = [ x[1] for x in coll.coll ]
    for cat in range(-vivi_defines.CATEGORIES_EXTREME,
        vivi_defines.CATEGORIES_EXTREME+1):
        if not cat in all_cats:
            return (cat, 0)

    ### at least one of this dynamic
    forces, cats, unknowns = _get_matching_fingers(
        inst_type, dyn, coll, files)
    flat_cats = [item for sublist in cats for item in sublist]
    if not 0 in flat_cats:
        return (0, 0)
    ### we need the extreme dynamics
    if dyn == 0:
        if not vivi_defines.CATEGORIES_EXTREME in flat_cats:
            return (vivi_defines.CATEGORIES_EXTREME, 0)
    if dyn == 3:
        if not -vivi_defines.CATEGORIES_EXTREME in flat_cats:
            return (-vivi_defines.CATEGORIES_EXTREME, 0)

    ### at least two unique finger positions
    all_fingers = [ files.get_audio_params(x[0]).finger_midi
                for x in coll.coll ]
    if len(set((all_fingers))) < 2:
        if 0 in all_fingers:
            return (0, 7)
        else:
            return (0, 0)
    return None


    #forces, cats, unknowns = _get_matching_fingers(dyn, coll, files)
    #for i, finger_midi in enumerate(FINGER_MIDIS):
    if True:
        need = [0]
        if dyn == 0:
            need += [vivi_defines.CATEGORIES_EXTREME]
        elif dyn == 3:
            need += [-vivi_defines.CATEGORIES_EXTREME]
        print need
        cat = _get_missing_cat(forces[i], cats[i], unknowns[i], need)
        print "basic", dyn, cat
        if cat is not None:
            return (cat, finger_midi)
    # FIXME: hard-coding for 5 categories
    # only once for each string
    if dyn == 0:
        cats = [item for sublist in cats for item in sublist]
        need = []
        need += [-1]
        need += [1]
        for n in need:
            if unfulfilled(n, cats, need):
                return (n, 0)
    return None


