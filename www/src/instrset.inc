.LLVM Instruction Set

[frame="all",grid="all"]
`30`70~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Category, Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Terminator instructions,\
"http://www.llvm.org/docs/LangRef.html#i_ret[ret], \
http://www.llvm.org/docs/LangRef.html#i_br[br], \
http://www.llvm.org/docs/LangRef.html#i_switch[switch], \
http://www.llvm.org/docs/LangRef.html#i_invoke[invoke], \
http://www.llvm.org/docs/LangRef.html#i_unwind[unwind], \
http://www.llvm.org/docs/LangRef.html#i_unreachable[unreachable]"
Binary operations,\
"http://www.llvm.org/docs/LangRef.html#i_add[add], \
http://www.llvm.org/docs/LangRef.html#i_sub[sub], \
http://www.llvm.org/docs/LangRef.html#i_mul[mul], \
http://www.llvm.org/docs/LangRef.html#i_udiv[udiv], \
http://www.llvm.org/docs/LangRef.html#i_sdiv[sdiv], \
http://www.llvm.org/docs/LangRef.html#i_fdiv[fdiv], \
http://www.llvm.org/docs/LangRef.html#i_urem[urem], \
http://www.llvm.org/docs/LangRef.html#i_srem[srem], \
http://www.llvm.org/docs/LangRef.html#i_frem[frem]"
Bitwise binary operations,\
"http://www.llvm.org/docs/LangRef.html#i_shl[shl], \
http://www.llvm.org/docs/LangRef.html#i_lshr[lshr], \
http://www.llvm.org/docs/LangRef.html#i_ashr[ashr], \
http://www.llvm.org/docs/LangRef.html#i_and[and], \
http://www.llvm.org/docs/LangRef.html#i_or[or], \
http://www.llvm.org/docs/LangRef.html#i_xor[xor]"
Vector operations,\
"http://www.llvm.org/docs/LangRef.html#i_extractelement[extractelement], \
http://www.llvm.org/docs/LangRef.html#i_insertelement[insertelement], \
http://www.llvm.org/docs/LangRef.html#i_shufflevector[shufflevector]"
Aggregate operations,\
"http://www.llvm.org/docs/LangRef.html#i_extractvalue[extractvalue], \
http://www.llvm.org/docs/LangRef.html#i_insertvalue[insertvalue]"
Memory access and addressing operations,\
"http://www.llvm.org/docs/LangRef.html#i_malloc[malloc], \
http://www.llvm.org/docs/LangRef.html#i_free[free], \
http://www.llvm.org/docs/LangRef.html#i_alloca[alloca], \
http://www.llvm.org/docs/LangRef.html#i_load[load], \
http://www.llvm.org/docs/LangRef.html#i_store[store], \
http://www.llvm.org/docs/LangRef.html#i_getelementptr[getelementptr]"
Conversion operations,\
"http://www.llvm.org/docs/LangRef.html#i_trunc[trunc], \
http://www.llvm.org/docs/LangRef.html#i_zext[zext], \
http://www.llvm.org/docs/LangRef.html#i_sext[sext], \
http://www.llvm.org/docs/LangRef.html#i_fptrunc[fptrunc], \
http://www.llvm.org/docs/LangRef.html#i_fpext[fpext], \
http://www.llvm.org/docs/LangRef.html#i_fptoui[fptoui], \
http://www.llvm.org/docs/LangRef.html#i_fptosi[fptosi], \
http://www.llvm.org/docs/LangRef.html#i_uitofp[uitofp], \
http://www.llvm.org/docs/LangRef.html#i_sitofp[sitofp], \
http://www.llvm.org/docs/LangRef.html#i_ptrtoint[ptrtoint], \
http://www.llvm.org/docs/LangRef.html#i_inttoptr[inttoptr], \
http://www.llvm.org/docs/LangRef.html#i_bitcast[bitcast]"
Other operations,\
"http://www.llvm.org/docs/LangRef.html#i_icmp[icmp], \
http://www.llvm.org/docs/LangRef.html#i_fcmp[fcmp], \
http://www.llvm.org/docs/LangRef.html#i_vicmp[vicmp], \
http://www.llvm.org/docs/LangRef.html#i_vfcmp[vfcmp], \
http://www.llvm.org/docs/LangRef.html#i_phi[phi], \
http://www.llvm.org/docs/LangRef.html#i_select[select], \
http://www.llvm.org/docs/LangRef.html#i_call[call], \
http://www.llvm.org/docs/LangRef.html#i_va_arg[va_arg], \
http://www.llvm.org/docs/LangRef.html#i_getresult[getresult]"
Variable argument handling intrinsics,\
"http://www.llvm.org/docs/LangRef.html#int_va_start[llvm.va_start], \
http://www.llvm.org/docs/LangRef.html#int_va_end[llvm.va_end], \
http://www.llvm.org/docs/LangRef.html#int_va_copy[llvm.va_copy]"
Accurate garbage collection intrinsics,\
"http://www.llvm.org/docs/LangRef.html#int_returnaddress[llvm.returnaddress], \
http://www.llvm.org/docs/LangRef.html#int_frameaddress[llvm.frameaddress], \
http://www.llvm.org/docs/LangRef.html#int_stacksave[llvm.stacksave], \
http://www.llvm.org/docs/LangRef.html#int_stackrestore[llvm.stackrestore], \
http://www.llvm.org/docs/LangRef.html#int_prefetch[llvm.prefetch], \
http://www.llvm.org/docs/LangRef.html#int_pcmarker[llvm.pcmarker], \
http://www.llvm.org/docs/LangRef.html#int_readcyclecounter[llvm.readcyclecounter]"
Standard C library intrinsics,\
"http://www.llvm.org/docs/LangRef.html#int_memcpy[llvm.memcpy.\*], \
http://www.llvm.org/docs/LangRef.html#int_memmove[llvm.memmove.\*], \
http://www.llvm.org/docs/LangRef.html#int_memset[llvm.memset.\*], \
http://www.llvm.org/docs/LangRef.html#int_sqrt[llvm.sqrt.\*], \
http://www.llvm.org/docs/LangRef.html#int_powi[llvm.powi.\*], \
http://www.llvm.org/docs/LangRef.html#int_sin[llvm.sin.\*], \
http://www.llvm.org/docs/LangRef.html#int_cos[llvm.cos.\*], \
http://www.llvm.org/docs/LangRef.html#int_pow[llvm.pow.\*]"
Bit manipulation intrinsics,\
"http://www.llvm.org/docs/LangRef.html#int_bswap[llvm.bswap.\*], \
http://www.llvm.org/docs/LangRef.html#int_ctpop[llvm.ctpop.\*], \
http://www.llvm.org/docs/LangRef.html#int_ctlz[llvm.ctlz.\*], \
http://www.llvm.org/docs/LangRef.html#int_cttz[llvm.cttz.\*], \
http://www.llvm.org/docs/LangRef.html#int_part_select[llvm.part.select.\*], \
http://www.llvm.org/docs/LangRef.html#int_part_set[llvm.part.set.\*]"
Debugger intrinsics,\
"http://www.llvm.org/docs/SourceLevelDebugging.html#format_common_stoppoint[llvm.dbg.stoppoint], \
http://www.llvm.org/docs/SourceLevelDebugging.html#format_common_func_start[llvm.dbg.func.start], \
http://www.llvm.org/docs/SourceLevelDebugging.html#format_common_region_start[llvm.dbg.region.start], \
http://www.llvm.org/docs/SourceLevelDebugging.html#format_common_region_end[llvm.dbg.region.end], \
http://www.llvm.org/docs/SourceLevelDebugging.html#format_common_declare[llvm.dbg.declare]"
Exception handling intrinsics,\
"http://www.llvm.org/docs/ExceptionHandling.html#llvm_eh_exception[llvm.eh_exception], \
http://www.llvm.org/docs/ExceptionHandling.html#llvm_eh_selector[llvm.eh_selector], \
http://www.llvm.org/docs/ExceptionHandling.html#llvm_eh_typeid_for[llvm.eh_typeid_for]"
Trampoline intrinsics,\
"http://www.llvm.org/docs/LangRef.html#int_it[llvm.init.trampoline]"
Atomic intrinsics,\
"http://www.llvm.org/docs/LangRef.html#int_memory_barrier[llvm.memory.barrier], \
http://www.llvm.org/docs/LangRef.html#int_atomic_lcs[llvm.atomic.lcs], \
http://www.llvm.org/docs/LangRef.html#int_atomic_las[llvm.atomic.las], \
http://www.llvm.org/docs/LangRef.html#int_atomic_swap[llvm.atomic.swap]"
General intrinsics,\
"http://www.llvm.org/docs/LangRef.html#int_var_annotation[llvm.var.annotation], \
http://www.llvm.org/docs/LangRef.html#int_annotation[llvm.annotation.\*], \
http://www.llvm.org/docs/LangRef.html#int_trap[llvm.trap]"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

