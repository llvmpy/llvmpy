import _api

context = _api.getGlobalContext()
modname = "modname"
module = _api.Module.new(modname, context)
assert modname == _api.Module.getModuleIdentifier(module)
modname2 = "newmodname"
_api.Module.setModuleIdentifier(module, modname2)
assert modname2 == _api.Module.getModuleIdentifier(module)

_api.Module.dump(module)

_api.Module.delete(module)

voidty = _api.Type.getVoidTy(context)
assert _api.Type.isVoidTy(voidty)
assert not _api.Type.isLabelTy(voidty)

int21ty = _api.Type.getIntNTy(context, 21)
assert _api.Type.isIntegerTy(int21ty)
assert _api.Type.isIntegerTy(int21ty, 21)
_api.Type.dump(int21ty)

halfty = _api.Type.getHalfTy(context)
assert _api.Type.isHalfTy(halfty)
_api.Type.dump(halfty)

fnty = _api.FunctionType.get(halfty, False)
_api.Type.dump(fnty)



