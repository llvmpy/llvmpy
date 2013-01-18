/*
 * Copyright (c) 2008-10, Mahadevan R All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *  * Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 *  * Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 *  * Neither the name of this software, nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * These are some "extra" functions not available in the standard LLVM-C
 * bindings, but are required / good-to-have inorder to implement the
 * Python bindings.
 */

// standard includes
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <sstream>
#include <cstdio>

// LLVM includes
#include "llvm/LLVMContext.h"
#include "llvm/Bitcode/ReaderWriter.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/Casting.h"
#include "llvm/Constants.h"
#include "llvm/DerivedTypes.h"
#include "llvm/GlobalVariable.h"
//#include "llvm/TypeSymbolTable.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/CallSite.h"
#include "llvm/Support/FormattedStream.h"
#include "llvm/Support/TargetRegistry.h"
#include "llvm/Support/TargetSelect.h"
#include "llvm/Support/Host.h"

#include "llvm/IntrinsicInst.h"
#include "llvm/Analysis/Verifier.h"
#include "llvm/Assembly/Parser.h"
#include "llvm/Support/DynamicLibrary.h"
#include "llvm/PassManager.h"
#include "llvm/ExecutionEngine/ExecutionEngine.h"
#include "llvm/Analysis/LoopPass.h"
#include "llvm/Analysis/Passes.h"
#include "llvm/Analysis/DomPrinter.h"
#include "llvm/Transforms/Scalar.h"
#include "llvm/Transforms/IPO.h"
#include "llvm/Transforms/Utils/UnifyFunctionExitNodes.h"
#include "llvm/Transforms/Instrumentation.h"
#include "llvm/Transforms/Utils/Cloning.h"
#include "llvm/Linker.h"
#include "llvm/Support/SourceMgr.h"
#include <llvm/InlineAsm.h>
#include <llvm/Support/PassNameParser.h>
#include <llvm/Target/TargetLibraryInfo.h>


#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
    #include "llvm/DataLayout.h"
#else
    #include "llvm/Target/TargetData.h"
#endif

// LLVM-C includes
#include "llvm-c/Core.h"
#include "llvm-c/ExecutionEngine.h"

// our includes
#include "extra.h"
#include "llvm_c_extra.h"

namespace llvm{
DEFINE_SIMPLE_CONVERSION_FUNCTIONS(EngineBuilder, LLVMEngineBuilderRef)
DEFINE_SIMPLE_CONVERSION_FUNCTIONS(TargetMachine, LLVMTargetMachineRef)
DEFINE_SIMPLE_CONVERSION_FUNCTIONS(NamedMDNode, LLVMNamedMDRef)
DEFINE_SIMPLE_CONVERSION_FUNCTIONS(Pass, LLVMPassRef)

template<typename T>
inline T **unwrap(LLVMTypeRef *Tys, unsigned Length) {
    (void)Length;
    return reinterpret_cast<T**>(Tys);
}

}

/*
 * For use in LLVMDumpPasses to dump passes.
 */
class PassRegistryPrinter : public llvm::PassRegistrationListener{
public:
    std::ostringstream stringstream;

    inline virtual void passEnumerate(const llvm::PassInfo * pass_info){
        stringstream << pass_info->getPassArgument()
                     << "\t"
                     << pass_info->getPassName()
                     << "\n";
    }
};


/* Helper method for LLVMDumpXXXToString() methods. */
template <typename W, typename UW>
char *do_print(W obj)
{
    std::string s;
    llvm::raw_string_ostream buf(s);
    UW *p = llvm::unwrap(obj);
    assert(p);
    p->print(buf);
    return strdup(buf.str().c_str());
}

namespace {
using namespace llvm;
const CodeGenOpt::Level OptLevelMap[] = {
    CodeGenOpt::None,
    CodeGenOpt::Less,
    CodeGenOpt::Default,
    CodeGenOpt::Aggressive,
};

const CodeModel::Model CodeModelMap[] = {
    CodeModel::Default,
    CodeModel::JITDefault,
    CodeModel::Small,
    CodeModel::Kernel,
    CodeModel::Medium,
    CodeModel::Large,
};


} // end anony namespace

#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
LLVMPassRef LLVMCreateTargetTransformInfo(LLVMTargetMachineRef tmref){
    using namespace llvm;
    TargetMachine * tm = unwrap(tmref);
    Pass * tti = new TargetTransformInfo(tm->getScalarTargetTransformInfo(),
                                         tm->getVectorTargetTransformInfo());
    return wrap(tti);
}
#endif

LLVMPassRef LLVMCreateTargetLibraryInfo(const char * triple){
    using namespace llvm;
    Pass * tli = new TargetLibraryInfo(Triple(triple));
    return wrap(tli);
}

const char * LLVMDefaultTargetTriple(){
    return strdup(llvm::sys::getDefaultTargetTriple().c_str());
}

LLVMPassRef LLVMCreatePassByName(const char *name){
    using namespace llvm;
    const PassInfo * pi = Pass::lookupPassInfo(StringRef(name));
    if (pi) {
        return wrap(pi->createPass());
    } else { // cannot find pass
        return NULL;
    }
}

void LLVMDisposePass(LLVMPassRef passref){
    using namespace llvm;
    delete unwrap(passref);
}

const char * LLVMGetPassName(LLVMPassRef passref){
    using namespace llvm;
    return unwrap(passref)->getPassName();
}

