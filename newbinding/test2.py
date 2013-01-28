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
fnty = api.FunctionType.get(int1ty, types, False)

print fnty

const = m.getOrInsertFunction("foo", fnty)
fn = extra.downcast(const, api.Function)
print fn
assert fn.hasName()
assert 'foo' == fn.getName()
fn.setName('bar')
assert 'bar' == fn.getName()

assert fn.getReturnType() is int1ty

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

builder.CreateRetVoid()

assert not bb.empty()
assert bb.getTerminator() is not None

print bb


