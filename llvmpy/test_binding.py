from io import BytesIO, StringIO

from llvmpy.api import llvm
from llvmpy import extra
from llvmpy import _capsule
import llvmpy.capsule
import collections
llvmpy.capsule.set_debug(True)


llvm.InitializeNativeTarget()
llvm.InitializeNativeTargetAsmPrinter()

def test_basic_jit_use():
    context = llvm.getGlobalContext()

    m = llvm.Module.new("modname", context)
    print(m.getModuleIdentifier())
    m.setModuleIdentifier('modname2')
    print(m.getModuleIdentifier())
    print('endianness', m.getEndianness())
    assert m.getEndianness() == llvm.Module.Endianness.AnyEndianness
    print('pointer-size', m.getPointerSize())
    assert m.getPointerSize() == llvm.Module.PointerSize.AnyPointerSize
    m.dump()


    os = extra.make_raw_ostream_for_printing()
    m.print_(os, None)
    print(os.str())


    int1ty = llvm.Type.getInt1Ty(context)
    int1ty.dump()

    assert int1ty.isIntegerTy(1)

    fnty = llvm.FunctionType.get(int1ty, False)
    fnty.dump()

    types = [llvm.Type.getIntNTy(context, 8), llvm.Type.getIntNTy(context, 32)]
    fnty = llvm.FunctionType.get(llvm.Type.getIntNTy(context, 8), types, False)

    print(fnty)

    const = m.getOrInsertFunction("foo", fnty)
    fn = const._downcast(llvm.Function)
    print(fn)
    assert fn.hasName()
    assert 'foo' == fn.getName()
    fn.setName('bar')
    assert 'bar' == fn.getName()

    assert fn.getReturnType().isIntegerTy(8)

    assert fnty is fn.getFunctionType()

    assert fn.isVarArg() == False
    assert fn.getIntrinsicID() == 0
    assert not fn.isIntrinsic()

    fn_uselist = fn.list_use()
    assert isinstance(fn_uselist, list)
    assert len(fn_uselist) == 0

    builder = llvm.IRBuilder.new(context)
    print(builder)

    bb = llvm.BasicBlock.Create(context, "entry", fn, None)
    assert bb.empty()
    builder.SetInsertPoint(bb)

    assert bb.getTerminator() is None

    arg0, arg1 = fn.getArgumentList()
    print(arg0, arg1)

    extended = builder.CreateZExt(arg0, arg1.getType())
    result = builder.CreateAdd(extended, arg1)
    ret = builder.CreateTrunc(result, fn.getReturnType())
    builder.CreateRet(ret)

    print(arg0.list_use())

    print(fn)

    errio = StringIO()
    print(m)

    # verifier
    action = llvm.VerifierFailureAction.ReturnStatusAction

    corrupted = llvm.verifyFunction(fn, action)
    assert not corrupted
    corrupted = llvm.verifyModule(m, action, errio)
    print(corrupted)
    assert not corrupted, errio.getvalue()

    # build pass manager
    pmb = llvm.PassManagerBuilder.new()
    pmb.OptLevel = 3
    assert pmb.OptLevel == 3
    pmb.LibraryInfo = llvm.TargetLibraryInfo.new()
    pmb.Inliner = llvm.createFunctionInliningPass()

    fpm = llvm.FunctionPassManager.new(m)
    pm = llvm.PassManager.new()

    pmb.populateFunctionPassManager(fpm)
    pmb.populateModulePassManager(pm)

    fpm.doInitialization()
    fpm.run(fn)
    fpm.doFinalization()

    pm.run(m)

    print(m)

    # build engine

    ee = llvm.ExecutionEngine.createJIT(m, errio)
    print(ee, errio.getvalue())
    print(ee.getDataLayout().getStringRepresentation())

    datalayout_str = 'e-p:64:64:64-S128-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f16:16:16-f32:32:32-f64:64:64-f128:128:128-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64'

    assert datalayout_str == str(llvm.DataLayout.new(datalayout_str))
    assert datalayout_str == str(llvm.DataLayout.new(str(llvm.DataLayout.new(datalayout_str))))

    fn2 = ee.FindFunctionNamed(fn.getName())
    assert fn2 is fn

    assert ee.getPointerToFunction(fn)
    assert ee.getPointerToNamedFunction('printf')

    gv0 = llvm.GenericValue.CreateInt(arg0.getType(), 12, False)
    gv1 = llvm.GenericValue.CreateInt(arg1.getType(), -32, True)

    assert gv0.valueIntWidth() == arg0.getType().getIntegerBitWidth()
    assert gv1.valueIntWidth() == arg1.getType().getIntegerBitWidth()

    assert gv0.toUnsignedInt() == 12
    assert gv1.toSignedInt() == -32

    gv1 = llvm.GenericValue.CreateInt(arg1.getType(), 32, False)

    gvR = ee.runFunction(fn, (gv0, gv1))

    assert 44 == gvR.toUnsignedInt()

    # write bitcode
    bc_buffer = BytesIO()
    llvm.WriteBitcodeToFile(m, bc_buffer)
    bc = bc_buffer.getvalue()
    bc_buffer.close()

    # read bitcode
    errbuf = BytesIO()
    m2 = llvm.ParseBitCodeFile(bc, context, errbuf)
    if not m2:
        raise Exception(errbuf.getvalue())
    else:
        m2.setModuleIdentifier(m.getModuleIdentifier())
        assert str(m2) == str(m)

    # parse llvm ir
    m3 = llvm.ParseAssemblyString(str(m), None, llvm.SMDiagnostic.new(), context)
    m3.setModuleIdentifier(m.getModuleIdentifier())
    assert str(m3) == str(m)

    # test clone
    m4 = llvm.CloneModule(m)
    assert m4 is not m
    assert str(m4) == str(m)

