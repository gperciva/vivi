
#ifndef DYNAMICS_H
#define DYNAMICS_H

// forte, mf, mp, piano
const int NUM_DYNAMICS = 4;

double get_distance(int inst, const double dyn);
double get_velocity(int inst, const double dyn);

#endif

