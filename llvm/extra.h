/**
 * These are some "extra" functions not available in the standard LLVM-C
 * bindings, but are required / good-to-have inorder to implement the
 * Python bindings.
 */

#ifndef LLVM_PY_EXTRA_H
#define LLVM_PY_EXTRA_H

#ifdef __cplusplus
extern "C" {
#endif

/** Dumps module contents to a string. See Module::print. Free the
    returned string with LLVMDisposeMessage, after use. */
char *LLVMDumpModuleToString(LLVMModuleRef M);

/** Dumps type to a string. See Type::print. Free the returned string with 
    LLVMDisposeMessage, after use. */
char *LLVMDumpTypeToString(LLVMTypeRef Ty);

/** Dumps value to a string. See Value::print. Free the returned string with
    LLVMDisposeMessage, after use. */
char *LLVMDumpValueToString(LLVMValueRef Val);

/* missing constant expressions */

#if 0 /* after LLVM 2.3! */
LLVMValueRef LLVMConstVICmp(LLVMIntPredicate Predicate,
                           LLVMValueRef LHSConstant, LLVMValueRef RHSConstant);
LLVMValueRef LLVMConstVFCmp(LLVMRealPredicate Predicate,
                           LLVMValueRef LHSConstant, LLVMValueRef RHSConstant);

/* missing instructions */

LLVMValueRef LLVMBuildVICmp(LLVMBuilderRef, LLVMIntPredicate Op,
                           LLVMValueRef LHS, LLVMValueRef RHS,
                           const char *Name);
LLVMValueRef LLVMBuildVFCmp(LLVMBuilderRef, LLVMRealPredicate Op,
                           LLVMValueRef LHS, LLVMValueRef RHS,
                           const char *Name);
#endif

LLVMValueRef LLVMBuildRetMultiple(LLVMBuilderRef, LLVMValueRef *Values,
                                  unsigned NumValues);
LLVMValueRef LLVMBuildGetResult(LLVMBuilderRef, LLVMValueRef V,
                                unsigned Index, const char *Name);

/* intrinsics */

LLVMValueRef LLVMGetIntrinsic(LLVMModuleRef B, int ID,
                              LLVMTypeRef *Types, unsigned Count);

/* module */

unsigned LLVMModuleGetPointerSize(LLVMModuleRef M);
LLVMValueRef LLVMModuleGetOrInsertFunction(LLVMModuleRef M, 
    const char *Name, LLVMTypeRef FunctionTy);

/* instruction */

unsigned LLVMInstIsTerminator(LLVMValueRef I);
unsigned LLVMInstIsBinaryOp(LLVMValueRef I);
unsigned LLVMInstIsShift(LLVMValueRef I);
unsigned LLVMInstIsCast(LLVMValueRef I);
unsigned LLVMInstIsLogicalShift(LLVMValueRef I);
unsigned LLVMInstIsArithmeticShift(LLVMValueRef I);
unsigned LLVMInstIsAssociative(LLVMValueRef I);
unsigned LLVMInstIsCommutative(LLVMValueRef I);
unsigned LLVMInstIsTrapping(LLVMValueRef I);

const char *LLVMInstGetOpcodeName(LLVMValueRef I);
unsigned LLVMInstGetOpcode(LLVMValueRef I);

/* reading llvm "assembly" */

LLVMModuleRef LLVMGetModuleFromAssembly(const char *A, unsigned Len,
                                        char **OutMessage);

/* bitcode related */

LLVMModuleRef LLVMGetModuleFromBitcode(const char *BC, unsigned Len,
                                       char **OutMessage);
unsigned char *LLVMGetBitcodeFromModule(LLVMModuleRef M, unsigned *Len);

/* passes */

#define declare_pass(P) \
    void LLVMAdd ## P ## Pass (LLVMPassManagerRef PM);

declare_pass( AggressiveDCE )
declare_pass( ArgumentPromotion )
declare_pass( BlockPlacement )
declare_pass( BreakCriticalEdges )
declare_pass( CodeGenPrepare )
declare_pass( CondPropagation )
declare_pass( ConstantMerge )
//LLVM-C declare_pass( ConstantPropagation )
declare_pass( DeadCodeElimination )
declare_pass( DeadArgElimination )
declare_pass( DeadTypeElimination )
declare_pass( DeadInstElimination )
declare_pass( DeadStoreElimination )
declare_pass( GCSE )
declare_pass( GlobalDCE )
declare_pass( GlobalOptimizer )
//LLVM-C declare_pass( GVN )
declare_pass( GVNPRE )
declare_pass( IndMemRem )
declare_pass( IndVarSimplify )
declare_pass( FunctionInlining )
declare_pass( BlockProfiler )
declare_pass( EdgeProfiler )
declare_pass( FunctionProfiler )
declare_pass( NullProfilerRS )
declare_pass( RSProfiling )
//LLVM-C declare_pass( InstructionCombining )
declare_pass( Internalize )
declare_pass( IPConstantPropagation )
declare_pass( IPSCCP )
declare_pass( JumpThreading )
declare_pass( LCSSA )
declare_pass( LICM )
declare_pass( LoopDeletion )
declare_pass( LoopExtractor )
declare_pass( SingleLoopExtractor )
declare_pass( LoopIndexSplit )
declare_pass( LoopStrengthReduce )
declare_pass( LoopRotate )
declare_pass( LoopUnroll )
declare_pass( LoopUnswitch )
declare_pass( LoopSimplify )
declare_pass( LowerAllocations )
declare_pass( LowerInvoke )
declare_pass( LowerSetJmp )
declare_pass( LowerSwitch )
//LLVM-C declare_pass( PromoteMemoryToRegister )
declare_pass( MemCpyOpt )
declare_pass( UnifyFunctionExitNodes )
declare_pass( PredicateSimplifier )
declare_pass( PruneEH )
declare_pass( RaiseAllocations )
//LLVM-C declare_pass( Reassociate )
declare_pass( DemoteRegisterToMemory )
declare_pass( ScalarReplAggregates )
declare_pass( SCCP )
declare_pass( SimplifyLibCalls )
//LLVM-C declare_pass( CFGSimplification )
declare_pass( StripSymbols )
declare_pass( StripDeadPrototypes )
declare_pass( StructRetPromotion )
declare_pass( TailCallElimination )
declare_pass( TailDuplication )

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* LLVM_PY_EXTRA_H */

