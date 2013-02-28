import re
import sys
from distutils.spawn import find_executable
from os.path import abspath, dirname, isfile, join
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
LLVMAnalysis
LLVMAsmParser
LLVMAsmPrinter
LLVMBitReader
LLVMBitWriter
LLVMCodeGen
LLVMCore
LLVMExecutionEngine
LLVMInstCombine
LLVMInstrumentation
LLVMInterpreter
LLVMipa
LLVMipo
LLVMJIT
LLVMLinker
LLVMMC
LLVMMCParser
LLVMObject
LLVMRuntimeDyld
LLVMScalarOpts
LLVMSelectionDAG
LLVMSupport
LLVMTarget
LLVMTransformUtils
LLVMVectorize
LLVMX86AsmParser
LLVMX86AsmPrinter
LLVMX86CodeGen
LLVMX86Desc
LLVMX86Disassembler
LLVMX86Info
LLVMX86Utils
Advapi32
Shell32
""".split():
        print('-l%s' % lib)

    if isfile(join(find_llvm_prefix(), 'lib', 'LLVMPTXCodeGen.lib')):
        print('-lLLVMPTXAsmPrinter')
        print('-lLLVMPTXCodeGen')
        print('-lLLVMPTXDesc')
        print('-lLLVMPTXInfo')

    elif isfile(join(find_llvm_prefix(), 'lib', 'LLVMNVPTXCodeGen.lib')):
        print('-lLLVMNVPTXAsmPrinter')
        print('-lLLVMNVPTXCodeGen')
        print('-lLLVMNVPTXDesc')
        print('-lLLVMNVPTXInfo')


def main():
    try:
        option = sys.argv[1]
    except IndexError:
        sys.exit('Error: option missing')

    if option == '--version':
        print(get_llvm_version())

    elif option == '--libs':
        libs_options()

    elif option == '--includedir':
        incdir = join(find_llvm_prefix(), 'include')
        ensure_file(join(incdir, 'llvm' , 'BasicBlock.h'))
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
