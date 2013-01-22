import api
#api.capsule.set_debug(True)
context = api.getGlobalContext()

def test():
    print '*' * 80
    m = api.Module.new("modname", context)
    print m.getModuleIdentifier()
    m.setModuleIdentifier('modname2')
    print m.getModuleIdentifier()
    print 'endianness', m.getEndianness()
    assert m.getEndianness() == api.Module.Endianness.AnyEndianness
    print 'pointer-size', m.getPointerSize()
    assert m.getPointerSize() == api.Module.PointerSize.AnyPointerSize
    m.dump()

m = api.Module.new("modname", context)
print m.getModuleIdentifier()
m.setModuleIdentifier('modname2')
print m.getModuleIdentifier()
print 'endianness', m.getEndianness()
assert m.getEndianness() == api.Module.Endianness.AnyEndianness
print 'pointer-size', m.getPointerSize()
assert m.getPointerSize() == api.Module.PointerSize.AnyPointerSize
m.dump()



os = api.raw_svector_ostream_helper.create()
m.print_(os, None)
print os.str()


int1ty = api.Type.getInt1Ty(context)
int1ty.dump()

print int1ty.isIntegerTy(1)

fnty = api.FunctionType.get(int1ty, False)

os2 = api.raw_svector_ostream_helper.create()
fnty.print_(os2)
print os2.str()

