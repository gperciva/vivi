import os

# TODO: hard-coded python verison!
Help("""
old message, incorrect now.

Build stuff:
    scons

Docs:  (requires doxygen)
    scons doc

Install stuff to:  bin/ include/ lib/
    scons --prefix=DIR install
# I use:
    scons --prefix=$HOME/.usr/ install
""")



### destination
AddOption('--prefix',
    dest='prefix',
    type='string',
    nargs=1,
    action='store',
    metavar='DIR',
    help='installation prefix')
env = Environment(
    ENV = os.environ,
    PREFIX = GetOption('prefix')
)
env["CC"] = os.getenv("CC") or env["CC"]
env["CXX"] = os.getenv("CXX") or env["CXX"]

env.ParseConfig('pkg-config --cflags --libs artifastring')
env.ParseConfig('pkg-config --cflags --libs monowav')

env['ears_files'] = Split("""
    ears.cpp
""")
env['vivi_controller_files'] = Split("""
    vivi_controller.cpp
    controller_params.cpp
""")


env.Append(
    #CPPFLAGS=Split("-fPIC -O3 -g "),
    CPPFLAGS=Split("-fPIC -O3 -march=native -g"),
    #CPPFLAGS=Split("-fPIC -g -Wall -Wextra"),
    CPPPATH=[
        "/usr/include/python2.6",
        "/usr/include/python2.7",
        ],
)
env.Append(
    LINKFLAGS=env["CPPFLAGS"],
)

### configure
has_swig = True
has_doxygen = True
if (not env.GetOption('clean')) and (not env.GetOption('help')):
    config = Configure(env)
    ### test for marsyas
    status = config.CheckLibWithHeader('marsyas',
        'marsyas/MarSystemManager.h', 'c++')
    if not status:
        print("Need marsyas!")
        Exit(1)
    ### test for aubio
    status = config.CheckLibWithHeader('aubio',
        'aubio/aubio.h', 'c')
    if not status:
        print("Need aubio!")
        Exit(1)
    ### tests for gnu science library
    status = config.CheckLibWithHeader(['gsl', 'gslcblas'],
        'gsl/gsl_randist.h', 'c++')
    if not status:
        print("Need GNU science library: gsl and/or gslcblas!")
        Exit(1)
    ### test for artifastring
    #status = config.CheckLibWithHeader('artifastring',
    #    'violin_instrument.h', 'c++')
    #if not status:
    #    print("Need artifastring!")
    #    Exit(1)

    ### test for swig
    #
    status = config.CheckCXXHeader('Python.h')
    if not status:
        print("Need Python.h")
        has_swig = False
    #
    status = config.CheckLib('python2.7')
    if status:
        env["pythonver"] = "2.7"
    else:
        status = config.CheckLib('python2.6')
        if status:
            env["pythonver"] = "2.6"
        else:
            print("Need python 2.6 or 2.7")
            has_swig = False
    #
    status = WhereIs('swig')
    if not status:
        print("Need swig")
        has_swig = False
    #
    ### test for doc
    status = WhereIs('doxygen')
    if not status:
        print("Need doxygen")
        has_doxygen = False
    #
    #
    env = config.Finish()

if not has_swig:
    print("Need swig and python devel libraries!")
    Exit(1)


### setup for installing
env.Alias('install', '$PREFIX')

Export('env')

def process_dir(dirname):
    sconscript_filename = dirname + os.sep + "SConscript"
    build_dirname = 'build' + os.sep + dirname
    SConscript(sconscript_filename,
	variant_dir=build_dirname, duplicate=0)
    Clean(sconscript_filename, build_dirname)

process_dir('src')
# this one needs swig!
### FIXME: debug only
process_dir('swig')
process_dir('python')

#if (has_doxygen) and ('doc' in COMMAND_LINE_TARGETS):
#    process_dir('doc')

Clean('.', 'build')
#env.Clean("distclean", [".sconsign.dblite", ".sconf_temp", "config.log"])

