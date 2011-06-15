
#include "controller_params.h"
#include <stdio.h>

int main() {
    ControllerParams *g_str = new ControllerParams("final/0_0.data");
    g_str->load_file();

    printf("%f   %f %f %f\n",
           g_str->stable_K,
           g_str->attack_forces[0],
           g_str->attack_forces[1],
           g_str->attack_forces[2]
          );


    delete g_str;
}
