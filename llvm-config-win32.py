import re
import sys
from distutils.spawn import find_executable
from os.path import abspath, dirname, isfile, join
from os import listdir
from subprocess import Popen, PIPE


def find_llvm_tblgen():
    path = find_executable('llvm-tblgen')
    if path is None:
        sys.exit('Error: could not locate llvm-tblgen')
    return path


def find_llvm_prefix():
    return abspath(dirname(dirname(find_llvm_tblgen())))


def ensure_file(path):
    if not isfile(path):
        sys.exit('Error: no file: %r' % path)


def get_llvm_version():
    args = [find_llvm_tblgen(), '--version']
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if stderr:
        sys.exit("Error: %r stderr is:\n%s" % (args, stderr.decode()))
    out = stdout.decode().strip()
    pat = re.compile(r'llvm\s+version\s+(\d+\.\d+\S*)', re.I)
    m = pat.search(out)
    if m is None:
        sys.exit('Error: could not parse version in:' + out)
    return m.group(1)


def libs_options():
    # NOTE: instead of actually looking at the components requested,
    #       we just print out a bunch of libs
    for lib in """
Advapi32
Shell32
""".split():
        print('-l%s' % lib)

    bpath = join(find_llvm_prefix(), 'lib')
    for filename in listdir(bpath):
        filepath = join(bpath, filename)
        if isfile(filepath) and filename.endswith('.lib') and filename.startswith('LLVM'):
            name = filename.split('.', 1)[0]
            print('-l%s' % name)

def main():
    try:
        option = sys.argv[1]
    except IndexError:
        sys.exit('Error: option missing')

    if option == '--version':
        print(get_llvm_version())

    elif option == '--targets-built':
        print('X86')  # just do X86

    elif option == '--libs':
        libs_options()

    elif option == '--includedir':
        incdir = join(find_llvm_prefix(), 'include')
        ensure_file(join(incdir, 'llvm' , 'Linker.h'))
        print(incdir)

    elif option == '--libdir':
        libdir = join(find_llvm_prefix(), 'lib')
        ensure_file(join(libdir, 'LLVMCore.lib'))
        print(libdir)

    elif option in ('--ldflags', '--components'):
        pass

    else:
        sys.exit('Error: Unrecognized llvm-config option %r' % option)


if __name__ == '__main__':
    main()