void LLVMPassDump(LLVMPassRef passref){
    using namespace llvm;
    return unwrap(passref)->dump();
}

void LLVMAddPass(LLVMPassManagerRef pmref, LLVMPassRef passref){
    using namespace llvm;
    unwrap(pmref)->add(unwrap(passref));
}

LLVMValueRef LLVMGetFunctionFromInlineAsm(LLVMTypeRef funcType,
                                          const char inlineAsm[],
                                          const char constrains[],
                                          bool hasSideEffect,
                                          bool isAlignStack,
                                          int asmDialect)
{
    using namespace llvm;
    FunctionType *fnty = unwrap<FunctionType>(funcType);
    // asmDialect does not exist for LLVM 3.1
    InlineAsm *inlineasmobj = InlineAsm::get(fnty, inlineAsm, constrains,
                                             hasSideEffect, isAlignStack);
    return wrap(inlineasmobj);
}

LLVMModuleRef LLVMCloneModule(LLVMModuleRef mod)
{
    using namespace llvm;
    return wrap(CloneModule(unwrap(mod)));
}

const char * LLVMDumpNamedMDToString(LLVMNamedMDRef nmd)
{
    using namespace llvm;
    std::string s;
    llvm::raw_string_ostream buf(s);
    unwrap(nmd)->print(buf, NULL);
    return strdup(buf.str().c_str());
}

const char * LLVMNamedMetaDataGetName(LLVMNamedMDRef nmd)
{
    using namespace llvm;
    return unwrap(nmd)->getName().data();
}

void LLVMNamedMetaDataAddOperand(LLVMNamedMDRef nmd, LLVMValueRef md)
{
    using namespace llvm;
    unwrap(nmd)->addOperand(unwrap<MDNode>(md));
}

void LLVMEraseNamedMetaData(LLVMNamedMDRef nmd)
{
    using namespace llvm;
    unwrap(nmd)->eraseFromParent();
}

LLVMNamedMDRef LLVMModuleGetOrInsertNamedMetaData(LLVMModuleRef mod, const char *name)
{
    using namespace llvm;
    return wrap(unwrap(mod)->getOrInsertNamedMetadata(name));
}

LLVMNamedMDRef LLVMModuleGetNamedMetaData(LLVMModuleRef mod, const char *name)
{
    using namespace llvm;
    return wrap(unwrap(mod)->getNamedMetadata(name));
}

void LLVMInstSetMetaData(LLVMValueRef instref, const char* mdkind,
                         LLVMValueRef metaref)
{
    using namespace llvm;
    unwrap<Instruction>(instref)->setMetadata(mdkind, unwrap<MDNode>(metaref));
}

LLVMValueRef LLVMMetaDataGet(LLVMModuleRef modref, LLVMValueRef * valrefs,
                             unsigned valct)
{
    using namespace llvm;
    LLVMContext & context = unwrap(modref)->getContext();
    MDNode * const node = MDNode::get(
                            context,
                            makeArrayRef(unwrap<Value>(valrefs, valct), valct));
    return wrap(node);
}

LLVMValueRef LLVMMetaDataGetOperand(LLVMValueRef mdref, unsigned index)
{
    return wrap(llvm::unwrap<llvm::MDNode>(mdref)->getOperand(index));
}

unsigned LLVMMetaDataGetNumOperands(LLVMValueRef mdref)
{
    return llvm::unwrap<llvm::MDNode>(mdref)->getNumOperands();
}

LLVMValueRef LLVMMetaDataStringGet(LLVMModuleRef modref, const char *s)
{
    LLVMContext & context = unwrap(modref)->getContext();
    MDString * const mdstring = MDString::get(context, s);
    return wrap(mdstring);
}

const char *LLVMGetConstExprOpcodeName(LLVMValueRef inst)
{
    return llvm::unwrap<llvm::ConstantExpr>(inst)->getOpcodeName();
}

unsigned LLVMGetConstExprOpcode(LLVMValueRef inst)
{
    return llvm::unwrap<llvm::ConstantExpr>(inst)->getOpcode();
}

void LLVMLdSetAlignment(LLVMValueRef inst, unsigned align)
{
    return llvm::unwrap<LoadInst>(inst)->setAlignment(align);
}

void LLVMStSetAlignment(LLVMValueRef inst, unsigned align)
{
    return llvm::unwrap<StoreInst>(inst)->setAlignment(align);
}

const char * LLVMGetHostCPUName()
{
    return strdup(llvm::sys::getHostCPUName().c_str());
}

const char * LLVMGetHostCPUFeatures()
{
    // placeholder
    // TODO not implemented even in LLVM3.2svn
    // llvm::sys::getHostCPUFeatures
    return NULL;
}

int LLVMInitializeNativeTargetAsmPrinter()
{
    return llvm::InitializeNativeTargetAsmPrinter();
}


