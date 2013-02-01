import api
import extra
import _capsule
from StringIO import StringIO
api.capsule.set_debug(True)

def test_basic_jit_use():
    api.InitializeNativeTarget()
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

def test_engine_builder():
    api.InitializeNativeTarget()
    context = api.getGlobalContext()

    m = api.Module.new("modname", context)

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


def main():
    for name, value in globals().items():
        if name.startswith('test_') and callable(value):
            print name.center(80, '-')
            value()

if __name__ == '__main__':
    main()

