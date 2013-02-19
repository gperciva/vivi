#include "controller_params.h"
#include <stdio.h>
#include <string.h>

ControllerParams::ControllerParams(const char *filename)
{
    strncpy(m_filename, filename, CP_MAX_FILENAME_LENGTH-1);
}

ControllerParams::~ControllerParams()
{
    // require explicit write now
    //write_file();
}

void ControllerParams::load_file()
{
    FILE* fd = fopen(m_filename, "r");
    if (fd != NULL) {
        int num_read;
        for (int i=0; i < BASIC_FINGER_MIDIS_SIZE; i++) {
            num_read = fscanf(fd, "%lf\n", &attack_forces[i]);
            if (num_read != 1) {
                printf("ERROR: Controller Params: problem reading attacks from %s\n", m_filename);
            }
            num_read = fscanf(fd, "%lf\n", &mid_forces_low[i]);
            if (num_read != 1) {
                printf("ERROR: Controller Params: problem reading mid forces from %s\n", m_filename);
            }
            num_read = fscanf(fd, "%lf\n", &mid_forces_high[i]);
            if (num_read != 1) {
                printf("ERROR: Controller Params: problem reading mid forces from %s\n", m_filename);
            }
            num_read = fscanf(fd, "%lf\n", &stable_K[i]);
            if (num_read != 1) {
                printf("ERROR: Controller Params: problem reading mid forces from %s\n", m_filename);
            }
        }
        //num_read = fscanf(fd, "%lf\n%lf\n",
        //                      &dampen_normal, &dampen_slur);
        num_read = fscanf(fd, "%lf\n",
                              &dampen_normal);
        if (num_read != 1) {
            printf("ERROR: Controller Params: problem reading dampen from %s\n", m_filename);
        }
        fclose(fd);
    } else {
        for (int i=0; i < BASIC_FINGER_MIDIS_SIZE; i++) {
            stable_K[i] = 1.0;
            attack_forces[i] = 0.0;
            mid_forces_low[i] = 0.0;
            mid_forces_high[i] = 0.0;
        }
        dampen_normal = 0.0;
    }
}

void ControllerParams::write_file()
{
    FILE* outfile = fopen(m_filename, "w");
    char textline[CP_MAX_LINE_LENGTH];

    for (int i=0; i < BASIC_FINGER_MIDIS_SIZE; i++) {
        sprintf(textline, "%.4f\n", attack_forces[i]);
        fwrite(textline, sizeof(char), strlen(textline), outfile);
        sprintf(textline, "%.4f\n", mid_forces_low[i]);
        fwrite(textline, sizeof(char), strlen(textline), outfile);
        sprintf(textline, "%.4f\n", mid_forces_high[i]);
        fwrite(textline, sizeof(char), strlen(textline), outfile);
        sprintf(textline, "%.4f\n", stable_K[i]);
        fwrite(textline, sizeof(char), strlen(textline), outfile);
    }
    sprintf(textline, "%.4f\n", dampen_normal);
    fwrite(textline, sizeof(char), strlen(textline), outfile);
    //sprintf(textline, "%.4f\n", dampen_slur);
    //fwrite(textline, sizeof(char), strlen(textline), outfile);

    fclose(outfile);
}

