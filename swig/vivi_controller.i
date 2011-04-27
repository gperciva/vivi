%module vivi_controller
%{
#include "ears.h"
#include "vivi_controller.h"
%}

/*
copy and paste from:
http://stackoverflow.com/questions/2510696/allowing-threads-from-python-after-calling-a-blocking-i-o-code-in-a-python-extens
*/
%exception {
    Py_BEGIN_ALLOW_THREADS
    $action
    Py_END_ALLOW_THREADS
}


%include "ears.h"
%include "vivi_controller.h"

