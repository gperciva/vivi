#ifndef ACTIONS_FILE
#define ACTIONS_FILE
#include <stdio.h>

const unsigned int MAX_LINE_LENGTH = 256;

class ActionsFile {
public:
    /**
     * @brief mundane constructor.
     * @param[in] filename Filename; \c ".actions" is recommended.
     * @param[in] buffer_size Number of actions to store
     * before writing to disk.
     * @warning ActionsFile does not check whether it received the
     * memory it attempted to allocate; if this occurs, it will
     * probably result in an unchecked exception crash.
     */
    ActionsFile(const char *filename, unsigned int buffer_size=1024);

    /// @brief writes data to disk before quitting
    ~ActionsFile();

    void wait(double seconds);
    void skipStart(double seconds);
    void skipStop(double seconds);
    void finger(double seconds, unsigned int string_number,
                double position);
    void pluck(double seconds, unsigned int string_number,
               double position, double force);
    void bow(double seconds, unsigned int string_number,
             double position, double force, double velocity);

    void category(double seconds, unsigned int category);
    // writes buffer to file immediately
    void comment(const char *text);

private:
    void writeBuffer();

    unsigned int size;
    unsigned int index;
    FILE *outfile;

    enum ActionType {
        ACTION_SKIPSTART,
        ACTION_SKIPSTOP,
        ACTION_WAIT,
        ACTION_FINGER,
        ACTION_PLUCK,
        ACTION_BOW,
        ACTION_CATEGORY,
    };

    typedef struct {
        ActionType type;
        double seconds;
        unsigned int string_number;
        double position;
        double force;
        double velocity;
    } ActionData;

    ActionData *data;
};
#endif

