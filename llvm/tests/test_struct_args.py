from __future__ import print_function
from . import tests
import sys
import unittest
from ctypes import Structure, c_float, c_double, c_uint8, CFUNCTYPE
from llvm import core as lc
from llvm import ee as le

from .support import (skip_if_win32, skip_if_not_win32, skip_if_not_32bits,
                      skip_if_not_64bits, skip_if_not_intel_cpu, TestCase)

class TwoDoubleOneByte(Structure):
    _fields_ = ('x', c_double), ('y', c_double), ('z', c_uint8)

    def __repr__(self):
        return '<x=%f y=%f z=%d>' % (self.x, self.y, self.z)

class TwoDouble(Structure):
    _fields_ = ('x', c_double), ('y', c_double)

    def __repr__(self):
        return '<x=%f y=%f>' % (self.x, self.y)

class TwoFloat(Structure):
    _fields_ = ('x', c_float), ('y', c_float)

    def __repr__(self):
        return '<x=%f y=%f>' % (self.x, self.y)

class OneByte(Structure):
    _fields_ = [('x', c_uint8)]

    def __repr__(self):
        return '<x=%d>' % (self.x,)

@skip_if_not_intel_cpu
@skip_if_win32
class TestStructSystemVABI(TestCase):
    '''
    Non microsoft convention
    '''

    #----------------------------------------------------------------------
    # 64 bits

    @skip_if_not_64bits
    def test_bigger_than_two_words_64(self):
        m = lc.Module.new('test_struct_arg')

        double_type = lc.Type.double()
        uint8_type = lc.Type.int(8)
        struct_type = lc.Type.struct([double_type, double_type, uint8_type])
        struct_ptr_type = lc.Type.pointer(struct_type)
        func_type = lc.Type.function(lc.Type.void(),
                                     [struct_ptr_type, struct_ptr_type])
        func = m.add_function(func_type, name='foo')

        # return value pointer
        func.args[0].add_attribute(lc.ATTR_STRUCT_RET)

        # pass structure by value
        func.args[1].add_attribute(lc.ATTR_BY_VAL)

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = builder.load(func.args[1])
        e1, e2, e3 = [builder.extract_value(arg, i) for i in range(3)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)
        ret = builder.insert_value(ret, e3, 2)
        builder.store(ret, func.args[0])
        builder.ret_void()

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoDoubleOneByte, TwoDoubleOneByte)
        cfunc = cfunctype(ptr)

        arg = TwoDoubleOneByte(x=1.321321, y=6.54352, z=128)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)
        self.assertEqual(arg.z, ret.z)

    @skip_if_not_64bits
    def test_just_two_words_64(self):
        m = lc.Module.new('test_struct_arg')

        double_type = lc.Type.double()
        struct_type = lc.Type.struct([double_type, double_type])
        func_type = lc.Type.function(struct_type, [struct_type])
        func = m.add_function(func_type, name='foo')

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = func.args[0]
        e1, e2 = [builder.extract_value(arg, i) for i in range(2)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)
        builder.ret(ret)

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoDouble, TwoDouble)
        cfunc = cfunctype(ptr)

        arg = TwoDouble(x=1.321321, y=6.54352)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)

    @skip_if_not_64bits
    def test_two_halfwords(self):
        '''Arguments smaller or equal to a word is packed into a word.

        Passing as struct { float, float } occupies two XMM registers instead
        of one.
        The output must be in XMM.
        '''
        m = lc.Module.new('test_struct_arg')

        float_type = lc.Type.float()
        struct_type = lc.Type.vector(float_type, 2)
        func_type = lc.Type.function(struct_type, [struct_type])
        func = m.add_function(func_type, name='foo')

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = func.args[0]
        constint = lambda x: lc.Constant.int(lc.Type.int(), x)
        e1, e2 = [builder.extract_element(arg, constint(i))
                  for i in range(2)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_element(lc.Constant.undef(struct_type), se1,
                                     constint(0))
        ret = builder.insert_element(ret, se2, constint(1))
        builder.ret(ret)

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoFloat, TwoFloat)
        cfunc = cfunctype(ptr)

        arg = TwoFloat(x=1.321321, y=6.54352)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)

    #----------------------------------------------------------------------
    # 32 bits

    @skip_if_not_32bits
    def test_structure_abi_32_1(self):
        '''x86 is simple.  Always pass structure as memory.
        '''
        m = lc.Module.new('test_struct_arg')

        double_type = lc.Type.double()
        uint8_type = lc.Type.int(8)
        struct_type = lc.Type.struct([double_type, double_type, uint8_type])
        struct_ptr_type = lc.Type.pointer(struct_type)
        func_type = lc.Type.function(lc.Type.void(),
                                     [struct_ptr_type, struct_ptr_type])
        func = m.add_function(func_type, name='foo')

        # return value pointer
        func.args[0].add_attribute(lc.ATTR_STRUCT_RET)

        # pass structure by value
        func.args[1].add_attribute(lc.ATTR_BY_VAL)

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = builder.load(func.args[1])
        e1, e2, e3 = [builder.extract_value(arg, i) for i in range(3)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)
        ret = builder.insert_value(ret, e3, 2)
        builder.store(ret, func.args[0])
        builder.ret_void()

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoDoubleOneByte, TwoDoubleOneByte)
        cfunc = cfunctype(ptr)

        arg = TwoDoubleOneByte(x=1.321321, y=6.54352, z=128)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)
        self.assertEqual(arg.z, ret.z)


    @skip_if_not_32bits
    def test_structure_abi_32_2(self):
        '''x86 is simple.  Always pass structure as memory.
        '''
        m = lc.Module.new('test_struct_arg')

        float_type = lc.Type.float()
        struct_type = lc.Type.struct([float_type, float_type])
        struct_ptr_type = lc.Type.pointer(struct_type)
        func_type = lc.Type.function(lc.Type.void(),
                                     [struct_ptr_type, struct_ptr_type])
        func = m.add_function(func_type, name='foo')

        # return value pointer
        func.args[0].add_attribute(lc.ATTR_STRUCT_RET)

        # pass structure by value
        func.args[1].add_attribute(lc.ATTR_BY_VAL)

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = builder.load(func.args[1])
        e1, e2 = [builder.extract_value(arg, i) for i in range(2)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)
        builder.store(ret, func.args[0])
        builder.ret_void()

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoFloat, TwoFloat)
        cfunc = cfunctype(ptr)

        arg = TwoFloat(x=1.321321, y=6.54352)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)


    @skip_if_not_32bits
    def test_structure_abi_32_3(self):
        '''x86 is simple.  Always pass structure as memory.
        '''
        m = lc.Module.new('test_struct_arg')

        uint8_type = lc.Type.int(8)
        struct_type = lc.Type.struct([uint8_type])
        struct_ptr_type = lc.Type.pointer(struct_type)
        func_type = lc.Type.function(lc.Type.void(),
                                     [struct_ptr_type, struct_ptr_type])
        func = m.add_function(func_type, name='foo')

        # return value pointer
        func.args[0].add_attribute(lc.ATTR_STRUCT_RET)

        # pass structure by value
        func.args[1].add_attribute(lc.ATTR_BY_VAL)

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = builder.load(func.args[1])
        e1 = builder.extract_value(arg, 0)
        se1 = builder.mul(e1, e1)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        builder.store(ret, func.args[0])
        builder.ret_void()

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(OneByte, OneByte)
        cfunc = cfunctype(ptr)

        arg = OneByte(x=8)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertEqual(arg.x * arg.x, ret.x)