LLVMTargetMachineRef LLVMTargetMachineLookup(const char *arch, const char *cpu,
                                             const char *features, int opt,
                                             int codemodel,
                                             std::string &error)
{
    using namespace llvm;
    Triple TheTriple;

    // begin borrow from LLVM 3.2 code
    // because we don't have 3 argument version of lookup() in 3.1
    const Target * TheTarget = NULL;

    const std::string ArchName(arch);
    for (TargetRegistry::iterator it = TargetRegistry::begin(),
        ie = TargetRegistry::end(); it != ie; ++it) {
        if (ArchName == it->getName()) {
            TheTarget = &*it;
            break;
        }
    }

    if (!TheTarget) {
        error = "Unknown arch";
        return NULL;
    }

    Triple::ArchType Type = Triple::getArchTypeForLLVMName(ArchName);

    if (Type != Triple::UnknownArch){
        TheTriple.setArch(Type);
    }
    // end borrow from LLVM 3.2 code

    if (!TheTarget->hasTargetMachine()){
        error = "No target machine for the arch";
        return NULL;
    }

    TargetOptions no_target_options;
    TargetMachine * tm = TheTarget->createTargetMachine(TheTriple.str(), cpu,
                                                        features,
                                                        no_target_options,
                                                        Reloc::Default,
                                                        CodeModelMap[codemodel],
                                                        OptLevelMap[opt]);

    if (!tm){
        error = "Cannot create target machine";
        return NULL;
    }
    return wrap(tm);
}

LLVMTargetMachineRef LLVMCreateTargetMachine(const char *triple,
                                             const char *cpu,
                                             const char *features,
                                             int opt,
                                             int codemodel,
                                             std::string &error)
{
    using namespace llvm;

    std::string TheTriple = triple;
    const Target * TheTarget = TargetRegistry::lookupTarget(TheTriple, error);
    if (!TheTarget) return NULL;

    TargetOptions no_target_options;
    TargetMachine * tm = TheTarget->createTargetMachine(TheTriple, cpu, features,
                                                        no_target_options,
                                                        Reloc::Default,
                                                        CodeModelMap[codemodel],
                                                        OptLevelMap[opt]);
    if (!tm) {
        error = "Cannot create target machine";
        return NULL;
    }
    return wrap(tm);
}

LLVMTargetMachineRef LLVMTargetMachineFromEngineBuilder(LLVMEngineBuilderRef eb)
{
    using namespace llvm;
    TargetMachine * tm = unwrap(eb)->selectTarget();
    return wrap(tm);
}

void LLVMDisposeTargetMachine(LLVMTargetMachineRef tm){
    delete llvm::unwrap(tm);
}


unsigned char* LLVMTargetMachineEmitFile(LLVMTargetMachineRef tmref,
                                         LLVMModuleRef modref,
                                         int assembly, size_t * lenp,
                                         std::string &error)
{
    using namespace llvm;
    assert(lenp);

    Module *modulep = unwrap(modref);
    assert(modulep);

    // get objectcode into a string
    std::string s;
    raw_string_ostream buf(s);

    formatted_raw_ostream fso(buf);

    TargetMachine * tm = unwrap(tmref);

    PassManager pm;
#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
    if (!tm->getDataLayout()){
        error = "No target data in target machine";
        return NULL;
    }
    pm.add(new DataLayout(*tm->getDataLayout()));
#else
    if (!tm->getTargetData()){
        error = "No target data in target machine";
        return NULL;
    }
    pm.add(new TargetData(*tm->getTargetData()));
#endif



    bool failed;
    if( assembly ) {
        failed = tm->addPassesToEmitFile(pm, fso, TargetMachine::CGFT_AssemblyFile);
    } else {
        failed = tm->addPassesToEmitFile(pm, fso, TargetMachine::CGFT_ObjectFile);
    }

    if ( failed ) {
        error = "No support for emit file";
        return NULL;
    }

    pm.run(*modulep);

    // flush all streams
    fso.flush();
    buf.flush();

    const std::string& bc = buf.str();

    // and then into a new buffer
    size_t bclen = bc.size();
    unsigned char *bytes = new unsigned char[bclen];
    memcpy(bytes, bc.data(), bclen);

    /* return */
    *lenp = bclen;
    return bytes;
}

const char* LLVMTargetMachineGetTargetName(LLVMTargetMachineRef tm)
{
    return strdup(llvm::unwrap(tm)->getTarget().getName());
}

const char* LLVMTargetMachineGetTargetShortDescription(LLVMTargetMachineRef tm)
{
    return strdup(llvm::unwrap(tm)->getTarget().getShortDescription());
}

const char* LLVMTargetMachineGetTriple(LLVMTargetMachineRef tm)
{
    return strdup(llvm::unwrap(tm)->getTargetTriple().str().c_str());
}

const char* LLVMTargetMachineGetCPU(LLVMTargetMachineRef tm)
{
    return strdup(llvm::unwrap(tm)->getTargetCPU().str().c_str());
}

const char* LLVMTargetMachineGetFS(LLVMTargetMachineRef tm)
{
    return strdup(llvm::unwrap(tm)->getTargetFeatureString().str().c_str());
}

void LLVMPrintRegisteredTargetsForVersion(){
    llvm::TargetRegistry::printRegisteredTargetsForVersion();
}



LLVMTargetDataRef LLVMTargetMachineGetTargetData(LLVMTargetMachineRef tm)
{
    using namespace llvm;
#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
    return wrap(new DataLayout(*unwrap(tm)->getDataLayout()));
#else
    return wrap(new TargetData(*unwrap(tm)->getTargetData()));
#endif
}

unsigned char* LLVMGetNativeCodeFromModule(LLVMModuleRef module, int assembly,
                                           size_t * lenp, std::string &error)
{
    using namespace llvm;
    assert(lenp);

    Module *modulep = unwrap(module);
    assert(modulep);

    // select native default machine
    TargetMachine * tm = EngineBuilder(modulep).selectTarget();

    return LLVMTargetMachineEmitFile(wrap(tm), module, assembly, lenp, error);
}

