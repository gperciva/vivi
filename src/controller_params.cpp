#include "controller_params.h"
#include <stdio.h>
#include <string.h>

ControllerParams::ControllerParams(const char *filename)
{
    strncpy(m_filename, filename, CP_MAX_FILENAME_LENGTH-1);
}

ControllerParams::~ControllerParams()
{
    write_file();
}

void ControllerParams::load_file()
{
    FILE* fd = fopen(m_filename, "r");
    if (fd != NULL) {
        for (int i=0; i < BASIC_FINGER_MIDIS_SIZE; i++) {
            int num_read = fscanf(fd, "%lf\n", &attack_forces[i]);
            if (num_read != 1) {
                printf("ERROR: Controller Params: problem reading file\n");
            }
        }
        int num_read = fscanf(fd, "%lf\n%lf\n%lf",
                              &stable_K, &accuracy, &dampen);
        if (num_read != 3) {
            printf("ERROR: Controller Params: problem reading file\n");
        }
        fclose(fd);
    } else {
        stable_K = 1.0;
        for (int i=0; i < BASIC_FINGER_MIDIS_SIZE; i++) {
            attack_forces[i] = 0.0;
        }
        accuracy = 0.0;
        dampen = 1.0;
    }
}

void ControllerParams::write_file()
{
    FILE* outfile = fopen(m_filename, "w");
    char textline[CP_MAX_LINE_LENGTH];

    for (int i=0; i < BASIC_FINGER_MIDIS_SIZE; i++) {
        sprintf(textline, "%.3f\n", attack_forces[i]);
        fwrite(textline, sizeof(char), strlen(textline), outfile);
    }
    sprintf(textline, "%.3f\n", stable_K);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
    sprintf(textline, "%.3f\n", accuracy);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
    sprintf(textline, "%.3f\n", dampen);
    fwrite(textline, sizeof(char), strlen(textline), outfile);

    fclose(outfile);
}

