from binding import *
from .namespace import llvm
from .ADT.StringRef import StringRef

MemoryObject = llvm.Class()
BytesMemoryObject = llvm.Class(MemoryObject)

@MemoryObject
class MemoryObject:
	pass

@BytesMemoryObject
class BytesMemoryObject:
	new = Constructor(cast(bytes, StringRef))

	getBase = Method(cast(Uint64, int))
	getExtent = Method(cast(Uint64, int))
