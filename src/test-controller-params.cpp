
#include "controller_params.h"
#include <stdio.h>

int main() {
    ControllerParams *g_str = new ControllerParams("final/violin/0_0.data");
    g_str->load_file();

    printf("%lf   %lf %lf %lf\n",
           g_str->stable_K[0],
           g_str->attack_forces[0],
           g_str->attack_forces[1],
           g_str->attack_forces[2]
          );

    g_str->write_file();
    delete g_str;
}
