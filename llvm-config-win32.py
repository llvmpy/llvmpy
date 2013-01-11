import sys, os

def find_path_of(filename, envvar='PATH'):
    """Finds the path from $PATH where the file exists, returns None if not found."""
    pathlist = os.getenv(envvar).split(os.pathsep)
    for path in pathlist:
        if os.path.exists(os.path.join(path, filename)):
            return os.path.abspath(path)
    return None

if sys.argv[1] == '--version':
    cmd = 'llvm-tblgen --version'
    # Hardcoded extraction, only tested on llvm 3.1
    result = os.popen(cmd).read().split('\n')[1].strip().split(' ')[2]
    print result
elif sys.argv[1] == '--libs':
    # NOTE: instead of actually looking at the components requested,
    #       we just spit out a bunch of libs
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
LLVMX86Info
LLVMX86Utils
Advapi32
Shell32
""".split():
        print('-l%s' % lib)
    llvmbin = find_path_of('llvm-tblgen.exe')
    if os.path.exists(os.path.join(llvmbin, '../lib/LLVMPTXCodeGen.lib')):
        print('-lLLVMPTXAsmPrinter')
        print('-lLLVMPTXCodeGen')
        print('-lLLVMPTXDesc')
        print('-lLLVMPTXInfo')
elif sys.argv[1] == '--includedir': 
    llvmbin = find_path_of('llvm-tblgen.exe')
    if llvmbin is None:
        raise RuntimeError('Could not find LLVM')
    incdir = os.path.abspath(os.path.join(llvmbin, '../include'))
    if not os.path.exists(os.path.join(incdir, 'llvm/BasicBlock.h')):
        raise RuntimeError('Could not find LLVM include dir')
    print incdir
elif sys.argv[1] == '--libdir': 
    llvmbin = find_path_of('llvm-tblgen.exe')
    if llvmbin is None:
        raise RuntimeError('Could not find LLVM')
    libdir = os.path.abspath(os.path.join(llvmbin, '../lib'))
    if not os.path.exists(os.path.join(libdir, 'LLVMCore.lib')):
        raise RuntimeError('Could not find LLVM lib dir')
    print libdir
else:
    raise RuntimeError('Unrecognized llvm-config command %s' % sys.argv[1])
