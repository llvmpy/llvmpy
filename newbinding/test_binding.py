import api
import extra
import _capsule
from StringIO import StringIO
api.capsule.set_debug(True)

def test_basic_jit_use():
    api.InitializeNativeTarget()
    api.InitializeNativeTargetAsmPrinter()
    context = api.getGlobalContext()

    m = api.Module.new("modname", context)
    print m.getModuleIdentifier()
    m.setModuleIdentifier('modname2')
    print m.getModuleIdentifier()
    print 'endianness', m.getEndianness()
    assert m.getEndianness() == api.Module.Endianness.AnyEndianness
    print 'pointer-size', m.getPointerSize()
    assert m.getPointerSize() == api.Module.PointerSize.AnyPointerSize
    m.dump()


    os = extra.make_raw_ostream_for_printing()
    m.print_(os, None)
    print os.str()


    int1ty = api.Type.getInt1Ty(context)
    int1ty.dump()

    assert int1ty.isIntegerTy(1)

    fnty = api.FunctionType.get(int1ty, False)
    fnty.dump()

    types = [api.Type.getIntNTy(context, 8), api.Type.getIntNTy(context, 32)]
    fnty = api.FunctionType.get(api.Type.getIntNTy(context, 8), types, False)

    print fnty

    const = m.getOrInsertFunction("foo", fnty)
    fn = const._downcast(api.Function)
    print fn
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

    builder = api.IRBuilder.new(context)
    print builder

    bb = api.BasicBlock.Create(context, "entry", fn, None)
    assert bb.empty()
    builder.SetInsertPoint(bb)

    assert bb.getTerminator() is None

    arg0, arg1 = fn.getArgumentList()
    print arg0, arg1

    extended = builder.CreateZExt(arg0, arg1.getType())
    result = builder.CreateAdd(extended, arg1)
    ret = builder.CreateTrunc(result, fn.getReturnType())
    builder.CreateRet(ret)

    print arg0.list_use()

    print fn

    errio = StringIO()
    print m

    # verifier
    action = api.VerifierFailureAction.ReturnStatusAction

    corrupted = api.verifyFunction(fn, action)
    assert not corrupted
    corrupted = api.verifyModule(m, action, errio)
    print corrupted
    assert not corrupted, errio.getvalue()

    # build pass manager
    pmb = api.PassManagerBuilder.new()
    pmb.OptLevel = 3
    assert pmb.OptLevel == 3
    pmb.LibraryInfo = api.TargetLibraryInfo.new()
    pmb.Inliner = api.createFunctionInliningPass()

    fpm = api.FunctionPassManager.new(m)
    pm = api.PassManager.new()

    pmb.populateFunctionPassManager(fpm)
    pmb.populateModulePassManager(pm)

    fpm.doInitialization()
    fpm.run(fn)
    fpm.doFinalization()
    
    pm.run(m)

    print m

    # build engine

    ee = api.ExecutionEngine.createJIT(m, errio)
    print ee, errio.getvalue()
    print ee.getDataLayout().getStringRepresentation()

    datalayout_str = 'e-p:64:64:64-S128-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f16:16:16-f32:32:32-f64:64:64-f128:128:128-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64'

    assert datalayout_str == str(api.DataLayout.new(datalayout_str))
    assert datalayout_str == str(api.DataLayout.new(str(api.DataLayout.new(datalayout_str))))

    fn2 = ee.FindFunctionNamed(fn.getName())
    assert fn2 is fn

    assert ee.getPointerToFunction(fn)
    assert ee.getPointerToNamedFunction('printf')

    gv0 = api.GenericValue.CreateInt(arg0.getType(), 12, False)
    gv1 = api.GenericValue.CreateInt(arg1.getType(), -32, True)

    assert gv0.valueIntWidth() == arg0.getType().getIntegerBitWidth()
    assert gv1.valueIntWidth() == arg1.getType().getIntegerBitWidth()

    assert gv0.toUnsignedInt() == 12
    assert gv1.toSignedInt() == -32

    gv1 = api.GenericValue.CreateInt(arg1.getType(), 32, False)

    gvR = ee.runFunction(fn, (gv0, gv1))

    assert 44 == gvR.toUnsignedInt()

    # write bitcode
    bc_buffer = StringIO()
    api.WriteBitcodeToFile(m, bc_buffer)
    bc = bc_buffer.getvalue()
    bc_buffer.close()

    # read bitcode
    errbuf = StringIO()
    m2 = api.ParseBitCodeFile(bc, context, errbuf)
    if not m2:
        raise Exception(errbuf.getvalue())
    else:
        m2.setModuleIdentifier(m.getModuleIdentifier())
        assert str(m2) == str(m)

    # parse llvm ir
    m3 = api.ParseAssemblyString(str(m), None, api.SMDiagnostic.new(), context)
    m3.setModuleIdentifier(m.getModuleIdentifier())
    assert str(m3) == str(m)

    # test clone
    m4 = api.CloneModule(m)
    assert m4 is not m
    assert str(m4) == str(m)