static
llvm::AtomicOrdering atomic_ordering_from_string(const char * ordering)
{
    using namespace llvm;

    if ( strcmp(ordering, "unordered") == 0 )
        return Unordered;
    else if ( strcmp(ordering, "monotonic") == 0 )
        return Monotonic;
    else if ( strcmp(ordering, "acquire") == 0 )
        return Acquire;
    else if ( strcmp(ordering, "release") == 0 )
        return Release;
    else if ( strcmp(ordering, "acq_rel") == 0 )
        return AcquireRelease;
    else if ( strcmp(ordering, "seq_cst") == 0 )
        return SequentiallyConsistent;
    else
        return NotAtomic;
}

static
llvm::SynchronizationScope sync_scope_from_int(int crossthread)
{
    if( crossthread )
        return llvm::CrossThread;
    else
        return llvm::SingleThread;
}

LLVMValueRef LLVMBuildFence(LLVMBuilderRef builder, const char* ordering,
                            int crossthread)
{
    using namespace llvm;
    AtomicOrdering atomic_order = atomic_ordering_from_string(ordering);
    SynchronizationScope sync_scope = sync_scope_from_int(crossthread);

    Value * inst = unwrap(builder)->CreateFence(atomic_order, sync_scope);
    return wrap(inst);
}

LLVMValueRef LLVMBuildAtomicRMW(LLVMBuilderRef builder, const char * opname,
                                LLVMValueRef ptr, LLVMValueRef val,
                                const char* ordering, int crossthread)
{
    using namespace llvm;

    AtomicRMWInst::BinOp op;

    if( strcmp(opname, "xchg") == 0 )
        op = AtomicRMWInst::Xchg;
    else if( strcmp(opname, "add") == 0 )
        op = AtomicRMWInst::Add;
    else if( strcmp(opname, "sub") == 0 )
        op = AtomicRMWInst::Sub;
    else if( strcmp(opname, "and") == 0 )
        op = AtomicRMWInst::And;
    else if( strcmp(opname, "nand") == 0 )
        op = AtomicRMWInst::Nand;
    else if( strcmp(opname, "or") == 0 )
        op = AtomicRMWInst::Or;
    else if( strcmp(opname, "xor") == 0 )
        op = AtomicRMWInst::Xor;
    else if( strcmp(opname, "max") == 0 )
        op = AtomicRMWInst::Max;
    else if( strcmp(opname, "min") == 0 )
        op = AtomicRMWInst::Min;
    else if( strcmp(opname, "umax") == 0 )
        op = AtomicRMWInst::UMax;
    else if( strcmp(opname, "umin") == 0 )
        op = AtomicRMWInst::UMin;
    else
        op = AtomicRMWInst::BAD_BINOP;

    AtomicOrdering atomic_order = atomic_ordering_from_string(ordering);
    SynchronizationScope sync_scope = sync_scope_from_int(crossthread);

    Value * inst = unwrap(builder)->CreateAtomicRMW(op, unwrap(ptr), unwrap(val),
                                                    atomic_order, sync_scope);
    return wrap(inst);
}

LLVMValueRef LLVMBuildAtomicLoad(LLVMBuilderRef builder, LLVMValueRef ptr,
                                 unsigned align, const char* ordering,
                                 int crossthread)
{
    using namespace llvm;
    AtomicOrdering atomic_order = atomic_ordering_from_string(ordering);
    SynchronizationScope sync_scope = sync_scope_from_int(crossthread);

    LoadInst * inst = unwrap(builder)->CreateLoad(unwrap(ptr));

    inst->setAtomic(atomic_order, sync_scope);
    inst->setAlignment(align);

    return wrap(inst);
}

LLVMValueRef LLVMBuildAtomicStore(LLVMBuilderRef builder,
                                  LLVMValueRef ptr, LLVMValueRef val,
                                  unsigned align, const char* ordering,
                                  int crossthread)
{
    using namespace llvm;
    AtomicOrdering atomic_order = atomic_ordering_from_string(ordering);
    SynchronizationScope sync_scope = sync_scope_from_int(crossthread);

    StoreInst * inst = unwrap(builder)->CreateStore(unwrap(val), unwrap(ptr));

    inst->setAtomic(atomic_order, sync_scope);
    inst->setAlignment(align);

    return wrap(inst);
}

LLVMValueRef LLVMBuildAtomicCmpXchg(LLVMBuilderRef builder, LLVMValueRef ptr,
                               LLVMValueRef cmp, LLVMValueRef val,
                               const char* ordering, int crossthread)
{
    using namespace llvm;

    AtomicOrdering atomic_order = atomic_ordering_from_string(ordering);
    SynchronizationScope sync_scope = sync_scope_from_int(crossthread);

    Value * inst = unwrap(builder)->CreateAtomicCmpXchg(
                                        unwrap(ptr), unwrap(cmp), unwrap(val),
                                        atomic_order, sync_scope);
    return wrap(inst);
}

LLVMEngineBuilderRef LLVMCreateEngineBuilder(LLVMModuleRef mod)
{
    return llvm::wrap(new EngineBuilder(unwrap(mod)));
}

void LLVMDisposeEngineBuilder(LLVMEngineBuilderRef eb)
{
    delete llvm::unwrap(eb);
}

