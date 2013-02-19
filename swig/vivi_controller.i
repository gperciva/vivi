%module vivi_controller
%{
#include "ears.h"
#include "vivi_controller.h"
#include "vivi_note_params.h"
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


%include "std_string.i"

%include "ears.h"
%include "vivi_controller.h"
%include "vivi_note_params.h"

/*
  useful for quick experiments with RMS of output
*/
%include "carrays.i"
%array_class(double, doubleArray);