tests.append(TestStructSystemVABI)

@skip_if_not_intel_cpu
@skip_if_not_win32
class TestStructMicrosoftABI(TestCase):
    '''
    Microsoft convention
    '''

    #----------------------------------------------------------------------
    # 64 bits

    @skip_if_not_64bits
    def test_bigger_than_two_words_64(self):
        m = lc.Module.new('test_struct_arg')

        double_type = lc.Type.double()
        uint8_type = lc.Type.int(8)
        struct_type = lc.Type.struct([double_type, double_type, uint8_type])
        struct_ptr_type = lc.Type.pointer(struct_type)
        func_type = lc.Type.function(lc.Type.void(),
                                     [struct_ptr_type, struct_ptr_type])
        func = m.add_function(func_type, name='foo')

        # return value pointer
        func.args[0].add_attribute(lc.ATTR_STRUCT_RET)

        # pass structure by value
        func.args[1].add_attribute(lc.ATTR_BY_VAL)

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = builder.load(func.args[1])
        e1, e2, e3 = [builder.extract_value(arg, i) for i in range(3)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)
        ret = builder.insert_value(ret, e3, 2)
        builder.store(ret, func.args[0])
        builder.ret_void()

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoDoubleOneByte, TwoDoubleOneByte)
        cfunc = cfunctype(ptr)

        arg = TwoDoubleOneByte(x=1.321321, y=6.54352, z=128)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)
        self.assertEqual(arg.z, ret.z)

    @skip_if_not_64bits
    def test_just_two_words_64(self):
        m = lc.Module.new('test_struct_arg')

        double_type = lc.Type.double()
        struct_type = lc.Type.struct([double_type, double_type])
        struct_ptr_type = lc.Type.pointer(struct_type)
        func_type = lc.Type.function(lc.Type.void(),
                                     [struct_ptr_type, struct_ptr_type])
        func = m.add_function(func_type, name='foo')

        # return value pointer
        func.args[0].add_attribute(lc.ATTR_STRUCT_RET)

        # pass structure by value
        func.args[1].add_attribute(lc.ATTR_BY_VAL)

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = builder.load(func.args[1])
        e1, e2 = [builder.extract_value(arg, i) for i in range(2)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)
        builder.store(ret, func.args[0])
        builder.ret_void()

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoDouble, TwoDouble)
        cfunc = cfunctype(ptr)

        arg = TwoDouble(x=1.321321, y=6.54352)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)

    @skip_if_not_64bits
    def test_two_halfwords(self):
        '''Arguments smaller or equal to a word is packed into a word.

        Floats structure are not passed on the XMM.
        Treat it as a i64.
        '''
        m = lc.Module.new('test_struct_arg')

        float_type = lc.Type.float()
        struct_type = lc.Type.struct([float_type, float_type])
        abi_type = lc.Type.int(64)

        func_type = lc.Type.function(abi_type, [abi_type])
        func = m.add_function(func_type, name='foo')

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = func.args[0]

        struct_ptr = builder.alloca(struct_type)
        struct_int_ptr = builder.bitcast(struct_ptr, lc.Type.pointer(abi_type))
        builder.store(arg, struct_int_ptr)

        arg = builder.load(struct_ptr)

        e1, e2 = [builder.extract_value(arg, i) for i in range(2)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)

        builder.store(ret, struct_ptr)
        ret = builder.load(struct_int_ptr)

        builder.ret(ret)

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoFloat, TwoFloat)
        cfunc = cfunctype(ptr)

        arg = TwoFloat(x=1.321321, y=6.54352)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)

    #----------------------------------------------------------------------
    # 32 bits

    @skip_if_not_32bits
    def test_one_word_register(self):
        '''Argument is passed by memory.
        Return value is passed by register.
        '''
        m = lc.Module.new('test_struct_arg')

        uint8_type = lc.Type.int(8)
        struct_type = lc.Type.struct([uint8_type])
        struct_ptr_type = lc.Type.pointer(struct_type)
        func_type = lc.Type.function(struct_type, [struct_ptr_type])
        func = m.add_function(func_type, name='foo')

        # pass structure by value
        func.args[0].add_attribute(lc.ATTR_BY_VAL)

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = builder.load(func.args[0])
        e1 = builder.extract_value(arg, 0)
        se1 = builder.mul(e1, e1)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)

        builder.ret(ret)

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(OneByte, OneByte)
        cfunc = cfunctype(ptr)

        arg = OneByte(x=8)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertEqual(arg.x * arg.x, ret.x)


    @skip_if_not_32bits
    def test_two_floats(self):
        '''Argument is passed by register.
        Return in 2 registers
        '''
        m = lc.Module.new('test_struct_arg')

        float_type = lc.Type.float()
        struct_type = lc.Type.struct([float_type, float_type])

        abi_type = lc.Type.int(64)
        func_type = lc.Type.function(abi_type, [struct_type])
        func = m.add_function(func_type, name='foo')

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        out_ptr = builder.alloca(struct_type)

        arg = func.args[0]
        e1, e2 = [builder.extract_value(arg, i) for i in range(2)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)
        builder.store(ret, out_ptr)

        out_int_ptr = builder.bitcast(out_ptr, lc.Type.pointer(abi_type))

        builder.ret(builder.load(out_int_ptr))

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoFloat, TwoFloat)
        cfunc = cfunctype(ptr)

        arg = TwoFloat(x=1.321321, y=6.54352)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)

    @skip_if_not_32bits
    def test_bigger_than_two_words(self):
        '''Pass in memory.
        '''
        m = lc.Module.new('test_struct_arg')

        double_type = lc.Type.double()
        uint8_type = lc.Type.int(8)
        struct_type = lc.Type.struct([double_type, double_type, uint8_type])
        struct_ptr_type = lc.Type.pointer(struct_type)
        func_type = lc.Type.function(lc.Type.void(),
                                     [struct_ptr_type, struct_ptr_type])
        func = m.add_function(func_type, name='foo')

        # return value pointer
        func.args[0].add_attribute(lc.ATTR_STRUCT_RET)

        # pass structure by value
        func.args[1].add_attribute(lc.ATTR_BY_VAL)

        # define function body
        builder = lc.Builder.new(func.append_basic_block(''))

        arg = builder.load(func.args[1])
        e1, e2, e3 = [builder.extract_value(arg, i) for i in range(3)]
        se1 = builder.fmul(e1, e2)
        se2 = builder.fdiv(e1, e2)
        ret = builder.insert_value(lc.Constant.undef(struct_type), se1, 0)
        ret = builder.insert_value(ret, se2, 1)
        ret = builder.insert_value(ret, e3, 2)
        builder.store(ret, func.args[0])
        builder.ret_void()

        del builder

        # verify
        m.verify()

        print(m)
        # use with ctypes
        engine = le.EngineBuilder.new(m).create()
        ptr = engine.get_pointer_to_function(func)

        cfunctype = CFUNCTYPE(TwoDoubleOneByte, TwoDoubleOneByte)
        cfunc = cfunctype(ptr)

        arg = TwoDoubleOneByte(x=1.321321, y=6.54352, z=128)
        ret = cfunc(arg)
        print(arg)
        print(ret)

        self.assertClose(arg.x * arg.y, ret.x)
        self.assertClose(arg.x / arg.y, ret.y)
        self.assertEqual(arg.z, ret.z)

tests.append(TestStructMicrosoftABI)

if __name__ == "__main__":
    unittest.main()