void LLVMEngineBuilderForceJIT(LLVMEngineBuilderRef eb)
{
    using namespace llvm;
    unwrap(eb)->setEngineKind(EngineKind::JIT);
}

void LLVMEngineBuilderForceInterpreter(LLVMEngineBuilderRef eb)
{
    using namespace llvm;
    unwrap(eb)->setEngineKind(EngineKind::Interpreter);
}

void LLVMEngineBuilderSetOptLevel(LLVMEngineBuilderRef eb, int level)
{
    unwrap(eb)->setOptLevel(OptLevelMap[level]);
}

void LLVMEngineBuilderSetMCPU(LLVMEngineBuilderRef eb, const char * mcpu)
{   // TODO add test when llvm3.2 releases
    unwrap(eb)->setMCPU(mcpu); // does not work in llvm3.1
}

void LLVMEngineBuilderSetMAttrs(LLVMEngineBuilderRef eb, const char * mattrs)
{   // TODO add test when llvm3.2 releases
    std::vector<std::string> tokenized;
    std::istringstream iss(mattrs);
    std::string buf;
    while ( iss >> buf ){
        tokenized.push_back(buf);
    }
    unwrap(eb)->setMAttrs(tokenized); // does not work in llvm3.1
}

LLVMExecutionEngineRef LLVMEngineBuilderCreate(LLVMEngineBuilderRef eb, std::string & error)
{
    using namespace llvm;
    LLVMExecutionEngineRef ret;

    ret = wrap(unwrap(eb)->setErrorStr(&error).create());

    if ( !error.empty() ) { // error string is set
        return NULL;
    } else {
        return ret;
    }
}

LLVMExecutionEngineRef LLVMEngineBuilderCreateTM(LLVMEngineBuilderRef eb,
                                                 LLVMTargetMachineRef tm,
                                                 std::string & error)
{
    using namespace llvm;
    LLVMExecutionEngineRef ret;

    ret = wrap(unwrap(eb)->setErrorStr(&error).create(unwrap(tm)));

    if ( !error.empty() ) { // error string is set
        return NULL;
    } else {
        return ret;
    }
}

int LLVMPassManagerBuilderGetOptLevel(LLVMPassManagerBuilderRef pmb)
{
    return llvm::unwrap(pmb)->OptLevel;
}

int LLVMPassManagerBuilderGetSizeLevel(LLVMPassManagerBuilderRef pmb)
{
    return llvm::unwrap(pmb)->SizeLevel;
}

void LLVMPassManagerBuilderSetVectorize(LLVMPassManagerBuilderRef pmb, int flag)
{
    llvm::unwrap(pmb)->Vectorize = flag;
}

int LLVMPassManagerBuilderGetVectorize(LLVMPassManagerBuilderRef pmb){
    return llvm::unwrap(pmb)->Vectorize;
}

#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
void LLVMPassManagerBuilderSetLoopVectorize(LLVMPassManagerBuilderRef pmb,
                                            int flag)
{
    llvm::unwrap(pmb)->LoopVectorize = flag;
}

int LLVMPassManagerBuilderGetLoopVectorize(LLVMPassManagerBuilderRef pmb){
    return llvm::unwrap(pmb)->LoopVectorize;
}
#endif // llvm-3.2


int LLVMPassManagerBuilderGetDisableUnitAtATime(LLVMPassManagerBuilderRef pmb)
{
    return llvm::unwrap(pmb)->DisableUnitAtATime;
}

int LLVMPassManagerBuilderGetDisableUnrollLoops(LLVMPassManagerBuilderRef pmb)
{
    return llvm::unwrap(pmb)->DisableUnrollLoops;
}

int LLVMPassManagerBuilderGetDisableSimplifyLibCalls(LLVMPassManagerBuilderRef pmb)
{
    return llvm::unwrap(pmb)->DisableSimplifyLibCalls;
}


int LLVMAddPassByName(LLVMPassManagerRef pm, const char * name)
{
    using namespace llvm;
    const PassInfo * pi = Pass::lookupPassInfo(StringRef(name));
    if (pi){
        unwrap(pm)->add(pi->createPass());
        return 1;  // success
    } else {
        return 0;  // fail -- cannot find pass
    }
}

void LLVMInitializePasses(){
    using namespace llvm;
    PassRegistry &registry = *PassRegistry::getPassRegistry();
    initializeCore(registry);
    initializeScalarOpts(registry);
    initializeVectorization(registry);
    initializeIPO(registry);
    initializeAnalysis(registry);
    initializeIPA(registry);
    initializeTransformUtils(registry);
    initializeInstCombine(registry);
    initializeInstrumentation(registry);
    initializeTarget(registry);
}

const char * LLVMDumpPasses()
{
    using namespace llvm;
    PassRegistry &registry = *PassRegistry::getPassRegistry();
    PassRegistryPrinter prp;
    registry.enumerateWith(&prp);
    return strdup(prp.stringstream.str().c_str());
}


int LLVMIsLiteralStruct(LLVMTypeRef type)
{
    return llvm::unwrap<llvm::StructType>(type)->isLiteral();
}

LLVMTypeRef LLVMStructTypeIdentified(const char * name)
{
    using namespace llvm;
    return wrap(StructType::create(getGlobalContext(), name));
}

void LLVMSetStructBody(LLVMTypeRef type, LLVMTypeRef* elemtys,
                       unsigned elemct, int is_packed)
{
    using namespace llvm;
    ArrayRef<Type*> elemtys_aryref(unwrap(elemtys), elemct);
    unwrap<StructType>(type)->setBody(elemtys_aryref, is_packed);
}

