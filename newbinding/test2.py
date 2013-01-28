import api
import extra
import _capsule
api.capsule.set_debug(True)
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

print int1ty.isIntegerTy(1)

fnty = api.FunctionType.get(int1ty, False)
fnty.dump()

types = [int1ty, api.Type.getIntNTy(context, 21)]
svt = extra.make_small_vector_from_types(*types)
fnty = api.FunctionType.get(int1ty, svt, False)

os = extra.make_raw_ostream_for_printing()
fnty.print_(os)
print os.str()

const = m.getOrInsertFunction("foo", fnty)
fn = extra.downcast(const, api.Function)
os = extra.make_raw_ostream_for_printing()
fn.print_(os, None)
print os.str()
assert fn.hasName()
assert 'foo' == fn.getName()
fn.setName('bar')
assert 'bar' == fn.getName()

os = extra.make_raw_ostream_for_printing()
assert fn.getReturnType() is int1ty

assert fnty is fn.getFunctionType()

assert fn.isVarArg() == False
assert fn.getIntrinsicID() == 0
assert not fn.isIntrinsic()

print fn.list_use()

builder = api.IRBuilder.new(context)
print builder

bb = api.BasicBlock.Create(context, "entry", fn, None)
builder.SetInsertPoint(bb)

builder.CreateRetVoid()

fn.dump()
