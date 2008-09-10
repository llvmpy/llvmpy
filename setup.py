#!/usr/bin/env python

import sys, os
from distutils.core import setup, Extension


def _run(cmd):
    return os.popen(cmd).read().rstrip()


def get_libs_and_objs(llvm_config, components):
    parts = _run(llvm_config + ' --libs ' + ' '.join(components)).split()
    libs = []
    objs = []
    for part in parts:
        if part.startswith('-l'):
            libs.append(part[2:])
        else:
            assert part.endswith('.o')
#            objs.append(part[:-2])
            objs.append(part) # eh, looks like we need the .o after all
    return (libs, objs)


def get_llvm_config():

    # get from command-line, or use default
    lc = 'llvm-config'
    i = 0
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith('--llvm-config='):
            del sys.argv[i]
            lc = arg.split('=')[1]
        else:
            i += 1
    
    # see if it works
    version = _run(lc + ' --version')
    if version == '':
        return (lc, False) # didn't work
    
    return (lc, True)


def call_setup(llvm_config):

    incdir      = _run(llvm_config + ' --includedir')
    libdir      = _run(llvm_config + ' --libdir')
    ldflags     = _run(llvm_config + ' --ldflags')
    libs_core, objs_core = get_libs_and_objs(llvm_config,
        ['core', 'analysis', 'scalaropts', 'executionengine', 
         'jit',  'native', 'interpreter', 'bitreader', 'bitwriter',
         'instrumentation', 'ipa', 'ipo', 'transformutils',
         'asmparser' ])

    std_libs    = [ 'pthread', 'm' ]
    if not sys.platform.startswith("openbsd"):
        std_libs.append("dl")

    ext_core = Extension(
        'llvm._core',
        ['llvm/_core.c', 'llvm/wrap.c', 'llvm/extra.cpp'],
        define_macros = [
            ('__STDC_LIMIT_MACROS', None),
            ('_GNU_SOURCE', None)],
        include_dirs = [incdir],
        library_dirs = [libdir],
        libraries = std_libs + libs_core,
        extra_objects = objs_core,
        extra_link_args = ["-fPIC"])

    setup(
        name='llvm-py',
        version='0.4',
        description='Python Bindings for LLVM',
        author='Mahadevan R',
        author_email='mdevan.foobar@gmail.com',
        url='http://mdevan.nfshost.com/llvm-py/',
        packages=['llvm'],
        py_modules = [ 'llvm.core' ],
        ext_modules = [ ext_core ],)


def main():

    # get llvm config
    llvm_config, is_good = get_llvm_config()
    if is_good:
        print "Using llvm-config=" + llvm_config
    else:
        print "Cannot invoke llvm-config (tried '%s')." % llvm_config
        print "Try again with --llvm-config=/path/to/llvm-config."
        return 1

    # setup
    call_setup(llvm_config)

    # done
    return 0


ev = main()
sys.exit(ev)