void LLVMSetStructName(LLVMTypeRef type, const char * name)
{
    llvm::StructType *st = llvm::unwrap<llvm::StructType>(type);
    st->setName(name);
}

char *LLVMGetModuleIdentifier(LLVMModuleRef module)
{
    return strdup(llvm::unwrap(module)->getModuleIdentifier().c_str());
}

void LLVMSetModuleIdentifier(LLVMModuleRef module, const char * name)
{
    llvm::unwrap(module)->setModuleIdentifier(name);
}

char *LLVMDumpModuleToString(LLVMModuleRef module)
{
    std::string s;
    llvm::raw_string_ostream buf(s);
    llvm::Module *p = llvm::unwrap(module);
    assert(p);
    p->print(buf, NULL);
    return strdup(buf.str().c_str());
}

void LLVMModuleAddLibrary(LLVMModuleRef module, const char *name)
{
    llvm::Module *M = llvm::unwrap(module);
    llvm::StringRef namestr = llvm::StringRef(name);
    M->addLibrary(namestr);
    return;
}

char *LLVMDumpTypeToString(LLVMTypeRef type)
{
    return do_print<LLVMTypeRef, llvm::Type>(type);
}

char *LLVMDumpValueToString(LLVMValueRef value)
{
    return do_print<LLVMValueRef, llvm::Value>(value);
}

unsigned LLVMModuleGetPointerSize(LLVMModuleRef module)
{
    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    llvm::Module::PointerSize p = modulep->getPointerSize();
    if (p == llvm::Module::Pointer32)
        return 32;
    else if (p == llvm::Module::Pointer64)
        return 64;
    return 0;
}

LLVMValueRef LLVMModuleGetOrInsertFunction(LLVMModuleRef module,
    const char *name, LLVMTypeRef function_type)
{
    assert(name);

    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    llvm::FunctionType *ftp = llvm::unwrap<llvm::FunctionType>(function_type);
    assert(ftp);

    llvm::Constant *f = modulep->getOrInsertFunction(name, ftp);
    return wrap(f);
}

int LLVMHasInitializer(LLVMValueRef global_var)
{
    llvm::GlobalVariable *gvp = llvm::unwrap<llvm::GlobalVariable>(global_var);
    assert(gvp);

    return gvp->hasInitializer();
}

#define inst_checkfn(ourfn, llvmfn)                 \
unsigned ourfn (LLVMValueRef v) {                   \
    llvm::Instruction *ip = llvm::unwrap<llvm::Instruction>(v); \
    assert(ip);                                     \
    return ip-> llvmfn () ? 1 : 0;                  \
}

inst_checkfn(LLVMInstIsTerminator,      isTerminator)
inst_checkfn(LLVMInstIsBinaryOp,        isBinaryOp)
inst_checkfn(LLVMInstIsShift,           isShift)
inst_checkfn(LLVMInstIsCast,            isCast)
inst_checkfn(LLVMInstIsLogicalShift,    isLogicalShift)
inst_checkfn(LLVMInstIsArithmeticShift, isArithmeticShift)
inst_checkfn(LLVMInstIsAssociative,     isAssociative)
inst_checkfn(LLVMInstIsCommutative,     isCommutative)

unsigned LLVMInstIsVolatile(LLVMValueRef v)
{
    using namespace llvm;
    Instruction *ip = unwrap<Instruction>(v);
    assert(ip);
    return ((isa<LoadInst>(*ip)  && cast<LoadInst>(*ip).isVolatile()) ||
            (isa<StoreInst>(*ip) && cast<StoreInst>(*ip).isVolatile()) );
}

const char *LLVMInstGetOpcodeName(LLVMValueRef inst)
{
    llvm::Instruction *instp = llvm::unwrap<llvm::Instruction>(inst);
    assert(instp);
    return instp->getOpcodeName();
}

unsigned LLVMInstGetOpcode(LLVMValueRef inst)
{
    llvm::Instruction *instp = llvm::unwrap<llvm::Instruction>(inst);
    assert(instp);
    return instp->getOpcode();
}

unsigned LLVMCmpInstGetPredicate(LLVMValueRef cmpinst)
{
    llvm::CmpInst *instp = llvm::unwrap<llvm::CmpInst>(cmpinst);
    assert(instp);
    return instp->getPredicate();
}

LLVMValueRef LLVMInstGetCalledFunction(LLVMValueRef inst)
{
    llvm::Instruction *instp = llvm::unwrap<llvm::Instruction>(inst);
    return llvm::wrap(CallSite(instp).getCalledFunction());
}

void LLVMInstSetCalledFunction(LLVMValueRef inst, LLVMValueRef fn)
{
    using namespace llvm;
    Instruction *instp = unwrap<Instruction>(inst);
    CallSite(instp).setCalledFunction(unwrap(fn));
}

///* llvm::unwrap a set of `n' wrapped objects starting at `values',
// * into a vector of pointers to llvm::unwrapped objects `out'. */
//template <typename W, typename UW>
//void unwrap_vec(W *values, unsigned n, std::vector<UW *>& out)
//{
//    out.clear();
//    out.reserve(n);
//    while (n--) {
//        UW *p = llvm::unwrap(*values);
//        assert(p);
//        out.push_back(p);
//        ++values;
//    }
//}

