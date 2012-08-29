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
    print("Cannot invoke llvm-config.")
    print("Try setting LLVM_CONFIG_PATH=/path/to/llvm-config")
    sys.exit(1)


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

if dynlink:
    libs_core = ['LLVM-%d.%d' % llvm_version]
    objs_core = []
else:
    if sys.platform == 'win32':
        # XXX: If found, the PTX components are returned by llvm-config-win32.py,
        #      regardless of whether we ask for them. There should be a better way
        #      eventually.
        print('PTX is included on Win32 at if found by llvm-config-win32.py')
        ptx_components = []
    elif llvm_version <= (3, 1): # select between PTX & NVPTX
        print('Using PTX')
        ptx_components = ['ptx',
                          'ptxasmprinter',
                          'ptxcodegen',
                          'ptxdesc',
                          'ptxinfo']
    else:
        print('Using NVPTX')
        ptx_components = ['nvptx',
                          'nvptxasmprinter',
                          'nvptxcodegen',
                          'nvptxdesc',
                          'nvptxinfo']
    libs_core, objs_core = get_libs_and_objs(
        ['core', 'analysis', 'scalaropts', 'executionengine',
         'jit',  'native', 'interpreter', 'bitreader', 'bitwriter',
         'instrumentation', 'ipa', 'ipo', 'transformutils',
         'asmparser', 'linker', 'support', 'vectorize']
        + ptx_components)

macros = [('__STDC_CONSTANT_MACROS', None),
          ('__STDC_LIMIT_MACROS', None)]
if sys.platform == 'win32':
    # If no PTX lib got added, disable PTX in the build
    if 'LLVMPTXCodeGen' not in libs_core:
        macros.append(('LLVM_DISABLE_PTX', None)),
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

# Read version from llvm/__init__.py
pat = re.compile(r'__version__\s*=\s*(\S+)', re.M)
data = open('llvm/__init__.py').read()
kwds['version'] = eval(pat.search(data).group(1))

setup(
    name = 'llvm-py',
    description = 'Python bindings for LLVM',
    author = 'Mahadevan R',
    author_email = 'mdevan@mdevan.org',
    url = 'http://www.llvmpy.org/',
    packages = ['llvm'],
    py_modules = ['llvm.core'],
    **kwds
)