def test_engine_builder():
    llvm.InitializeNativeTarget()
    context = llvm.getGlobalContext()

    m = llvm.Module.new("modname", context)

    int32ty = llvm.Type.getIntNTy(context, 32)
    fnty = llvm.FunctionType.get(int32ty, [int32ty], False)
    fn = m.getOrInsertFunction("foo", fnty)._downcast(llvm.Function)
    bb = llvm.BasicBlock.Create(context, "entry", fn, None)
    builder = llvm.IRBuilder.new(context)
    builder.SetInsertPoint(bb)
    builder.CreateRet(fn.getArgumentList()[0])

    print(fn)

    eb = llvm.EngineBuilder.new(m)
    eb2 = eb.setEngineKind(llvm.EngineKind.Kind.JIT)
    assert eb is eb2
    eb.setOptLevel(llvm.CodeGenOpt.Level.Aggressive).setUseMCJIT(False)

    tm = eb.selectTarget()

    print('target triple:', tm.getTargetTriple())
    print('target cpu:', tm.getTargetCPU())
    print('target feature string:', tm.getTargetFeatureString())

    target = tm.getTarget()
    print('target name:', target.getName())
    print('target short description:', target.getShortDescription())

    assert target.hasJIT()
    assert target.hasTargetMachine()

    ee = eb.create(tm)

    triple = llvm.Triple.new('x86_64-unknown-linux')
    assert triple.getArchName() == 'x86_64'
    assert triple.getVendorName() == 'unknown'
    assert triple.getOSName() == 'linux'
    assert triple.isArch64Bit()
    assert not triple.isArch32Bit()
    triple_32variant = triple.get32BitArchVariant()
    assert triple_32variant.isArch32Bit()

    print(tm.getDataLayout())

    pm = llvm.PassManager.new()
    pm.add(llvm.DataLayout.new(str(tm.getDataLayout())))
    pm.add(llvm.TargetLibraryInfo.new())

    # write assembly
    pm = llvm.PassManager.new()
    pm.add(llvm.DataLayout.new(str(tm.getDataLayout())))

    raw = extra.make_raw_ostream_for_printing()
    formatted = llvm.formatted_raw_ostream.new(raw, False)

    cgft = llvm.TargetMachine.CodeGenFileType.CGFT_AssemblyFile
    failed = tm.addPassesToEmitFile(pm, formatted, cgft, False)
    assert not failed

    pm.run(m)

    formatted.flush()
    raw.flush()
    asm = raw.str()
    print(asm)
    assert 'foo' in asm


def test_linker():
    context = llvm.getGlobalContext()

    mA = llvm.Module.new("modA", context)
    mB = llvm.Module.new("modB", context)

    def create_function(m, name):
        int32ty = llvm.Type.getIntNTy(context, 32)
        fnty = llvm.FunctionType.get(int32ty, [int32ty], False)
        fn = m.getOrInsertFunction(name, fnty)._downcast(llvm.Function)
        bb = llvm.BasicBlock.Create(context, "entry", fn, None)
        builder = llvm.IRBuilder.new(context)
        builder.SetInsertPoint(bb)
        builder.CreateRet(fn.getArgumentList()[0])

    create_function(mA, 'foo')
    create_function(mB, 'bar')

    errmsg = StringIO()
    linkermode = llvm.Linker.LinkerMode.PreserveSource
    failed = llvm.Linker.LinkModules(mA, mB, linkermode, errmsg)
    assert not failed, errmsg.getvalue()
    assert mA.getFunction('foo')
    assert mA.getFunction('bar')

    assert set(mA.list_functions()) == set([mA.getFunction('foo'),
                                            mA.getFunction('bar')])