///* Same as llvm::unwrap_vec, but use a vector of const pointers. */
//template <typename W, typename UW>
//void unwrap_cvec(W *values, unsigned n, std::vector<const UW *>& out)
//{
//    out.clear();

//    while (n--) {
//        UW *p = llvm::unwrap(*values);
//        assert(p);
//        out.push_back(p);
//        ++values;
//    }
//}


LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef builder,
    LLVMValueRef *values, unsigned n_values)
{
    using namespace llvm;
    assert(values);

    IRBuilder<> *builderp = unwrap(builder);
    assert(builderp);

    return wrap(builderp->CreateAggregateRet(unwrap<Value>(values, n_values), n_values));
}

LLVMValueRef LLVMBuildGetResult(LLVMBuilderRef builder,
    LLVMValueRef value, unsigned index, const char *name)
{
    assert(name);

    llvm::IRBuilder<> *builderp = llvm::unwrap(builder);
    assert(builderp);

    return llvm::wrap(builderp->CreateExtractValue(llvm::unwrap(value), index, name));
}

unsigned LLVMValueGetID(LLVMValueRef value)
{
    llvm::Value *valuep = llvm::unwrap(value);
    assert(valuep);

    return valuep->getValueID();
}


unsigned LLVMValueGetNumUses(LLVMValueRef value)
{
    llvm::Value *valuep = llvm::unwrap(value);
    assert(valuep);

    return valuep->getNumUses();
}


unsigned LLVMValueGetUses(LLVMValueRef value, LLVMValueRef **refs)
{
    llvm::Value *valuep = llvm::unwrap(value);
    assert(valuep);

    unsigned n = valuep->getNumUses();
    if (n == 0)
        return 0;

    assert(refs);
    LLVMValueRef *out = new LLVMValueRef[n];
    if (!out)
        return 0;
    *refs = out;

    memset(out, 0, sizeof(LLVMValueRef) * n);
    llvm::Value::use_iterator it = valuep->use_begin();
    while (it != valuep->use_end()) {
        *out++ = llvm::wrap(*it);
        ++it;
    }

    return n;
}

void LLVMDisposeValueRefArray(LLVMValueRef *refs)
{
    assert(refs);
    delete [] refs;
}

unsigned LLVMUserGetNumOperands(LLVMValueRef user)
{
    llvm::User *userp = llvm::unwrap<llvm::User>(user);
    assert(userp);
    return userp->getNumOperands();
}

LLVMValueRef LLVMUserGetOperand(LLVMValueRef user, unsigned idx)
{
    llvm::User *userp = llvm::unwrap<llvm::User>(user);
    assert(userp);
    llvm::Value *operand = userp->getOperand(idx);
    return llvm::wrap(operand);
}

unsigned LLVMGetDoesNotThrow(LLVMValueRef fn)
{
    llvm::Function *fnp = llvm::unwrap<llvm::Function>(fn);
    assert(fnp);

    return fnp->doesNotThrow();
}

void LLVMSetDoesNotThrow(LLVMValueRef fn, int DoesNotThrow)
{
    llvm::Function *fnp = llvm::unwrap<llvm::Function>(fn);
    assert(fnp);

    if ((bool)DoesNotThrow)
    	fnp->setDoesNotThrow();
}


LLVMValueRef LLVMGetIntrinsic(LLVMModuleRef module, int id,
    LLVMTypeRef *types, unsigned n_types)
{
    using namespace llvm;
    assert(types);

    Module *modulep = unwrap(module);
    assert(modulep);

    Function *intfunc = Intrinsic::getDeclaration(modulep, Intrinsic::ID(id),
                                    makeArrayRef(unwrap<Type>(types, n_types),
                                                 n_types));

    return wrap(intfunc);
}

LLVMModuleRef LLVMGetModuleFromAssembly(const char *asmtext, char **out)
{
    assert(asmtext);
    assert(out);

    llvm::Module *modulep;
    llvm::SMDiagnostic error;
    if (!(modulep = llvm::ParseAssemblyString(asmtext, NULL, error,
                                              llvm::getGlobalContext()))) {
        std::string s;
        llvm::raw_string_ostream buf(s);
        error.print("llvm-py", buf);
        *out = strdup(buf.str().c_str());
        return NULL;
    }

    return wrap(modulep);
}

LLVMModuleRef LLVMGetModuleFromBitcode(const char *bitcode, unsigned bclen,
    char **out)
{
    assert(bitcode);
    assert(out);

    llvm::StringRef as_str(bitcode, bclen);

    llvm::MemoryBuffer *mbp;
    if (!(mbp = llvm::MemoryBuffer::getMemBufferCopy(as_str)))
        return NULL;

    std::string msg;
    llvm::Module *modulep;
    if (!(modulep = llvm::ParseBitcodeFile(mbp, llvm::getGlobalContext(),
                                           &msg)))
        *out = strdup(msg.c_str());

    delete mbp;
    return wrap(modulep);
}

#if LLVM_VERSION_MAJOR <= 3 && LLVM_VERSION_MINOR < 2
// Shamelessly copy from LLVM-3.2
unsigned LLVMLinkModules(LLVMModuleRef Dest, LLVMModuleRef Src,
                         int Mode, char **OutMessages) {
    std::string Messages;
    unsigned Result = Linker::LinkModules(unwrap(Dest), unwrap(Src), Mode,
                                          OutMessages? &Messages : 0);
    if (OutMessages)
            *OutMessages = strdup(Messages.c_str());
    return Result;
}
#endif

