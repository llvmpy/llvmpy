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

#ifndef LLVM_PY_EXTRA_H
#define LLVM_PY_EXTRA_H

// select PTX or NVPTX

#if LLVM_VERSION_MAJOR >= 3 && LLVM_VERSION_MINOR >= 2
    #define LLVM_HAS_NVPTX 1
#else
    #define LLVM_HAS_NVPTX 0
#endif

#include "llvm-c/Transforms/PassManagerBuilder.h"

#include "llvm_c_extra.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Wraps Instruction::setMetadata()
 */
void LLVMInstSetMetaData(LLVMValueRef instref, const char* mdkind,
                         LLVMValueRef metaref);

/*
 * Wraps MDNode::get()
 */
LLVMValueRef LLVMMetaDataGet(LLVMModuleRef modref, LLVMValueRef * valrefs,
                             unsigned valct);

/*
 * Wraps MDNode::getOperand()
 */
LLVMValueRef LLVMMetaDataGetOperand(LLVMValueRef mdref, unsigned index);

/*
 * Wraps MDNode::getNumOperands()
 */
unsigned LLVMMetaDataGetNumOperands(LLVMValueRef mdref);

/*
 * Wraps MDString::get()
 */
LLVMValueRef LLVMMetaDataStringGet(LLVMModuleRef modref, const char *s);

/*
 * Wraps ConstantExpr::getOpcodeName()
 */
const char *LLVMGetConstExprOpcodeName(LLVMValueRef inst);

/*
 * Wraps ConstantExpr::getOpcode()
 */
unsigned LLVMGetConstExprOpcode(LLVMValueRef inst);

/*
 * Wraps LoadInst::SetAlignment
 */
void LLVMLdSetAlignment(LLVMValueRef inst, unsigned align);

/*
 * Wraps StoreInst::SetAlignment
 */
void LLVMStSetAlignment(LLVMValueRef inst, unsigned align);

const char * LLVMGetHostCPUName();

int LLVMInitializeNativeTargetAsmPrinter();


LLVMTargetMachineRef LLVMTargetMachineLookup(const char *arch, const char *cpu,
                                             const char *features, int opt,
                                             std::string &error);

/*
 * Wraps EngineBuilder::selectTarget
 */
LLVMTargetMachineRef LLVMTargetMachineFromEngineBuilder(LLVMEngineBuilderRef eb);

/*
 * Wraps operator delete
 */
void LLVMDisposeTargetMachine(LLVMTargetMachineRef tm);

/*
 * Wraps TargetMachine::addPassesToEmitFile
 */
unsigned char* LLVMTargetMachineEmitFile(LLVMTargetMachineRef tmref,
                                         LLVMModuleRef modref,
                                         int assembly, size_t * lenp,
                                         std::string &error);

/*
 * Wraps TargetMachine::getTargetData
 */
LLVMTargetDataRef LLVMTargetMachineGetTargetData(LLVMTargetMachineRef tm);

/*
 * Wraps TargetMachine::getTarget().getName()
 */
const char* LLVMTargetMachineGetTargetName(LLVMTargetMachineRef tm);

/*
 * Wraps TargetMachine::getTarget().getShortDescription()
 */
const char* LLVMTargetMachineGetTargetShortDescription(LLVMTargetMachineRef tm);

/*
 * Wraps TargetMachine::getTargetTriple
 */
const char * LLVMTargetMachineGetTriple(LLVMTargetMachineRef tm);

/*
 * Wraps TargetMachine::getTargetCPU
 */
const char * LLVMTargetMachineGetCPU(LLVMTargetMachineRef tm);

/*
 * Wraps TargetMachine::getTargetFeatureString
 */
const char * LLVMTargetMachineGetFS(LLVMTargetMachineRef tm);

/*
 * Wraps TargetRegister::printRegisteredTargetsForVersion
 */
void LLVMPrintRegisteredTargetsForVersion();

/*
 * Wraps TargetMachine::addPassesToEmitFile
 */
