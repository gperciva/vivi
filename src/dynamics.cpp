
#include "dynamics.h"
#include <math.h>

//#include <stdio.h>

const double BOW_BRIDGE_DISTANCES [NUM_DYNAMICS] =
{0.08, 0.10, 0.12, 0.14};
const double BOW_VELOCITIES [NUM_DYNAMICS] =
{0.40, 0.33, 0.26, 0.20};

/*
 I haven't thought about it; this just comes from:
 http://en.wikipedia.org/wiki/Linear_interpolation
*/
inline double interpolate(const double x,
                          const double x0, const double y0,
                          const double x1, const double y1)
{
    if ((x1-x0) == 0) {
        return y0;
    } else {
        return y0 + (x-x0)*(y1-y0)/(x1-x0);
    }
}


double get_distance(double dyn) {
    const int x0 = floor(dyn);
    const int x1 = ceil(dyn);
    return interpolate(dyn,
                       x0, BOW_BRIDGE_DISTANCES [x0],
                       x1, BOW_BRIDGE_DISTANCES [x1]);
}

double get_velocity(double dyn) {
    const int x0 = floor(dyn);
    const int x1 = ceil(dyn);
    return interpolate(dyn,
                       x0, BOW_VELOCITIES [x0],
                       x1, BOW_VELOCITIES [x1]);
}



