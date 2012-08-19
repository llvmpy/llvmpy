#! /usr/bin/env python
'''
Test and stress Constants.
'''
import unittest
import logging

from llvm.core import *
from llvm.ee import *
from ctypes import *


# logging.basicConfig(level=logging.DEBUG)

def _build_test_module(datatype, constants):
    mod = Module.new('module_test_const_%s' % datatype)
    fnty_callback = Type.function(Type.void(), [datatype])
    fnty_subject = Type.function(Type.void(), [Type.pointer(fnty_callback)])
    func_subject = mod.add_function(fnty_subject, 'test_const_%s' % datatype)

    bb_entry = func_subject.append_basic_block('entry')
    builder = Builder.new(bb_entry)



    for k in constants:
        builder.call(func_subject.args[0], [k])

    builder.ret_void()

    func_subject.verify()

    return mod, func_subject

def _build_test_module_array(datatype, constants):
    mod = Module.new('module_test_const_%s' % datatype)
    fnty_callback = Type.function(Type.void(), [datatype])
    fnty_subject = Type.function(Type.void(), [Type.pointer(fnty_callback)])
    func_subject = mod.add_function(fnty_subject, 'test_const_%s' % datatype)

    bb_entry = func_subject.append_basic_block('entry')
    builder = Builder.new(bb_entry)


    for k in constants:
        ptr = builder.alloca(k.type)
        builder.store(k, ptr)
        builder.call(func_subject.args[0],
                     [builder.gep(ptr, [Constant.int(Type.int(), 0)]*2)])

    builder.ret_void()

    func_subject.verify()

    return mod, func_subject

def _build_test_module_struct(datatype, constants):
    mod = Module.new('module_test_const_%s' % datatype)
    fnty_callback = Type.function(Type.void(), [datatype])
    fnty_subject = Type.function(Type.void(), [Type.pointer(fnty_callback)])
    func_subject = mod.add_function(fnty_subject, 'test_const_%s' % datatype)

    bb_entry = func_subject.append_basic_block('entry')
    builder = Builder.new(bb_entry)

    for k in constants:
        ptr = builder.alloca(k.type)
        builder.store(k, ptr)
        builder.call(func_subject.args[0], [ptr])

    builder.ret_void()

    func_subject.verify()

    return mod, func_subject