unsigned char* LLVMGetNativeCodeFromModule(LLVMModuleRef module, int assembly,
                                           size_t * lenp, std::string &error);

/*
 * Wraps IRBuilder::CreateFence
 */
LLVMValueRef LLVMBuildFence(LLVMBuilderRef builder, const char* ordering,
                            int crossthread);

/*
 * Wraps IRBuilder::CreateLoad, LoadInst::setAtomic
 */
LLVMValueRef LLVMBuildAtomicLoad(LLVMBuilderRef builder, LLVMValueRef ptr,
                                 unsigned align, const char* ordering,
                                 int crossthread);
/*
 * Wraps IRBuilder::CreateStore, StoreInst::setAtomic
 */
LLVMValueRef LLVMBuildAtomicStore(LLVMBuilderRef builder,
                                  LLVMValueRef ptr, LLVMValueRef val,
                                  unsigned align, const char* ordering,
                                  int crossthread);

/*
 * Wraps IRBuilder::CreateAtomicRMW
 */
LLVMValueRef LLVMBuildAtomicRMW(LLVMBuilderRef builder, const char * op,
                                LLVMValueRef ptr, LLVMValueRef val,
                                const char* ordering, int crossthread);

/*
 * Wraps IRBuilder::CreateAtomicCmpXchg
 */
LLVMValueRef LLVMBuildAtomicCmpXchg(LLVMBuilderRef builder, LLVMValueRef ptr,
                                    LLVMValueRef cmp, LLVMValueRef val,
                                    const char* ordering, int crossthread);

/*
 * Wraps new EngineBuilder
 */
LLVMEngineBuilderRef LLVMCreateEngineBuilder(LLVMModuleRef mod);

/*
 * Wraps delete EngineBuilder
 */
void LLVMDisposeEngineBuilder(LLVMEngineBuilderRef eb);


/*
 * Wraps EngineBuilder::setEngineKind(EngineKind::JIT)
 */
void LLVMEngineBuilderForceJIT(LLVMEngineBuilderRef eb);

/*
 * Wraps EngineBuilder::setEngineKind(EngineKind::Interpreter)
 */
void LLVMEngineBuilderForceInterpreter(LLVMEngineBuilderRef eb);


/*
 * Wraps EngineBuilder::setOptLevel
 */
void LLVMEngineBuilderSetOptLevel(LLVMEngineBuilderRef eb, int level);

/*
 * Wraps EngineBuilder::setMCPU
 */
void LLVMEngineBuilderSetMCPU(LLVMEngineBuilderRef eb, const char * mcpu);

/*
 * Wraps EngineBuilder::setMAttrs
 */
void LLVMEngineBuilderSetMAttrs(LLVMEngineBuilderRef eb, const char * mattrs);

/*
 * Wraps EngineBuilder::setErrorStr and EngineBuilder::create
 */
LLVMExecutionEngineRef LLVMEngineBuilderCreate(LLVMEngineBuilderRef eb,
                                               std::string &error);

/*
 * Wraps PassManagerBuilder::OptLevel
 */
int LLVMPassManagerBuilderGetOptLevel(LLVMPassManagerBuilderRef pmb);

/*
 * Wraps PassManagerBuilder::SizeLevel
 */
int LLVMPassManagerBuilderGetSizeLevel(LLVMPassManagerBuilderRef pmb);

/*
 * Wraps PassManagerBuilder::Vectorize
 */
void LLVMPassManagerBuilderSetVectorize(LLVMPassManagerBuilderRef pmb, int flag);

/*
 * Wraps PassManagerBuilder::Vectorize
 */
int LLVMPassManagerBuilderGetVectorize(LLVMPassManagerBuilderRef pmb);

/*
 * Wraps PassManagerBuilder::DisableUnitAtATime
 */
int LLVMPassManagerBuilderGetDisableUnitAtATime(LLVMPassManagerBuilderRef pmb);

/*
 * Wraps PassManagerBuilder::DisableUnrollLoops
 */
