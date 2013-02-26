#ifndef CONTROLLER_PARAMS
#define CONTROLLER_PARAMS

#include "vivi_defines.h"

const int CP_MAX_FILENAME_LENGTH = 256;
const int CP_MAX_LINE_LENGTH = 256;

#include <stdio.h>

class ControllerParams {
public:
    /**
     * @brief mundane constructor.
     * @param[in] filename Filename; \c ".vivi" is recommended.
     * reads data from file if it exists
     */
    ControllerParams(const char *filename);

    /// @brief writes data to disk before quitting
    ~ControllerParams();

    void load_file();
    void write_file();

    // main data
    double stable_K[BASIC_FINGER_MIDIS_SIZE];
    void set_stable_K(int index, double value) {
        stable_K[index] = value;
    };
    double get_stable_K(int index) {
        return stable_K[index];
    };

    double attack_forces[BASIC_FINGER_MIDIS_SIZE];
    double mid_forces_low[BASIC_FINGER_MIDIS_SIZE];
    double mid_forces_high[BASIC_FINGER_MIDIS_SIZE];
    double dampen_normal;
    //double dampen_slur;
    // accessors for iffy python swig stuff
    void set_force(int index, double value) {
        attack_forces[index] = value;
    };
    double get_attack_force(int index) {
        return attack_forces[index];
    };
    void set_mid_force_low(int index, double value) {
        mid_forces_low[index] = value;
    };
    double get_mid_force_low(int index) {
        return mid_forces_low[index];
    };
    void set_mid_force_high(int index, double value) {
        mid_forces_high[index] = value;
    };
    double get_mid_force_high(int index) {
        return mid_forces_high[index];
    };

private:
    char m_filename[CP_MAX_FILENAME_LENGTH];
};
#endif

