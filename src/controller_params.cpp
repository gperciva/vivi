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
        int num_read = fscanf(fd, "%lf\n%lf\n%lf\n%lf\n%lf\n%lf",
                              &attack_forces[0], &attack_forces[1],
                              &attack_forces[2],
                              &stable_K, &accuracy, &dampen);
        fclose(fd);
        if (num_read != 6) {
            printf("ERROR: Controller Params: problem reading file\n");
        }
    } else {
        stable_K = 1.0;
        attack_forces[0] = attack_forces[1] = attack_forces[2] = 0.0;
        accuracy = 0.0;
        dampen = 0.0;
    }
}

void ControllerParams::write_file()
{
    FILE* outfile = fopen(m_filename, "w");
    char textline[CP_MAX_LINE_LENGTH];

    sprintf(textline, "%.3f\n", attack_forces[0]);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
    sprintf(textline, "%.3f\n", attack_forces[1]);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
    sprintf(textline, "%.3f\n", attack_forces[2]);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
    sprintf(textline, "%.3f\n", stable_K);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
    sprintf(textline, "%.3f\n", accuracy);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
    sprintf(textline, "%.3f\n", dampen);
    fwrite(textline, sizeof(char), strlen(textline), outfile);

    fclose(outfile);
}

