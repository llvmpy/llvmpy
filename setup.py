from __future__ import print_function
import os
import sys
from subprocess import Popen, PIPE, check_call
from distutils.core import setup, Extension

import versioneer


versioneer.versionfile_source = 'llvm/_version.py'
versioneer.versionfile_build = 'llvm/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'llvmpy-'


# On win32, there is a fake llvm-config since llvm doesn't supply one
if sys.platform == 'win32':
    default_llvm_config = 'python llvm-config-win32.py'
else:
    default_llvm_config = 'llvm-config'

llvm_config = os.environ.get('LLVM_CONFIG_PATH', default_llvm_config)


def run_llvm_config(extra_args):
    args = llvm_config.split()
    args.extend(extra_args)
    try:
        p = Popen(args, stdout=PIPE, stderr=PIPE)
    except OSError:
        sys.exit("Error: could not invoke %r\n"
                 "Try setting LLVM_CONFIG_PATH=/path/to/llvm-config" % args)
    stdout, stderr = p.communicate()
    if stderr:
        raise Exception("%r stderr is:\n%s" % (args, stderr.decode()))
    return stdout.decode().strip()

llvm_version = run_llvm_config(['--version'])

print('LLVM version = %r' % llvm_version)

targets_built = run_llvm_config(['--targets-built'])
include_targets = set(os.environ.get('LLVMPY_TARGETS', '').split())
targets_built = ' '.join(set(targets_built.split()) & include_targets)
print('LLVM targets = %s' % targets_built)

def get_libs_and_objs(components):
    parts = run_llvm_config(['--libs'] + components).split()
    libs = []
    objs = []
    for part in parts:
        if part.startswith('-l'):
            libs.append(part[2:])
        elif part.endswith('.o'):
            objs.append(part)
    return libs, objs

def get_enabled_components():
    return run_llvm_config(['--components']).split()

def auto_intrinsic_gen(incdir):
    # let's do auto intrinsic generation
    print("Generate intrinsic IDs")
    from tools import intrgen

    if llvm_version.startswith('3.3') or llvm_version.startswith('3.4'):
        path = "%s/llvm/IR/Intrinsics.gen" % incdir
    else:
        path = "%s/llvm/Intrinsics.gen" % incdir

    with open('llvm/_intrinsic_ids.py', 'w') as fout:
        intrgen.gen(path, fout)


incdir = run_llvm_config(['--includedir'])
libdir = run_llvm_config(['--libdir'])
ldflags = run_llvm_config(['--ldflags'])



auto_intrinsic_gen(incdir)

macros = [('__STDC_CONSTANT_MACROS', None),
          ('__STDC_LIMIT_MACROS', None)]

def determine_to_use_dynlink(libdir, llvm_version):
    user_envvar = os.getenv('LLVMPY_DYNLINK')
    if user_envvar:
        # if users sets LLVMPY_DYNLINK=[0|1]
        # respect the user setting
        print('User sets LLVMPY_DYNLINK to %s' % user_envvar)
        return bool(int(user_envvar))
    else:
        # otherwise, determine by scanning the libdir
        libfile = 'libLLVM-%s' % llvm_version
        print('Searching shared library %s in %s' % (libfile, libdir))
        so = '%s.so' % libfile
        dylib = '%s.dylib' % libfile
        dll = '%s.dll' % libfile
        libdir_content = os.listdir(libdir)
        if sys.platform.startswith('linux'):
            return so in libdir_content
        elif sys.platform.startswith('darwin'):
            return dylib in libdir_content or so in libdir_content
        elif sys.platform.startswith('win32'):
            return dll in libdir_content
        else: # other platforms
            return any((x in libdir_content) for x in [so, dylib, dll])


dynlink = determine_to_use_dynlink(libdir, llvm_version)


if dynlink:
    print('Using dynamic linking')
    libs_core = ['LLVM-%s' % llvm_version]
    objs_core = []
else:
    extra_components = set()
    for tm in map(lambda s: s.lower(), targets_built.split()):
        postfixes = ['', 'asmprinter', 'codegen', 'desc', 'info']
        for postfix in postfixes:
            extra_components.add(tm + postfix)
    enabled_components = set(get_enabled_components())
    extra_components = list(extra_components & enabled_components)

    libs_core, objs_core = get_libs_and_objs(
        ['core', 'analysis', 'scalaropts', 'executionengine', 'mcjit',
         'jit',  'native', 'interpreter', 'bitreader', 'bitwriter',
         'instrumentation', 'ipa', 'ipo', 'transformutils',
         'asmparser', 'linker', 'support', 'vectorize', 'all-targets']
        + extra_components)

if sys.platform == 'win32':
    pass
else:
    macros.append(('_GNU_SOURCE', None))

# auto generate bindings
os.environ['LLVMPY_LLVM_VERSION'] = llvm_version
os.environ['LLVM_TARGETS_BUILT'] = targets_built
check_call([sys.executable, 'llvmpy/build.py'])

# generate shared objects
extra_link_args = ldflags.split()
kwds = dict(
    ext_modules = [
        Extension(
            name='llvmpy._api',
            sources=['llvmpy/api.cpp'],
            define_macros = macros,
            include_dirs = [incdir, 'llvmpy/include'],
            library_dirs = [libdir],
            libraries = libs_core,
            extra_objects = objs_core,
            extra_link_args = extra_link_args),

        Extension(
            name='llvmpy._capsule',
            sources=['llvmpy/capsule.cpp'],
            include_dirs=['llvmpy/include'],
        )
#        Extension(name='llvm._dwarf',
#                  sources=['llvm/_dwarf.cpp'],
#                  include_dirs=[incdir])
        ],
    cmdclass = versioneer.get_cmdclass(),
)


#if sys.version_info[0] == 3:
#    from distutils.command.build_py import build_py_2to3
#    kwds["cmdclass"]['build_py'] = build_py_2to3


kwds['long_description'] = open('README.rst').read()

setup(
    name = 'llvmpy',
    version=versioneer.get_version(),
    description = 'Python bindings for LLVM',
    author = 'R Mahadevan, Siu Kwan Lam',
    maintainer = 'Continuum Analytics, Inc.',
    maintainer_email = 'llvmpy@continuum.io',
    url = 'http://www.llvmpy.org/',
    packages = ['llvm', 'llvm.workaround',
                'llvm.mc',
                'llvm_cbuilder',
                'llpython',
                'llvm_array',
                'llvmpy.api', 'llvmpy.api.llvm',
                'llvm.tests',],
    package_data = {'llvm': ['llrt/*.ll']},
    py_modules = ['llvmpy',
                  'llvmpy._capsule',
                  'llvmpy._api',
                  'llvmpy.capsule',
                  'llvmpy.extra'],
    license = "BSD",
    classifiers = [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: C++",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ],
    **kwds
)
