import api
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


os = api.make_raw_ostream_for_printing()
m.print_(os, None)
print os.str()


int1ty = api.Type.getInt1Ty(context)
int1ty.dump()

print int1ty.isIntegerTy(1)

fnty = api.FunctionType.get(int1ty, False)
fnty.dump()

types = [int1ty, api.Type.getIntNTy(context, 21)]
svt = api.make_small_vector_from_types(*types)
fnty = api.FunctionType.get(int1ty, svt, False)

os = api.make_raw_ostream_for_printing()
fnty.print_(os)
print os.str()

fn = m.getOrInsertFunction("foo", fnty)
os = api.make_raw_ostream_for_printing()
fn.print_(os, None)
print os.str()
