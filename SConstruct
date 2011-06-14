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

#print env.Dump()

env['ears_files'] = Split("""
	ears.cpp
""")
env['vivi_controller_files'] = Split("""
	vivi_controller.cpp
""")


env.Append(
#	CPPFLAGS=Split("-O3 -fPIC -funroll-loops"),
	CPPFLAGS=Split("-g -fbounds-check -Wall -Wextra"),
	CPPPATH=[
		"/usr/include/python2.6",
		],
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
	### tests for gnu science library
	status = config.CheckLibWithHeader(['gsl', 'gslcblas'],
		'gsl/gsl_randist.h', 'c++')
	if not status:
		print("Need GNU science library: gsl and/or gslcblas!")
		Exit(1)
	### test for artifastring
	#status = config.CheckLibWithHeader('artifastring',
	#	'violin_instrument.h', 'c++')
	#if not status:
	#	print("Need artifastring!")
	#	Exit(1)

	### test for swig
	#
	status = config.CheckCXXHeader('Python.h')
	if not status:
		print("Need Python.h")
		has_swig = False
	#
	status = config.CheckLib('python2.6')
	if not status:
		print("Need python2.6")
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
	


### setup for installing
env.Alias('install', '$PREFIX')
env.ParseConfig('pkg-config --cflags --libs artifastring')
env.ParseConfig('pkg-config --cflags --libs monowav')

Export('env')

def process_dir(dirname):
	sconscript_filename = dirname + os.sep + "SConscript"
	build_dirname = 'build' + os.sep + dirname
	SConscript(sconscript_filename, build_dir=build_dirname, duplicate=0)
	Clean(sconscript_filename, build_dirname)

process_dir('src')
# this one needs swig!
process_dir('swig')
process_dir('python')

#if (has_doxygen) and ('doc' in COMMAND_LINE_TARGETS):
#	process_dir('doc')

Clean('.', 'build')
#env.Clean("distclean", [".sconsign.dblite", ".sconf_temp", "config.log"])