unsigned char *LLVMGetBitcodeFromModule(LLVMModuleRef module, size_t *lenp)
{
    assert(lenp);

    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    /* get bc into a string */
    std::string s;
    llvm::raw_string_ostream buf(s);
    llvm::WriteBitcodeToFile(modulep, buf);
    const std::string& bc = buf.str();

    /* and then into a new()-ed block */
    size_t bclen = bc.size();
    unsigned char *bytes = new unsigned char[bclen];
    memcpy(bytes, bc.data(), bclen);

    /* return */
    *lenp = bclen;
    return bytes;
}

/* Return 0 on failure (with errmsg filled in), 1 on success. */
unsigned LLVMLoadLibraryPermanently(const char* filename, char **errmsg)
{
    printf("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@1");
    assert(filename);
    printf("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2");
    assert(errmsg);
    printf("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@3");

    /* Note: the LLVM API returns true on failure. Don't ask why. */
    std::string msg;
    printf("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@4");
    if (llvm::sys::DynamicLibrary::LoadLibraryPermanently(filename, &msg)) {
        printf("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@5");
        *errmsg = strdup(msg.c_str());
        printf("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@6");
        return 0;
    }
    printf("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@7");
    return 1;
}

void LLVMExecutionEngineDisableLazyCompilation(LLVMExecutionEngineRef ee, int flag)
{
    llvm::unwrap(ee)->DisableLazyCompilation(flag);
}

void *LLVMGetPointerToFunction(LLVMExecutionEngineRef ee, LLVMValueRef fn)
{
    llvm::ExecutionEngine *eep = llvm::unwrap(ee);
    assert(eep);

    llvm::Function *fnp = llvm::unwrap<llvm::Function>(fn);
    assert(fnp);

    return eep->getPointerToFunction(fnp);
}


int LLVMInlineFunction(LLVMValueRef call)
{
    llvm::Value *callp = llvm::unwrap(call);
    assert(callp);

    llvm::InlineFunctionInfo unused;

    llvm::Instruction *II = llvm::dyn_cast<llvm::Instruction>(callp);
    if (II->getOpcode() == llvm::Instruction::Call)
        return llvm::InlineFunction(static_cast<llvm::CallInst*>(II), unused);
    else if (II->getOpcode() == llvm::Instruction::Invoke)
        return llvm::InlineFunction(static_cast<llvm::InvokeInst*>(II), unused);
    else
        return 0;
}

unsigned LLVMGetParamAlignment(LLVMValueRef arg)
{
    llvm::Argument *argp = llvm::unwrap<llvm::Argument>(arg);
    assert(argp);

    unsigned argno = argp->getArgNo();

    return argp->getParent()->getParamAlignment(argno + 1);
}


/* Passes. A few passes (listed below) are used directly from LLVM-C,
 * rest are defined here.
 */
/*
#define define_pass(P)                                   \
void LLVMAdd ## P ## Pass (LLVMPassManagerRef passmgr) { \
    using namespace llvm;                                \
    llvm::PassManagerBase *pmp = llvm::unwrap(passmgr);  \
    assert(pmp);                                         \
    pmp->add( create ## P ## Pass ());                   \
}

define_pass( AAEval )
define_pass( AliasAnalysisCounter )
//define_pass( AlwaysInliner )
//define_pass( BasicAliasAnalysis )
define_pass( BlockPlacement )
define_pass( BreakCriticalEdges )
define_pass( CodeGenPrepare )
define_pass( DbgInfoPrinter )
define_pass( DeadCodeElimination )
define_pass( DeadInstElimination )
define_pass( DemoteRegisterToMemory )
define_pass( DomOnlyPrinter )
define_pass( DomOnlyViewer )
define_pass( DomPrinter )
define_pass( DomViewer )
define_pass( EdgeProfiler )
//define_pass( GEPSplitter )
define_pass( GlobalsModRef )
define_pass( InstCount )
define_pass( InstructionNamer )
define_pass( LazyValueInfo )
define_pass( LCSSA )
//define_pass( LiveValues )
define_pass( LoopDependenceAnalysis )
define_pass( LoopExtractor )
define_pass( LoopSimplify )
define_pass( LoopStrengthReduce )
define_pass( LowerInvoke )
define_pass( LowerSwitch )
define_pass( MergeFunctions )
define_pass( NoAA )
define_pass( NoProfileInfo )
define_pass( OptimalEdgeProfiler )
define_pass( PartialInlining )
//define_pass( PartialSpecialization )
define_pass( PostDomOnlyPrinter )
define_pass( PostDomOnlyViewer )
define_pass( PostDomPrinter )
define_pass( PostDomViewer )
define_pass( ProfileEstimator )
define_pass( ProfileLoader )
define_pass( ProfileVerifier )
define_pass( ScalarEvolutionAliasAnalysis )
//define_pass( SimplifyHalfPowrLibCalls )
define_pass( SingleLoopExtractor )
define_pass( StripNonDebugSymbols )
//define_pass( StructRetPromotion )
//define_pass( TailDuplication )
define_pass( UnifyFunctionExitNodes )
*/
/* we support only internalize(true) */
/*
llvm::ModulePass *createInternalize2Pass() { return llvm::createInternalizePass(true); }
define_pass( Internalize2 )
*/
