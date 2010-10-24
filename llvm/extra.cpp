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

// LLVM includes
#include "llvm/LLVMContext.h"
#include "llvm/Bitcode/ReaderWriter.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/Casting.h"
#include "llvm/Constants.h"
#include "llvm/DerivedTypes.h"
#include "llvm/GlobalVariable.h"
#include "llvm/TypeSymbolTable.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/CallSite.h"
#include "llvm/IntrinsicInst.h"
#include "llvm/Analysis/Verifier.h"
#include "llvm/Assembly/Parser.h"
#include "llvm/System/DynamicLibrary.h"
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

// LLVM-C includes
#include "llvm-c/Core.h"
#include "llvm-c/ExecutionEngine.h"

// our includes
#include "extra.h"

//using namespace llvm;

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

char *LLVMDumpModuleToString(LLVMModuleRef module)
{
    std::string s;
    llvm::raw_string_ostream buf(s);
    llvm::Module *p = llvm::unwrap(module);
    assert(p);
    p->print(buf, NULL);
    return strdup(buf.str().c_str());
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

/* llvm::unwrap a set of `n' wrapped objects starting at `values',
 * into a vector of pointers to llvm::unwrapped objects `out'. */
template <typename W, typename UW>
void unwrap_vec(W *values, unsigned n, std::vector<UW *>& out)
{
    out.clear();

    while (n--) {
        UW *p = llvm::unwrap(*values);
        assert(p);
        out.push_back(p);
        ++values;
    }
}

/* Same as llvm::unwrap_vec, but use a vector of const pointers. */
template <typename W, typename UW>
void unwrap_cvec(W *values, unsigned n, std::vector<const UW *>& out)
{
    out.clear();

    while (n--) {
        UW *p = llvm::unwrap(*values);
        assert(p);
        out.push_back(p);
        ++values;
    }
}

LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef builder, 
    LLVMValueRef *values, unsigned n_values)
{
    assert(values);

    std::vector<llvm::Value *> values_vec;
    unwrap_vec(values, n_values, values_vec);

    llvm::IRBuilder<> *builderp = llvm::unwrap(builder);
    assert(builderp);

    return llvm::wrap(builderp->CreateAggregateRet(&values_vec[0], values_vec.size()));
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
    LLVMValueRef *out = (LLVMValueRef *)malloc(sizeof(LLVMValueRef) * n);
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
    free(refs);
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

    return fnp->setDoesNotThrow((bool)DoesNotThrow);
}

LLVMValueRef LLVMGetIntrinsic(LLVMModuleRef module, int id,
    LLVMTypeRef *types, unsigned n_types)
{
    assert(types);

    std::vector<const llvm::Type*> types_vec;
    unwrap_cvec(types, n_types, types_vec);

    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    llvm::Function *intfunc = llvm::Intrinsic::getDeclaration(modulep, 
        llvm::Intrinsic::ID(id), &types_vec[0], types_vec.size());

    return wrap(intfunc);
}

LLVMModuleRef LLVMGetModuleFromAssembly(const char *asmtext, unsigned txtlen,
    char **out)
{
    assert(asmtext);
    assert(out);

    llvm::Module *modulep;
    llvm::SMDiagnostic error;
    if (!(modulep = llvm::ParseAssemblyString(asmtext, NULL, error,
                                              llvm::getGlobalContext()))) {
        std::string s;
        llvm::raw_string_ostream buf(s);
        error.Print("llvm-py", buf);
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

unsigned LLVMLinkModules(LLVMModuleRef dest, LLVMModuleRef src, char **out)
{
    llvm::Module *sourcep = llvm::unwrap(src);
    assert(sourcep);
    llvm::Module *destinationp = llvm::unwrap(dest);
    assert(destinationp);

    std::string msg;
    if (llvm::Linker::LinkModules(destinationp, sourcep, &msg)) {
        *out = strdup(msg.c_str());
        return 0;
    }

    return 1;
}

unsigned char *LLVMGetBitcodeFromModule(LLVMModuleRef module, unsigned *lenp)
{
    assert(lenp);

    llvm::Module *modulep = llvm::unwrap(module);
    assert(modulep);

    /* get bc into a string */
    std::string s;
    llvm::raw_string_ostream buf(s);
    llvm::WriteBitcodeToFile(modulep, buf);
    const std::string& bc = buf.str();

    /* and then into a malloc()-ed block */
    size_t bclen = bc.size();
    unsigned char *bytes = (unsigned char *)malloc(bclen);
    if (!bytes)
        return NULL;
    memcpy(bytes, bc.data(), bclen);

    /* return */
    *lenp = bclen;
    return bytes;
}

/* Return 0 on failure (with errmsg filled in), 1 on success. */
unsigned LLVMLoadLibraryPermanently(const char* filename, char **errmsg)
{
    assert(filename);
    assert(errmsg);

    /* Note: the LLVM API returns true on failure. Don't ask why. */
    std::string msg;
    if (llvm::sys::DynamicLibrary::LoadLibraryPermanently(filename, &msg)) {
        *errmsg = strdup(msg.c_str());
        return 0;
    }

    return 1;
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

    llvm::CallSite cs = llvm::CallSite::get(callp);

    llvm::InlineFunctionInfo unused;
    return llvm::InlineFunction(cs, unused);
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

#define define_pass(P)                                   \
void LLVMAdd ## P ## Pass (LLVMPassManagerRef passmgr) { \
    using namespace llvm;                                \
    llvm::PassManagerBase *pmp = llvm::unwrap(passmgr);  \
    assert(pmp);                                         \
    pmp->add( create ## P ## Pass ());                   \
}

define_pass( AAEval )
define_pass( AliasAnalysisCounter )
define_pass( AlwaysInliner )
define_pass( BasicAliasAnalysis )
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
define_pass( GEPSplitter )
define_pass( GlobalsModRef )
define_pass( InstCount )
define_pass( InstructionNamer )
define_pass( LazyValueInfo )
define_pass( LCSSA )
define_pass( LiveValues )
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
define_pass( PartialSpecialization )
define_pass( PostDomOnlyPrinter )
define_pass( PostDomOnlyViewer )
define_pass( PostDomPrinter )
define_pass( PostDomViewer )
define_pass( ProfileEstimator )
define_pass( ProfileLoader )
define_pass( ProfileVerifier )
define_pass( ScalarEvolutionAliasAnalysis )
define_pass( SimplifyHalfPowrLibCalls )
define_pass( SingleLoopExtractor )
define_pass( StripNonDebugSymbols )
define_pass( StructRetPromotion )
define_pass( TailDuplication )
define_pass( UnifyFunctionExitNodes )

/* we support only internalize(true) */
llvm::ModulePass *createInternalize2Pass() { return llvm::createInternalizePass(true); }
define_pass( Internalize2 )