class TestConstants(unittest.TestCase):
    def test_const_int(self):
        from random import randint
        values = [0, -1, 1, 0xfffffffe, 0xffffffff, 0x100000000]
        values += [randint(0, 0xffffffff) for x in range(100)]

        constant_list = map(lambda X: Constant.int(Type.int(), X), values)
        mod, func_subject = _build_test_module(Type.int(), constant_list)

        # done function generation
        logging.debug(func_subject)

        # prepare execution
        ee = ExecutionEngine.new(mod)

        cf_callback = CFUNCTYPE(None, c_uint32)
        cf_test = CFUNCTYPE(None, cf_callback)

        test_subject = cf_test(ee.get_pointer_to_function(func_subject))

        # setup callback
        results = []
        def callback(value):
            results.append(value)

        test_subject(cf_callback(callback))

        # check result
        for result, golden in zip(results, values):
            self.assertEqual(result, golden & 0xffffffff)

    def test_const_float(self):
        from random import random
        values = [0., 1., -1.] + [random() for x in range(100)]

        constant_list = map(lambda X: Constant.real(Type.float(), X), values)
        mod, func_subject = _build_test_module(Type.float(), constant_list)

        # done function generation
        logging.debug(func_subject)

        # prepare execution
        ee = ExecutionEngine.new(mod)

        cf_callback = CFUNCTYPE(None, c_float)
        cf_test = CFUNCTYPE(None, cf_callback)

        test_subject = cf_test(ee.get_pointer_to_function(func_subject))

        # setup callback
        results = []
        def callback(value):
            results.append(value)

        test_subject(cf_callback(callback))

        # check result
        for result, golden in zip(results, values):
            if golden == 0:
                self.assertEqual(result, golden)
            else:
                self.assert_(abs(result-golden)/golden < 1e-7)

    def test_const_double(self):
        from random import random
        values = [0., 1., -1.] + [random() for x in range(100)]

        constant_list = map(lambda X: Constant.real(Type.double(), X), values)
        mod, func_subject = _build_test_module(Type.double(), constant_list)

        # done function generation
        logging.debug(func_subject)

        # prepare execution
        ee = ExecutionEngine.new(mod)

        cf_callback = CFUNCTYPE(None, c_double)
        cf_test = CFUNCTYPE(None, cf_callback)

        test_subject = cf_test(ee.get_pointer_to_function(func_subject))

        # setup callback
        results = []
        def callback(value):
            results.append(value)

        test_subject(cf_callback(callback))

        # check result
        for result, golden in zip(results, values):
            self.assertEqual(result, golden)

    def test_const_string(self):
        values = ["hello", "world", "", "\n"]

        constant_list = map(Constant.stringz, values)
        mod, func_subject = _build_test_module_array(Type.pointer(Type.int(8)),
                                                     constant_list)

        # done function generation
        logging.debug(func_subject)

        # prepare execution
        ee = ExecutionEngine.new(mod)

        cf_callback = CFUNCTYPE(None, c_char_p)
        cf_test = CFUNCTYPE(None, cf_callback)

        test_subject = cf_test(ee.get_pointer_to_function(func_subject))

        # setup callback
        results = []
        def callback(value):
            results.append(value)

        test_subject(cf_callback(callback))

        # check result
        for result, golden in zip(results, values):
            self.assertEqual(result.decode(), golden)

    def test_const_struct(self):
        from random import randint, random
        values = [
            (0, 0., 0.),
            (-1, -1., -1.),
            (1, 1., 1.),
        ] + [(randint(0, 0xffffffff), random(), random()) for _ in range(100)]

        struct_type = Type.struct([Type.int(), Type.float(), Type.double()])

        def map_constant(packed_values):
            vi, vf, vd = packed_values
            return Constant.struct([
                     Constant.int(Type.int(), vi),
                     Constant.real(Type.float(), vf),
                     Constant.real(Type.double(), vd),
                   ])

        constant_list = map(map_constant, values)

        mod, func_subject = _build_test_module_struct(Type.pointer(struct_type),
                                                      constant_list)

        # done function generation
        logging.debug(func_subject)

        # prepare execution
        ee = ExecutionEngine.new(mod)

        class c_struct_type(Structure):
            _fields_ = [ ('vi', c_uint32),
                         ('vf', c_float),
                         ('vd', c_double), ]

            def __iter__(self):
                return iter([self.vi, self.vf, self.vd])

        cf_callback = CFUNCTYPE(None, POINTER(c_struct_type))
        cf_test = CFUNCTYPE(None, cf_callback)

        test_subject = cf_test(ee.get_pointer_to_function(func_subject))

        # setup callback
        results = []
        def callback(value):
            results.append(tuple(value[0]))

        test_subject(cf_callback(callback))

        # check result
        for result, golden in zip(results, values):
            self.assertEqual(result[0], golden[0] & 0xffffffff)
            if golden[1] == 0:
                self.assertEqual(result[1], golden[1])
            else:
                self.assert_(abs(result[1]-golden[1])/golden[1] < 1e-7)
            self.assertEqual(result[2], golden[2])

    def test_const_vector(self):
        from random import randint
        randgen = lambda: randint(0, 0xffffffff)
        values = [
            (0, 0, 0, 0),
            (1, 1, 1, 1),
            (-1, -1, -1, -1),
        ] + [ (randgen(), randgen(), randgen(), randgen()) for _ in range(100) ]

        def map_constant(packed_values):
            consts = [ Constant.int(Type.int(), i) for i in packed_values ]
            return Constant.vector(consts)

        constant_list = map(map_constant, values)
        mod, func_subject = _build_test_module_array(Type.pointer(Type.int()),
                                                     constant_list)

        # done function generation
        logging.debug(func_subject)

        # prepare execution
        ee = ExecutionEngine.new(mod)

        cf_callback = CFUNCTYPE(None, POINTER(c_uint32))
        cf_test = CFUNCTYPE(None, cf_callback)

        test_subject = cf_test(ee.get_pointer_to_function(func_subject))

        # setup callback
        results = []
        def callback(value):
            results.append(tuple(value[0:4]))

        test_subject(cf_callback(callback))

        # check result
        for result, golden in zip(results, values):
            self.assertEqual(result,
                             tuple(map(lambda X: X & 0xffffffff, golden)))


if __name__ == '__main__':
    unittest.main()