int LLVMPassManagerBuilderGetDisableUnrollLoops(LLVMPassManagerBuilderRef pmb);

/*
 * Wraps PassManagerBuilder::DisableSimplifyLibCalls
 */
int LLVMPassManagerBuilderGetDisableSimplifyLibCalls(LLVMPassManagerBuilderRef pmb);

/*
 * Wraps PassManager::add
 */
int LLVMAddPassByName(LLVMPassManagerRef pm, const char * name);

/*
 * Wraps initialize*
 */
void LLVMInitializePasses(void);

/*
 * Wraps PassRegistry::enumerateWith()
 * Returns a '\n' separated string of all passes available to `opt`.
 */
const char * LLVMDumpPasses(void);

/*
 * Wraps StructType::isLiteral()
 */
int LLVMIsLiteralStruct(LLVMTypeRef type);

/*
 * Wraps StructType::create()
 */
LLVMTypeRef LLVMStructTypeIdentified(const char * name);

/*
 * StructType::setBody()
 */
void LLVMSetStructBody(LLVMTypeRef type, LLVMTypeRef* elemtys, unsigned elemct, int is_packed);

/*
 * Wraps llvm::StructType::setName()
 */
void LLVMSetStructName(LLVMTypeRef type, const char * name);


/*
 * Wraps llvm::Module::getModuleIdentifier()
 */
char *LLVMGetModuleIdentifier(LLVMModuleRef module);

/*
 * Wraps llvm::Module::setModuleIdentifier()
 */
void LLVMSetModuleIdentifier(LLVMModuleRef module, const char * name);

/* Notes:
 *  - Some returned strings must be disposed of by LLVMDisposeMessage. These are
 *    indicated in the comments. Where it is not indicated, DO NOT call dispose.
 */

/* Wraps llvm::Module::print(). Dispose the returned string after use, via
 * LLVMDisposeMessage(). */
char *LLVMDumpModuleToString(LLVMModuleRef module);

/* Wraps llvm::Module::addLibrary(name). */
void LLVMModuleAddLibrary(LLVMModuleRef module, const char *name);

/* Wraps llvm::Type::print(). Dispose the returned string after use, via
 * LLVMDisposeMessage(). */
char *LLVMDumpTypeToString(LLVMTypeRef type);

/* Wraps llvm::Value::print(). Dispose the returned string after use, via
 * LLVMDisposeMessage(). */
char *LLVMDumpValueToString(LLVMValueRef Val);

/* Wraps llvm::IRBuilder::CreateRet(). */
LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef bulder, LLVMValueRef *values,
    unsigned n_values);

/* Wraps llvm::IRBuilder::CreateGetResult(). */
LLVMValueRef LLVMBuildGetResult(LLVMBuilderRef builder, LLVMValueRef value,
    unsigned index, const char *name);

/* Wraps llvm::Value::getValueID(). */
unsigned LLVMValueGetID(LLVMValueRef value);

/* Wraps llvm::Value::getNumUses(). */
unsigned LLVMValueGetNumUses(LLVMValueRef value);

/* Wraps llvm::Value::use_{begin,end}. Allocates LLVMValueRef's as
 * required. Number of objects are returned as return value. If that is
 * greater than zero, the pointer given out must be freed by a
 * subsequent call to LLVMDisposeValueRefArray(). */
unsigned LLVMValueGetUses(LLVMValueRef value, LLVMValueRef **refs);

/* See above. */
void LLVMDisposeValueRefArray(LLVMValueRef *refs);

/* Wraps llvm:User::getNumOperands(). */
unsigned LLVMUserGetNumOperands(LLVMValueRef user);

/* Wraps llvm:User::getOperand(). */
LLVMValueRef LLVMUserGetOperand(LLVMValueRef user, unsigned idx);

/* Wraps llvm::ConstantExpr::getVICmp(). */
LLVMValueRef LLVMConstVICmp(LLVMIntPredicate predicate, LLVMValueRef lhs,
    LLVMValueRef rhs);

