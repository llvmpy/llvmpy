import api
#api.enable_capsule_dtor_debug(True)
context = api.getGlobalContext()

m = api.Module.new("modname", context)
print m.getModuleIdentifier()
m.setModuleIdentifier('modname2')
print m.getModuleIdentifier()
m.dump()
os = api.raw_svector_ostream_helper.create()
m.print_(os, None)
print os.str()

int1ty = api.Type.getInt1Ty(context)
int1ty.dump()

print int1ty.isIntegerTy(1)



