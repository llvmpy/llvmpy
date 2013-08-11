import sys, os
from distutils.core import setup, Extension

llvm_config = os.environ.get('LLVM_CONFIG_PATH')

def run_llvm_config(args):
    cmd = llvm_config + ' ' + ' '.join(args)
    return os.popen(cmd).read().rstrip()

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

incdir = run_llvm_config(['--includedir'])
libdir = run_llvm_config(['--libdir'])
ldflags = run_llvm_config(['--ldflags'])
macros = [('__STDC_CONSTANT_MACROS', None),
          ('__STDC_LIMIT_MACROS', None)]

extra_link_args = ldflags.split()

components = ['core', 'analysis', 'scalaropts',
              'executionengine', 'jit',  'native',
              'interpreter', 'bitreader',
              'bitwriter', 'instrumentation', 'ipa',
              'ipo', 'transformutils', 'asmparser',
              'linker', 'support', 'vectorize', 'all-targets'
              ]

nvptx = ['nvptx',
         'nvptxasmprinter',
         'nvptxcodegen',
         'nvptxdesc',
         'nvptxinfo']

libs_core, objs_core = get_libs_and_objs(components + nvptx)


ext_modules = [Extension(name='_api',
                         sources=['api.cpp'],
                         include_dirs = ['include', incdir],
                         library_dirs = [libdir],
                         libraries = libs_core,
                         define_macros = macros,
                         extra_objects = objs_core,
                         extra_link_args = extra_link_args),
               Extension(name='_capsule',
                         sources=['capsule.cpp'],
                         include_dirs = ['include'],),
               ]


setup(name = 'llvmpy2',
      description = 'Python bindings for LLVM',
      author = 'Siu Kwan Lam',
      ext_modules = ext_modules,
      license = "BSD")
