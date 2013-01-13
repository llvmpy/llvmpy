import sys
import os
import re
from distutils.core import setup, Extension


# On win32, there is a fake llvm-config since llvm doesn't supply one
if sys.platform == 'win32':
    default_llvm_config = 'python llvm-config-win32.py'
else:
    default_llvm_config = 'llvm-config'

llvm_config = os.environ.get('LLVM_CONFIG_PATH', default_llvm_config)
# set LLVMPY_DYNLINK=1, if you want to link _core.so dynamically to libLLVM.so
dynlink = int(os.environ.get('LLVMPY_DYNLINK', 0))

def run_llvm_config(args):
    cmd = llvm_config + ' ' + ' '.join(args)
    return os.popen(cmd).read().rstrip()

if run_llvm_config(['--version']) == '':
    sys.exit("Cannot invoke llvm-config.\n"
             "Try setting LLVM_CONFIG_PATH=/path/to/llvm-config")


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

def get_llvm_version():
    # get version number; treat it as fixed point
    pat = re.compile(r'(\d+)\.(\d+)')
    m = pat.search(run_llvm_config([' --version']))
    if m is None:
        sys.exit('could not determine llvm version')
    return tuple(map(int, m.groups()))


def auto_intrinsic_gen(incdir):
    # let's do auto intrinsic generation
    print("Generate intrinsic IDs")
    from tools import intrgen
    path = "%s/llvm/Intrinsics.gen" % incdir
    with open('llvm/_intrinsic_ids.py', 'w') as fout:
        intrgen.gen(path, fout)


incdir = run_llvm_config(['--includedir'])
libdir = run_llvm_config(['--libdir'])
ldflags = run_llvm_config(['--ldflags'])

llvm_version = get_llvm_version()
print('LLVM version = %d.%d' % llvm_version)

auto_intrinsic_gen(incdir)

macros = [('__STDC_CONSTANT_MACROS', None),
          ('__STDC_LIMIT_MACROS', None)]
if dynlink:
    libs_core = ['LLVM-%d.%d' % llvm_version]
    objs_core = []
else:
    enabled_components = set(get_enabled_components())
    ptx_components = set(['ptx',
                          'ptxasmprinter',
                          'ptxcodegen',
                          'ptxdesc',
                          'ptxinfo'])
    nvptx_components = set(['nvptx',
                            'nvptxasmprinter',
                            'nvptxcodegen',
                            'nvptxdesc',
                            'nvptxinfo'])

    extra_components = []
    if (nvptx_components & enabled_components) == nvptx_components:
        print("Using NVPTX")
        extra_components.extend(nvptx_components)
    elif (ptx_components & enabled_components) == ptx_components:
        print("Using PTX")
        extra_components.extend(ptx_components)
    else:
        print("No CUDA support")
        macros.append(('LLVM_DISABLE_PTX', None))

    libs_core, objs_core = get_libs_and_objs(
        ['core', 'analysis', 'scalaropts', 'executionengine',
         'jit',  'native', 'interpreter', 'bitreader', 'bitwriter',
         'instrumentation', 'ipa', 'ipo', 'transformutils',
         'asmparser', 'linker', 'support', 'vectorize']
        + extra_components)

if sys.platform == 'win32':
    # If no PTX lib got added, disable PTX in the build
    if 'LLVMPTXCodeGen' not in libs_core:
        macros.append(('LLVM_DISABLE_PTX', None))
else:
    macros.append(('_GNU_SOURCE', None))

extra_link_args = ldflags.split()
kwds = dict(ext_modules = [Extension(
    name='llvm._core',
    sources=['llvm/_core.cpp', 'llvm/wrap.cpp', 'llvm/extra.cpp'],
    define_macros = macros,
    include_dirs = ['/usr/include', incdir],
    library_dirs = [libdir],
    libraries = libs_core,
    extra_objects = objs_core,
    extra_link_args = extra_link_args)])

def run_2to3():
    import lib2to3.refactor
    from distutils.command.build_py import build_py_2to3 as build_py
    print("Installing 2to3 fixers")
    # need to convert sources to Py3 on installation
    fixes = lib2to3.refactor.get_fixers_from_package("lib2to3.fixes")
    #fixes = [fix for fix in fixes
    #          if fix.split('fix_')[-1] not in ('next',)
    #]

    kwds["cmdclass"] = {"build_py": build_py}

if sys.version_info[0] >= 3:
    run_2to3()

# Read version from llvm/__init__.py
pat = re.compile(r'__version__\s*=\s*(\S+)', re.M)
data = open('llvm/__init__.py').read()
kwds['version'] = eval(pat.search(data).group(1))
kwds['long_description'] = open('README.rst').read()

setup(
    name = 'llvmpy',
    description = 'Python bindings for LLVM',
    author = 'R Mahadevan',
    maintainer = 'Continuum Analytics, Inc.',
    maintainer_email = 'llvmpy@continuum.io',
    url = 'http://www.llvmpy.org/',
    packages = ['llvm', 'llvm_cbuilder', 'llpython'],
    py_modules = ['llvm.core'],
    license = "BSD",
    classifiers = [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: C++",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
    **kwds
)