def test_engine_builder():
    api.InitializeNativeTarget()
    context = api.getGlobalContext()

    m = api.Module.new("modname", context)

    int32ty = api.Type.getIntNTy(context, 32)
    fnty = api.FunctionType.get(int32ty, [int32ty], False)
    fn = m.getOrInsertFunction("foo", fnty)._downcast(api.Function)
    bb = api.BasicBlock.Create(context, "entry", fn, None)
    builder = api.IRBuilder.new(context)
    builder.SetInsertPoint(bb)
    builder.CreateRet(fn.getArgumentList()[0])

    print fn

    eb = api.EngineBuilder.new(m)
    eb2 = eb.setEngineKind(api.EngineKind.Kind.JIT)
    assert eb is eb2
    eb.setOptLevel(api.CodeGenOpt.Level.Aggressive).setUseMCJIT(False)

    tm = eb.selectTarget()

    print 'target triple:', tm.getTargetTriple()
    print 'target cpu:', tm.getTargetCPU()
    print 'target feature string:', tm.getTargetFeatureString()

    target = tm.getTarget()
    print 'target name:', target.getName()
    print 'target short description:', target.getShortDescription()

    assert target.hasJIT()
    assert target.hasTargetMachine()

    ee = eb.create(tm)

    triple = api.Triple.new('x86_64-unknown-linux')
    assert triple.getArchName() == 'x86_64'
    assert triple.getVendorName() == 'unknown'
    assert triple.getOSName() == 'linux'
    assert triple.isArch64Bit()
    assert not triple.isArch32Bit()
    triple_32variant = triple.get32BitArchVariant()
    assert triple_32variant.isArch32Bit()

    print tm.getDataLayout()

    pm = api.PassManager.new()
    pm.add(api.DataLayout.new(str(tm.getDataLayout())))
    pm.add(api.TargetLibraryInfo.new())

    # write assembly
    pm = api.PassManager.new()
    pm.add(api.DataLayout.new(str(tm.getDataLayout())))

    raw = extra.make_raw_ostream_for_printing()
    formatted = api.formatted_raw_ostream.new(raw, False)

    cgft = api.TargetMachine.CodeGenFileType.CGFT_AssemblyFile
    failed = tm.addPassesToEmitFile(pm, formatted, cgft, False)
    assert not failed

    pm.run(m)

    formatted.flush()
    raw.flush()
    asm = raw.str()
    print asm
    assert 'foo' in asm


def test_linker():
    context = api.getGlobalContext()

    mA = api.Module.new("modA", context)
    mB = api.Module.new("modB", context)

    def create_function(m, name):
        int32ty = api.Type.getIntNTy(context, 32)
        fnty = api.FunctionType.get(int32ty, [int32ty], False)
        fn = m.getOrInsertFunction(name, fnty)._downcast(api.Function)
        bb = api.BasicBlock.Create(context, "entry", fn, None)
        builder = api.IRBuilder.new(context)
        builder.SetInsertPoint(bb)
        builder.CreateRet(fn.getArgumentList()[0])

    create_function(mA, 'foo')
    create_function(mB, 'bar')

    errmsg = StringIO()
    linkermode = api.Linker.LinkerMode.PreserveSource
    failed = api.Linker.LinkModules(mA, mB, linkermode, errmsg)
    assert not failed, errmsg.getvalue()
    assert mA.getFunction('foo')
    assert mA.getFunction('bar')

    assert set(mA.list_functions()) == set([mA.getFunction('foo'),
                                            mA.getFunction('bar')])

def test_structtype():
    context = api.getGlobalContext()
    m = api.Module.new("modname", context)

    assert m.getTypeByName("truck") is None

    truck = api.StructType.create(context, "truck")
    assert 'type opaque' in str(truck)
    elemtys = [api.Type.getInt32Ty(context), api.Type.getDoubleTy(context)]
    truck.setBody(elemtys)

    assert 'i32' in str(truck)
    assert 'double' in str(truck)

    assert m.getTypeByName("truck") is truck

def test_globalvariable():
    context = api.getGlobalContext()
    m = api.Module.new("modname", context)

    ty = api.Type.getInt32Ty(context)
    LinkageTypes = api.GlobalVariable.LinkageTypes
    linkage = LinkageTypes.ExternalLinkage
    gvar = api.GlobalVariable.new(m, ty, False, linkage, None, "apple")
    assert '@apple = external global i32' in str(m)

    gvar2 = m.getNamedGlobal('apple')
    assert gvar2 is gvar

    print m.list_globals()


def test_sequentialtypes():
    context = api.getGlobalContext()
    int32ty = api.Type.getInt32Ty(context)
    ary_int32x4 = api.ArrayType.get(int32ty, 4)
    assert '[4 x i32]' == str(ary_int32x4)
    ptr_int32 = api.PointerType.get(int32ty, 1)
    assert 'i32 addrspace(1)*' == str(ptr_int32)
    vec_int32x4 = api.VectorType.get(int32ty, 4)
    assert '<4 x i32>' == str(vec_int32x4)


def test_constants():
    context = api.getGlobalContext()
    int32ty = api.Type.getInt32Ty(context)
    ary_int32x4 = api.ArrayType.get(int32ty, 4)
    intconst = api.ConstantInt.get(int32ty, 123)
    aryconst = api.ConstantArray.get(ary_int32x4, [intconst] * 4)
    assert str(aryconst.getAggregateElement(0)) == str(intconst)

def test_intrinsic():
    context = api.getGlobalContext()
    m = api.Module.new("modname", context)
    INTR_SIN = 1652
    floatty = api.Type.getFloatTy(context)
    fn = api.Intrinsic.getDeclaration(m, INTR_SIN, [floatty])
    assert 'llvm.sin.f32' in str(fn)
    fn.eraseFromParent()
    assert 'llvm.sin.f32' not in str(m)

def main():
    for name, value in globals().items():
        if name.startswith('test_') and callable(value):
            print name.center(80, '-')
            value()


if __name__ == '__main__':
    main()

