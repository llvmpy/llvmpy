#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ______________________________________________________________________

import ctypes

import llvm.core as lc

# ______________________________________________________________________

lvoid = lc.Type.void()
li1 = lc.Type.int(1)
li8 = lc.Type.int(8)
li16 = lc.Type.int(16)
li32 = lc.Type.int(32)
li64 = lc.Type.int(64)
liptr = lc.Type.int(ctypes.sizeof(ctypes.c_void_p) * 8)
lc_size_t = lc.Type.int(ctypes.sizeof(
        getattr(ctypes, 'c_ssize_t', getattr(ctypes, 'c_size_t'))) * 8)
lfloat = lc.Type.float()
ldouble = lc.Type.double()
li8_ptr = lc.Type.pointer(li8)

lc_int = lc.Type.int(ctypes.sizeof(ctypes.c_int) * 8)
lc_long = lc.Type.int(ctypes.sizeof(ctypes.c_long) * 8)

l_pyobject_head = [lc_size_t, li8_ptr]
l_pyobject_head_struct = lc.Type.struct(l_pyobject_head)
l_pyobj_p = l_pyobject_head_struct_p = lc.Type.pointer(l_pyobject_head_struct)
l_pyobj_pp = lc.Type.pointer(l_pyobj_p)
l_pyfunc = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))

strlen = lc.Type.function(lc_size_t, (li8_ptr,))
strncpy = lc.Type.function(li8_ptr, (li8_ptr, li8_ptr, lc_size_t))
strndup = lc.Type.function(li8_ptr, (li8_ptr, lc_size_t))
malloc = lc.Type.function(li8_ptr, (lc_size_t,))
free = lc.Type.function(lvoid, (li8_ptr,))

PyArg_ParseTuple = lc.Type.function(lc_int, [l_pyobj_p, li8_ptr], True)
PyBool_FromLong = lc.Type.function(l_pyobj_p, [lc_long])
PyErr_GivenExceptionMatches = lc.Type.function(lc_int, (l_pyobj_p, l_pyobj_p))
PyEval_SaveThread = lc.Type.function(li8_ptr, [])
PyEval_RestoreThread = lc.Type.function(lvoid, [li8_ptr])
PyInt_AsLong = lc.Type.function(lc_long, [l_pyobj_p])
PyInt_FromLong = lc.Type.function(l_pyobj_p, [lc_long])
PyNumber_Add = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_Divide = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_Multiply = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_Remainder = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_Subtract = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_TrueDivide = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_InPlaceAdd = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_InPlaceDivide = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_InPlaceMultiply = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_InPlaceRemainder = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_InPlaceSubtract = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
PyNumber_InPlaceTrueDivide = lc.Type.function(l_pyobj_p, (l_pyobj_p,
                                                          l_pyobj_p))
PyObject_IsTrue = lc.Type.function(lc_int, [l_pyobj_p])
PyObject_RichCompare = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p,
                                                    lc_int))
PySequence_Contains = lc.Type.function(lc_int, (l_pyobj_p, l_pyobj_p))
PyString_Check = lc.Type.function(lc_int, [l_pyobj_p])
PyString_CheckExact = lc.Type.function(lc_int, [l_pyobj_p])
PyString_Format = lc.Type.function(l_pyobj_p, (l_pyobj_p, l_pyobj_p))
Py_BuildValue = lc.Type.function(l_pyobj_p, [li8_ptr], True)
Py_DecRef = lc.Type.function(lvoid, [l_pyobj_p])
Py_IncRef = lc.Type.function(lvoid, [l_pyobj_p])

PyInt_Type = li8

# ______________________________________________________________________
# End of bytetype.py
