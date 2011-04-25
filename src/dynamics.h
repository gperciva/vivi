
#ifndef DYNAMICS_H
#define DYNAMICS_H

// forte, mf, mp, piano
const unsigned int NUM_DYNAMICS = 4;

// TODO: make static ?  eliminate class?  namespace?
class Dynamics {
public:
    Dynamics();
    ~Dynamics();

    double get_distance(const double dyn);
    double get_velocity(const double dyn);

private:
    inline double interpolate(const double x,
                              const double x0, const double y0,
                              const double x1, const double y1);

};

#endif

