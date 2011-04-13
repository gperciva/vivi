#include "actions_file.h"
#include <string.h>

ActionsFile::ActionsFile(const char *filename, unsigned int buffer_size)
{
    size = buffer_size;
    data = new ActionData[size];
    index = 0;
    outfile = fopen(filename, "w");
}

ActionsFile::~ActionsFile()
{
    writeBuffer();
    fclose(outfile);
    delete [] data;
}

void ActionsFile::wait(double seconds) {
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_WAIT;
    action.seconds = seconds;
    data[index] = action;
    index++;
}

void ActionsFile::skipStart(double seconds) {
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_SKIPSTART;
    action.seconds = seconds;
    data[index] = action;
    index++;
}

void ActionsFile::skipStop(double seconds) {
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_SKIPSTOP;
    action.seconds = seconds;
    data[index] = action;
    index++;
}

void ActionsFile::finger(double seconds, unsigned int string_number,
                         double position)
{
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_FINGER;
    action.seconds = seconds;
    action.string_number = string_number;
    action.position = position;
    data[index] = action;
    index++;
}

void ActionsFile::pluck(double seconds, unsigned int string_number,
                        double position, double force)
{
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_PLUCK;
    action.seconds = seconds;
    action.string_number = string_number;
    action.position = position;
    action.force = force;
    data[index] = action;
    index++;
}

void ActionsFile::bow(double seconds, unsigned int string_number,
                      double position, double force, double velocity)
{
    if ((index + 1) >= size) {
        writeBuffer();
    }
    ActionData action;
    action.type = ACTION_BOW;
    action.seconds = seconds;
    action.string_number = string_number;
    action.position = position;
    action.force = force;
    action.velocity = velocity;
    data[index] = action;
    index++;
}

void ActionsFile::writeBuffer()
{
    for (unsigned int i = 0; i < index; i++) {
        ActionData actions = data[i];
        char textline[256];

        switch (actions.type) {
        case ACTION_WAIT:
            sprintf(textline, "w\t%f\n",
                    actions.seconds);
            break;
        case ACTION_SKIPSTART:
            sprintf(textline, "s\t%f\n",
                    actions.seconds);
            break;
        case ACTION_SKIPSTOP:
            sprintf(textline, "k\t%f\n",
                    actions.seconds);
            break;
        case ACTION_FINGER:
            sprintf(textline, "f\t%f\t%i\t%f\n",
                    actions.seconds,
                    actions.string_number, actions.position);
            break;
        case ACTION_PLUCK:
            sprintf(textline, "p\t%f\t%i\t%f\t%f\n",
                    actions.seconds,
                    actions.string_number, actions.position,
                    actions.force);
            break;
        case ACTION_BOW:
            sprintf(textline, "b\t%f\t%i\t%f\t%f\t%f\n",
                    actions.seconds,
                    actions.string_number, actions.position,
                    actions.force, actions.velocity);
            break;
        }
        fwrite(textline, sizeof(char), strlen(textline), outfile);
    }
    index = 0;
}

