#!/usr/bin/env python

from llvm.core import Module,Type,Builder,ModuleProvider
from llvm.ee import ExecutionEngine
import llvm.core
import ctypes

def test_jit_ctypes():

    # This example demonstrates calling an LLVM defined function using
    # ctypes. It illustrates the common C pattern of having an output
    # variable in the argument list to the function. The function also
    # returns an error code upon exit.

    # setup llvm types
    ty_errcode = Type.int()
    ty_float = Type.float()
    ty_ptr_float = Type.pointer(Type.float())
    ty_func = Type.function(ty_errcode, [ty_float, ty_float, ty_ptr_float])

    # setup ctypes types
    ct_errcode = ctypes.c_int
    ct_float = ctypes.c_float
    ct_ptr_float = ctypes.POINTER(ct_float)
    ct_argtypes = [ct_float, ct_float, ct_ptr_float]

    # generate the function using LLVM
    my_module = Module.new('my_module')

    mult = my_module.add_function(ty_func, "mult")
    mult.args[0].name = "a"
    mult.args[1].name = "b"
    mult.args[2].name = "out"
    mult.args[2].add_attribute(llvm.core.ATTR_NO_CAPTURE) # add nocapture to output arg
    mult.does_not_throw = True # add nounwind attribute to function

    bb = mult.append_basic_block("entry")
    builder = Builder.new(bb)
    tmp = builder.mul( mult.args[0], mult.args[1] )
    builder.store( tmp, mult.args[2] )
    builder.ret(llvm.core.Constant.int(ty_errcode, 0))

    if 0:
        # print the created module
        print my_module

    # compile the function
    mp = ModuleProvider.new(my_module)
    ee = ExecutionEngine.new(mp)

    # let ctypes know about the function
    func_ptr_int = ee.get_pointer_to_function( mult )
    FUNC_TYPE = ctypes.CFUNCTYPE(ct_errcode, *ct_argtypes)
    py_mult = FUNC_TYPE(func_ptr_int)

    # now run the function, calling via ctypes
    output_value = ct_float(123456.0)
    errcode = py_mult( 2.0, 3.0, ctypes.byref(output_value) )
    if errcode != 0:
        raise RuntimeError('unexpected error')
    assert output_value.value == 6.0

if __name__=='__main__':
    test_jit_ctypes()