def test_structtype():
    context = llvm.getGlobalContext()
    m = llvm.Module.new("modname", context)

    assert m.getTypeByName("truck") is None

    truck = llvm.StructType.create(context, "truck")
    assert 'type opaque' in str(truck)
    elemtys = [llvm.Type.getInt32Ty(context), llvm.Type.getDoubleTy(context)]
    truck.setBody(elemtys)

    assert 'i32' in str(truck)
    assert 'double' in str(truck)

    assert m.getTypeByName("truck") is truck

def test_globalvariable():
    context = llvm.getGlobalContext()
    m = llvm.Module.new("modname", context)

    ty = llvm.Type.getInt32Ty(context)
    LinkageTypes = llvm.GlobalVariable.LinkageTypes
    linkage = LinkageTypes.ExternalLinkage
    gvar = llvm.GlobalVariable.new(m, ty, False, linkage, None, "apple")
    assert '@apple = external global i32' in str(m)

    gvar2 = m.getNamedGlobal('apple')
    assert gvar2 is gvar

    print(m.list_globals())


def test_sequentialtypes():
    context = llvm.getGlobalContext()
    int32ty = llvm.Type.getInt32Ty(context)
    ary_int32x4 = llvm.ArrayType.get(int32ty, 4)
    assert '[4 x i32]' == str(ary_int32x4)
    ptr_int32 = llvm.PointerType.get(int32ty, 1)
    assert 'i32 addrspace(1)*' == str(ptr_int32)
    vec_int32x4 = llvm.VectorType.get(int32ty, 4)
    assert '<4 x i32>' == str(vec_int32x4)


def test_constants():
    context = llvm.getGlobalContext()
    int32ty = llvm.Type.getInt32Ty(context)
    ary_int32x4 = llvm.ArrayType.get(int32ty, 4)
    intconst = llvm.ConstantInt.get(int32ty, 123)
    aryconst = llvm.ConstantArray.get(ary_int32x4, [intconst] * 4)
    assert str(aryconst.getAggregateElement(0)) == str(intconst)

    bignum = 4415104608
    int64ty = llvm.Type.getInt64Ty(context)
    const_bignum = llvm.ConstantInt.get(int64ty, 4415104608)
    assert str(bignum) in str(const_bignum)

def test_intrinsic():
    context = llvm.getGlobalContext()
    m = llvm.Module.new("modname", context)
    INTR_SIN = 1652
    floatty = llvm.Type.getFloatTy(context)
    fn = llvm.Intrinsic.getDeclaration(m, INTR_SIN, [floatty])
    assert 'llvm.sin.f32' in str(fn)
    fn.eraseFromParent()
    assert 'llvm.sin.f32' not in str(m)

def test_passregistry():
    passreg = llvm.PassRegistry.getPassRegistry()

    llvm.initializeScalarOpts(passreg)

    passinfo = passreg.getPassInfo("dce")
    dcepass = passinfo.createPass()
    print(dcepass.getPassName())

    print(passreg.enumerate())

def test_targetregistry():
    llvm.TargetRegistry.printRegisteredTargetsForVersion()
    errmsg = StringIO()

    target = llvm.TargetRegistry.getClosestTargetForJIT(errmsg)
    errmsg.close()

    print(target.getName())
    print(target.getShortDescription())
    assert target.hasJIT()
    assert target.hasTargetMachine()

    next = target.getNext()
    if next:
        print(next.getName())
        print(next.getShortDescription())

    triple = llvm.sys.getDefaultTargetTriple()
    cpu = llvm.sys.getHostCPUName()
    features = {}
    assert not llvm.sys.getHostCPUFeatures(features), "Only for Linux and ARM?"

    targetoptions = llvm.TargetOptions.new()
    tm = target.createTargetMachine(triple, cpu, "", targetoptions)

def main():
    for name, value in list(globals().items()):
        if name.startswith('test_') and isinstance(value, collections.Callable):
            print(name.center(80, '-'))
            value()


if __name__ == '__main__':
    main()

