#ifndef CONTROLLER_PARAMS
#define CONTROLLER_PARAMS

#include "vivi_defines.h"

const int CP_MAX_FILENAME_LENGTH = 256;
const int CP_MAX_LINE_LENGTH = 256;

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
    double stable_K;
    double attack_forces[BASIC_FINGER_MIDIS_SIZE];
    double accuracy;
    double dampen;
    // accessors for iffy python swig stuff
    void set_force(int index, double value) {
        attack_forces[index] = value;
    };
    double get_attack_force(int index) {
        return attack_forces[index];
    };

private:
    char m_filename[CP_MAX_FILENAME_LENGTH];
};
#endif