/* Wraps llvm::ConstantExpr::getVFCmp(). */
LLVMValueRef LLVMConstVFCmp(LLVMRealPredicate predicate, LLVMValueRef lhs,
    LLVMValueRef rhs);

/* Wraps llvm::IRBuilder::CreateVICmp(). */
LLVMValueRef LLVMBuildVICmp(LLVMBuilderRef builder, LLVMIntPredicate predicate,
    LLVMValueRef lhs, LLVMValueRef rhs, const char *name);

/* Wraps llvm::IRBuilder::CreateVFCmp(). */
LLVMValueRef LLVMBuildVFCmp(LLVMBuilderRef builder, LLVMRealPredicate predicate,
    LLVMValueRef lhs, LLVMValueRef rhs, const char *name);

/* Wraps llvm::Intrinsic::getDeclaration(). */
LLVMValueRef LLVMGetIntrinsic(LLVMModuleRef builder, int id,
    LLVMTypeRef *types, unsigned n_types);

/* Wraps llvm::Function::doesNotThrow(). */
unsigned LLVMGetDoesNotThrow(LLVMValueRef fn);

/* Wraps llvm::Function::setDoesNotThrow(). */
void LLVMSetDoesNotThrow(LLVMValueRef fn, int DoesNotThrow);

/* Wraps llvm::Module::getPointerSize(). */
unsigned LLVMModuleGetPointerSize(LLVMModuleRef module);

/* Wraps llvm::Module::getOrInsertFunction(). */
LLVMValueRef LLVMModuleGetOrInsertFunction(LLVMModuleRef module,
    const char *name, LLVMTypeRef function_type);

/* Wraps llvm::GlobalVariable::hasInitializer(). */
int LLVMHasInitializer(LLVMValueRef global_var);

/* The following functions wrap various llvm::Instruction::isXXX() functions.
 * All of them take an instruction and return 0 (isXXX returned false) or 1
 * (isXXX returned false). */
unsigned LLVMInstIsTerminator      (LLVMValueRef inst);
unsigned LLVMInstIsBinaryOp        (LLVMValueRef inst);
unsigned LLVMInstIsShift           (LLVMValueRef inst);
unsigned LLVMInstIsCast            (LLVMValueRef inst);
unsigned LLVMInstIsLogicalShift    (LLVMValueRef inst);
unsigned LLVMInstIsArithmeticShift (LLVMValueRef inst);
unsigned LLVMInstIsAssociative     (LLVMValueRef inst);
unsigned LLVMInstIsCommutative     (LLVMValueRef inst);
unsigned LLVMInstIsTrapping        (LLVMValueRef inst);

/* As above, but these are wrap methods from subclasses of Instruction. */
unsigned LLVMInstIsVolatile        (LLVMValueRef inst);

/* Wraps llvm::Instruction::getOpcodeName(). */
const char *LLVMInstGetOpcodeName(LLVMValueRef inst);

/* Wraps llvm::Instruction::getOpcode(). */
unsigned LLVMInstGetOpcode(LLVMValueRef inst);

/* Wraps llvm::CmpInst::getPredicate(). */
unsigned LLVMCmpInstGetPredicate(LLVMValueRef cmpinst);

/* Wraps llvm::CallSite::getCalledFunction.
 */
LLVMValueRef LLVMInstGetCalledFunction(LLVMValueRef inst);

/* Wraps llvm::ParseAssemblyString(). Returns a module reference or NULL (with
 * `out' pointing to an error message). Dispose error message after use, via
 * LLVMDisposeMessage(). */
LLVMModuleRef LLVMGetModuleFromAssembly(const char *asmtxt, char **out);

/* Wraps llvm::ParseBitcodeFile(). Returns a module reference or NULL (with
 * `out' pointing to an error message). Dispose error message after use, via
 * LLVMDisposeMessage(). */
LLVMModuleRef LLVMGetModuleFromBitcode(const char *bc, unsigned bclen,
    char **out);

