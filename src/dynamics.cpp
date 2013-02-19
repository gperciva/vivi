
#include "dynamics.h"
#include <math.h>

#include "vivi_defines.h"
//#include <stdio.h>

const double BOW_BRIDGE_DISTANCES [NUM_DISTINCT_INSTRUMENTS][NUM_DYNAMICS] =
{   // f  mf,   mp,   p
    {0.092, 0.134, 0.154, 0.186},  // violin
    {0.092, 0.134, 0.154, 0.186},  // viola
    //{0.117, 0.134, 0.154, 0.186},  // cello
    //{0.117, 0.134, 0.154, 0.186},  // cello
    //{0.117, 0.134, 0.154, 0.186}  // cello
    {0.092, 0.134, 0.154, 0.186},  // cello
    //{0.073, 0.092, 0.134, 0.154},  // cello
};
const double BOW_VELOCITIES [NUM_DISTINCT_INSTRUMENTS][NUM_DYNAMICS] =
{   // f  mf,   mp,   p
    {0.40, 0.33, 0.26, 0.20}, // violin
    {0.40, 0.33, 0.26, 0.20}, // viola
    {0.40, 0.33, 0.26, 0.20}  // cello
};
//{0.30, 0.26, 0.23, 0.20};

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


double get_distance(int inst, double dyn) {
    const int x0 = floor(dyn);
    const int x1 = ceil(dyn);
    return interpolate(dyn,
                       x0, BOW_BRIDGE_DISTANCES [inst][x0],
                       x1, BOW_BRIDGE_DISTANCES [inst][x1]);
}

double get_velocity(int inst, double dyn) {
    const int x0 = floor(dyn);
    const int x1 = ceil(dyn);
    return interpolate(dyn,
                       x0, BOW_VELOCITIES [inst][x0],
                       x1, BOW_VELOCITIES [inst][x1]);
}