#if LLVM_VERSION_MAJOR <= 3 && LLVM_VERSION_MINOR < 2
/* Wraps llvm::Linker::LinkModules().  Returns 0 on failure (with errmsg
 * filled in) and 1 on success.  Dispose error message after use with
 * LLVMDisposeMessage(). */
unsigned LLVMLinkModules(LLVMModuleRef dest, LLVMModuleRef src,
			 unsigned int, char **errmsg);
#endif
/* Returns pointer to a heap-allocated block of `*len' bytes containing bit code
 * for the given module. NULL on error. */
unsigned char *LLVMGetBitcodeFromModule(LLVMModuleRef module, size_t *len);

/* Wraps llvm::sys::DynamicLibrary::LoadLibraryPermanently(). Returns 0 on
 * failure (with errmsg filled in) and 1 on success. Dispose error message after
 * use, via LLVMDisposeMessage(). */
unsigned LLVMLoadLibraryPermanently(const char* filename, char **errmsg);

/* Wraps llvm::ExecutionEngine::getPointerToFunction(). Returns a pointer
 * to the JITted function. */
void *LLVMGetPointerToFunction(LLVMExecutionEngineRef ee, LLVMValueRef fn);

/* Wraps llvm::InlineFunction(). Inlines a function. C is the call
 * instruction, created by LLVMBuildCall. Even if it fails, the Function
 * containing the call is still in a proper state (not changed).
 */
int LLVMInlineFunction(LLVMValueRef call);

/* Wraps llvm::getAlignmentFromAttrs from Attributes.h. Compliments the
 * already available LLVMSetParamAlignment(). */
unsigned LLVMGetParamAlignment(LLVMValueRef arg);

/* Passes. Some passes are used directly from LLVM-C, rest are declared
 * here. */

/*
#define declare_pass(P) \
    void LLVMAdd ## P ## Pass (LLVMPassManagerRef PM);

declare_pass( AAEval )
declare_pass( AliasAnalysisCounter )
declare_pass( AlwaysInliner )
declare_pass( BasicAliasAnalysis )
declare_pass( BlockPlacement )
declare_pass( BreakCriticalEdges )
declare_pass( CodeGenPrepare )
declare_pass( DbgInfoPrinter )
declare_pass( DeadCodeElimination )
declare_pass( DeadInstElimination )
declare_pass( DemoteRegisterToMemory )
declare_pass( DomOnlyPrinter )
declare_pass( DomOnlyViewer )
declare_pass( DomPrinter )
declare_pass( DomViewer )
declare_pass( EdgeProfiler )
//declare_pass( GEPSplitter )
declare_pass( GlobalsModRef )
declare_pass( InstCount )
declare_pass( InstructionNamer )
declare_pass( LazyValueInfo )
declare_pass( LCSSA )
//declare_pass( LiveValues )
declare_pass( LoopDependenceAnalysis )
declare_pass( LoopExtractor )
declare_pass( LoopSimplify )
declare_pass( LoopStrengthReduce )
declare_pass( LowerInvoke )
declare_pass( LowerSwitch )
declare_pass( MergeFunctions )
declare_pass( NoAA )
declare_pass( NoProfileInfo )
declare_pass( OptimalEdgeProfiler )
declare_pass( PartialInlining )
//declare_pass( PartialSpecialization )
declare_pass( PostDomOnlyPrinter )
declare_pass( PostDomOnlyViewer )
declare_pass( PostDomPrinter )
declare_pass( PostDomViewer )
declare_pass( ProfileEstimator )
declare_pass( ProfileLoader )
declare_pass( ProfileVerifier )
declare_pass( ScalarEvolutionAliasAnalysis )
declare_pass( SimplifyHalfPowrLibCalls )
declare_pass( SingleLoopExtractor )
declare_pass( StripNonDebugSymbols )
declare_pass( StructRetPromotion )
declare_pass( TailDuplication )
declare_pass( UnifyFunctionExitNodes )

declare_pass( Internalize2 )
*/

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* LLVM_PY_EXTRA_H */

