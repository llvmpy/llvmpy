"""
LLVM tests
"""
import os
import sys
import math
import shutil
import unittest
import subprocess
import tempfile

is_py3k = bool(sys.version_info[0] == 3)
BITS = tuple.__itemsize__ * 8

if is_py3k:
    from io import StringIO
else:
    from cStringIO import StringIO


import llvm
from llvm.core import (Module, Type, GlobalVariable, Function, Builder,
                       Constant, MetaData, MetaDataString, inline_function)
from llvm.ee import EngineBuilder
import llvm.core as lc
import llvm.passes as lp
import llvm.ee as le


tests = []

# ---------------------------------------------------------------------------

class TestAsm(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_asm(self):
        # create a module
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')

        # write it's assembly representation to a file
        asm = str(m)

        testasm_ll = os.path.join(self.tmpdir, 'testasm.ll')
        with open(testasm_ll, "w") as fout:
            fout.write(asm)

        # read it back into a module
        with open(testasm_ll) as fin:
            m2 = Module.from_assembly(fin)
            # The default `m.id` is '<string>'.
            m2.id = m.id # Copy the name from `m`

        self.assertEqual(str(m2).strip(), asm.strip())

    def test_bitcode(self):
        # create a module
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')

        # write it's assembly representation to a file
        asm = str(m)

        testasm_bc = os.path.join(self.tmpdir, 'testasm.bc')
        with open(testasm_bc, "wb") as fout:
            m.to_bitcode(fout)

        # read it back into a module
        with open(testasm_bc, "rb") as fin:
            m2 = Module.from_bitcode(fin)
            # The default `m.id` is '<string>'.
            m2.id = m.id # Copy the name from `m`

        self.assertEqual(str(m2).strip(), asm.strip())

tests.append(TestAsm)

# ---------------------------------------------------------------------------

class TestAttr(unittest.TestCase):
    def make_module(self):
        test_module = """
            define i32 @sum(i32, i32) {
            entry:
                %2 = add i32 %0, %1
                ret i32 %2
            }
        """
        return Module.from_assembly(StringIO(test_module))

    def test_align(self):
        m = self.make_module()
        f = m.get_function_named('sum')
        f.args[0].alignment = 16
        self.assert_("align 16" in str(f))
        self.assertEqual(f.args[0].alignment, 16)

tests.append(TestAttr)

# ---------------------------------------------------------------------------

class TestAtomic(unittest.TestCase):
    orderings = ['unordered', 'monotonic', 'acquire',
                 'release', 'acq_rel', 'seq_cst']

    atomic_op = ['xchg', 'add', 'sub', 'and', 'nand', 'or', 'xor',
                 'max', 'min', 'umax', 'umin']

    def test_atomic_cmpxchg(self):
        mod = Module.new('mod')
        functype = Type.function(Type.void(), [])
        func = mod.add_function(functype, name='foo')
        bb = func.append_basic_block('entry')
        bldr = Builder.new(bb)
        ptr = bldr.alloca(Type.int())

        old = bldr.load(ptr)
        new = Constant.int(Type.int(), 1234)

        for ordering in self.orderings:
            inst = bldr.atomic_cmpxchg(ptr, old, new, ordering)
            self.assertEqual(ordering, str(inst).strip().split(' ')[-1])

        inst = bldr.atomic_cmpxchg(ptr, old, new, ordering, crossthread=False)
        self.assertEqual('singlethread', str(inst).strip().split(' ')[-2])

    def test_atomic_rmw(self):
        mod = Module.new('mod')
        functype = Type.function(Type.void(), [])
        func = mod.add_function(functype, name='foo')
        bb = func.append_basic_block('entry')
        bldr = Builder.new(bb)
        ptr = bldr.alloca(Type.int())

        old = bldr.load(ptr)
        val = Constant.int(Type.int(), 1234)

        for ordering in self.orderings:
            inst = bldr.atomic_rmw('xchg', ptr, val, ordering)
            self.assertEqual(ordering, str(inst).split(' ')[-1])

        for op in self.atomic_op:
            inst = bldr.atomic_rmw(op, ptr, val, ordering)
            self.assertEqual(op, str(inst).strip().split(' ')[3])

        inst = bldr.atomic_rmw('xchg', ptr, val, ordering, crossthread=False)
        self.assertEqual('singlethread', str(inst).strip().split(' ')[-2])

        for op in self.atomic_op:
            atomic_op = getattr(bldr, 'atomic_%s' % op)
            inst = atomic_op(ptr, val, ordering)
            self.assertEqual(op, str(inst).strip().split(' ')[3])

    def test_atomic_ldst(self):
        mod = Module.new('mod')
        functype = Type.function(Type.void(), [])
        func = mod.add_function(functype, name='foo')
        bb = func.append_basic_block('entry')
        bldr = Builder.new(bb)
        ptr = bldr.alloca(Type.int())

        val = Constant.int(Type.int(), 1234)

        for ordering in self.orderings:
            loaded = bldr.atomic_load(ptr, ordering)
            self.assert_('load atomic' in str(loaded))
            self.assertEqual(ordering,
                             str(loaded).strip().split(' ')[-3].rstrip(','))
            self.assert_('align 1' in str(loaded))

            stored = bldr.atomic_store(loaded, ptr, ordering)
            self.assert_('store atomic' in str(stored))
            self.assertEqual(ordering,
                             str(stored).strip().split(' ')[-3].rstrip(','))
            self.assert_('align 1' in str(stored))

            fenced = bldr.fence(ordering)
            self.assertEqual(['fence', ordering],
                             str(fenced).strip().split(' '))

tests.append(TestAtomic)

# ---------------------------------------------------------------------------

class TestConstExpr(unittest.TestCase):

    def test_constexpr_opcode(self):
        mod = Module.new('test_constexpr_opcode')
        func = mod.add_function(Type.function(Type.void(), []), name="foo")
        builder = Builder.new(func.append_basic_block('entry'))
        a = builder.inttoptr(Constant.int(Type.int(), 123),
                             Type.pointer(Type.int()))
        self.assertTrue(isinstance(a, lc.ConstantExpr))
        self.assertEqual(a.opcode, lc.OPCODE_INTTOPTR)
        self.assertEqual(a.opcode_name, "inttoptr")

tests.append(TestConstExpr)

# ---------------------------------------------------------------------------

class TestOperands(unittest.TestCase):
    # implement a test function
    test_module = """
define i32 @prod(i32, i32) {
entry:
        %2 = mul i32 %0, %1
        ret i32 %2
}

define i32 @test_func(i32, i32, i32) {
entry:
        %tmp1 = call i32 @prod(i32 %0, i32 %1)
        %tmp2 = add i32 %tmp1, %2
        %tmp3 = add i32 %tmp2, 1
        %tmp4 = add i32 %tmp3, -1
        %tmp5 = add i64 -81985529216486895, 12297829382473034410
        ret i32 %tmp4
}
"""
    def test_operands(self):
        m = Module.from_assembly(StringIO(self.test_module))

        test_func = m.get_function_named("test_func")
        prod = m.get_function_named("prod")

        # test operands
        i1 = test_func.basic_blocks[0].instructions[0]
        i2 = test_func.basic_blocks[0].instructions[1]
        i3 = test_func.basic_blocks[0].instructions[2]
        i4 = test_func.basic_blocks[0].instructions[3]
        i5 = test_func.basic_blocks[0].instructions[4]

        self.assertEqual(i1.operand_count, 3)
        self.assertEqual(i2.operand_count, 2)

        self.assertEqual(i3.operands[1].z_ext_value, 1)
        self.assertEqual(i3.operands[1].s_ext_value, 1)
        self.assertEqual(i4.operands[1].z_ext_value, 0xffffffff)
        self.assertEqual(i4.operands[1].s_ext_value, -1)
        self.assertEqual(i5.operands[0].s_ext_value, -81985529216486895)
        self.assertEqual(i5.operands[1].z_ext_value, 12297829382473034410)

        self.assert_(i1.operands[-1] is prod)
        self.assert_(i1.operands[0] is test_func.args[0])
        self.assert_(i1.operands[1] is test_func.args[1])
        self.assert_(i2.operands[0] is i1)
        self.assert_(i2.operands[1] is test_func.args[2])
        self.assertEqual(len(i1.operands), 3)
        self.assertEqual(len(i2.operands), 2)

        self.assert_(i1.called_function is prod)

tests.append(TestOperands)

# ---------------------------------------------------------------------------

class TestPasses(unittest.TestCase):
    # Create a module.
    asm = """

define i32 @test() nounwind {
    ret i32 42
}

define i32 @test1() nounwind  {
entry:
        %tmp = alloca i32
        store i32 42, i32* %tmp, align 4
        %tmp1 = load i32* %tmp, align 4
        %tmp2 = call i32 @test()
        %tmp3 = load i32* %tmp, align 4
        %tmp4 = load i32* %tmp, align 4
    ret i32 %tmp1
}

define i32 @test2() nounwind  {
entry:
        %tmp = call i32 @test()
    ret i32 %tmp
}
"""
    def test_passes(self):
        m = Module.from_assembly(StringIO(self.asm))

        fn_test1 = m.get_function_named('test1')
        fn_test2 = m.get_function_named('test2')

        original_test1 = str(fn_test1)
        original_test2 = str(fn_test2)

        # Let's run a module-level inlining pass. First, create a pass manager.
        pm = lp.PassManager.new()

        # Add the target data as the first "pass". This is mandatory.
        pm.add(le.TargetData.new(''))

        # Add the inlining pass.
        pm.add(lp.PASS_INLINE)

        # Run it!
        pm.run(m)

        # Done with the pass manager.
        del pm

        # Make sure test2 is inlined
        self.assertNotEqual(str(fn_test2).strip(), original_test2.strip())

        bb_entry = fn_test2.basic_blocks[0]

        self.assertEqual(len(bb_entry.instructions), 1)
        self.assertEqual(bb_entry.instructions[0].opcode_name, 'ret')

        # Let's run a DCE pass on the the function 'test1' now. First create a
        # function pass manager.
        fpm = lp.FunctionPassManager.new(m)

        # Add the target data as first "pass". This is mandatory.
        fpm.add(le.TargetData.new(''))

        # Add a DCE pass
        fpm.add(lp.PASS_ADCE)

        # Run the pass on the function 'test1'
        fpm.run(m.get_function_named('test1'))

        # Make sure test1 is modified
        self.assertNotEqual(str(fn_test1).strip(), original_test1.strip())

    def test_passes_with_pmb(self):
        m = Module.from_assembly(StringIO(self.asm))

        fn_test1 = m.get_function_named('test1')
        fn_test2 = m.get_function_named('test2')

        original_test1 = str(fn_test1)
        original_test2 = str(fn_test2)

        # Try out the PassManagerBuilder

        pmb = lp.PassManagerBuilder.new()

        self.assertEqual(pmb.opt_level, 2)  # ensure default is level 2
        pmb.opt_level = 3
        self.assertEqual(pmb.opt_level, 3) # make sure it works

        self.assertEqual(pmb.size_level, 0) # ensure default is level 0
        pmb.size_level = 2
        self.assertEqual(pmb.size_level, 2) # make sure it works

        self.assertFalse(pmb.vectorize) # ensure default is False
        pmb.vectorize = True
        self.assertTrue(pmb.vectorize) # make sure it works

        # make sure the default is False
        self.assertFalse(pmb.disable_unit_at_a_time)
        self.assertFalse(pmb.disable_unroll_loops)
        self.assertFalse(pmb.disable_simplify_lib_calls)

        # Do function pass
        fpm = lp.FunctionPassManager.new(m)
        pmb.populate(fpm)
        fpm.run(fn_test1)

        # Make sure test1 has changed
        self.assertNotEqual(str(fn_test1).strip(), original_test1.strip())

        # Do module pass
        pm = lp.PassManager.new()
        pmb.populate(pm)
        pm.run(m)

        # Make sure test2 has changed
        self.assertNotEqual(str(fn_test2).strip(), original_test2.strip())

    def test_dump_passes(self):
        self.assertTrue(len(lp.PASSES)>0, msg="Cannot have no passes")

tests.append(TestPasses)

# ---------------------------------------------------------------------------

class TestEngineBuilder(unittest.TestCase):

    def make_test_module(self):
        module = Module.new("testmodule")
        fnty = Type.function(Type.int(), [])
        function = module.add_function(fnty, 'foo')
        bb_entry = function.append_basic_block('entry')
        builder = Builder.new(bb_entry)
        builder.ret(Constant.int(Type.int(), 0xcafe))
        module.verify()
        return module

    def run_foo(self, ee, module):
        function = module.get_function_named('foo')
        retval = ee.run_function(function, [])
        self.assertEqual(retval.as_int(), 0xcafe)


    def test_enginebuilder_basic(self):
        module = self.make_test_module()
        ee = EngineBuilder.new(module).create()

        with self.assertRaises(llvm.LLVMException):
            # Ensure the module is owned.
            llvm._util.check_is_unowned(module)

        self.run_foo(ee, module)


    def test_enginebuilder_with_tm(self):
        tm = le.TargetMachine.new()
        module = self.make_test_module()
        ee = EngineBuilder.new(module).create(tm)

        with self.assertRaises(llvm.LLVMException):
            # Ensure the targetmachine is owned.
            llvm._util.check_is_unowned(tm)
        

        with self.assertRaises(llvm.LLVMException):
            # Ensure the module is owned.
            llvm._util.check_is_unowned(module)

        self.run_foo(ee, module)

    def test_enginebuilder_force_jit(self):
        module = self.make_test_module()
        ee = EngineBuilder.new(module).force_jit().create()

        self.run_foo(ee, module)

    def test_enginebuilder_force_interpreter(self):
        module = self.make_test_module()
        ee = EngineBuilder.new(module).force_interpreter().create()

        self.run_foo(ee, module)

    def test_enginebuilder_opt(self):
        module = self.make_test_module()
        ee = EngineBuilder.new(module).opt(3).create()

        self.run_foo(ee, module)

tests.append(TestEngineBuilder)

# ---------------------------------------------------------------------------

class TestExecutionEngine(unittest.TestCase):
    def test_get_pointer_to_global(self):
        module = lc.Module.new(str(self))
        gvar = module.add_global_variable(Type.int(), 'hello')
        X = 1234
        gvar.initializer = lc.Constant.int(Type.int(), X)

        ee = le.ExecutionEngine.new(module)
        ptr = ee.get_pointer_to_global(gvar)
        from ctypes import c_void_p, cast, c_int, POINTER
        casted = cast(c_void_p(ptr), POINTER(c_int))
        self.assertEqual(X, casted[0])

    def test_add_global_mapping(self):
        module = lc.Module.new(str(self))
        gvar = module.add_global_variable(Type.int(), 'hello')

        fnty = lc.Type.function(Type.int(), [])
        foo = module.add_function(fnty, name='foo')
        bldr = lc.Builder.new(foo.append_basic_block('entry'))
        bldr.ret(bldr.load(gvar))

        ee = le.ExecutionEngine.new(module)
        from ctypes import c_int, addressof, CFUNCTYPE
        value = 0xABCD
        value_ctype = c_int(value)
        value_pointer = addressof(value_ctype)

        ee.add_global_mapping(gvar, value_pointer)

        foo_addr = ee.get_pointer_to_function(foo)
        prototype = CFUNCTYPE(c_int)
        foo_callable = prototype(foo_addr)
        self.assertEqual(foo_callable(), value)



tests.append(TestExecutionEngine)
# ---------------------------------------------------------------------------

class TestObjCache(unittest.TestCase):

    def test_objcache(self):
        # Testing module aliasing
        m1 = Module.new('a')
        t = Type.int()
        ft = Type.function(t, [t])
        f1 = m1.add_function(ft, "func")
        m2 = f1.module
        self.assert_(m1 is m2)

        # Testing global vairable aliasing 1
        gv1 = GlobalVariable.new(m1, t, "gv")
        gv2 = GlobalVariable.get(m1, "gv")
        self.assert_(gv1 is gv2)

        # Testing global vairable aliasing 2
        gv3 = m1.global_variables[0]
        self.assert_(gv1 is gv3)

        # Testing global vairable aliasing 3
        gv2 = None
        gv3 = None

        gv1.delete()
        gv4 = GlobalVariable.new(m1, t, "gv")

        self.assert_(gv1 is not gv4)

        # Testing function aliasing 1
        b1 = f1.append_basic_block('entry')
        f2 = b1.function
        self.assert_(f1 is f2)

        # Testing function aliasing 2
        f3 = m1.get_function_named("func")
        self.assert_(f1 is f3)

        # Testing function aliasing 3
        f4 = Function.get_or_insert(m1, ft, "func")
        self.assert_(f1 is f4)

        # Testing function aliasing 4
        f5 = Function.get(m1, "func")
        self.assert_(f1 is f5)

        # Testing function aliasing 5
        f6 = m1.get_or_insert_function(ft, "func")
        self.assert_(f1 is f6)

        # Testing function aliasing 6
        f7 = m1.functions[0]
        self.assert_(f1 is f7)

        # Testing argument aliasing
        a1 = f1.args[0]
        a2 = f1.args[0]
        self.assert_(a1 is a2)

        # Testing basic block aliasing 1
        b2 = f1.basic_blocks[0]
        self.assert_(b1 is b2)

        # Testing basic block aliasing 2
        b3 = f1.get_entry_basic_block()
        self.assert_(b1 is b3)

        # Testing basic block aliasing 3
        b31 = f1.entry_basic_block
        self.assert_(b1 is b31)

        # Testing basic block aliasing 4
        bldr = Builder.new(b1)
        b4 = bldr.basic_block
        self.assert_(b1 is b4)

        # Testing basic block aliasing 5
        i1 = bldr.ret_void()
        b5 = i1.basic_block
        self.assert_(b1 is b5)

        # Testing instruction aliasing 1
        i2 = b5.instructions[0]
        self.assert_(i1 is i2)

        # phi node
        phi = bldr.phi(t)
        phi.add_incoming(f1.args[0], b1)
        v2 = phi.get_incoming_value(0)
        b6 = phi.get_incoming_block(0)

        # Testing PHI / basic block aliasing 5
        self.assert_(b1 is b6)

        # Testing PHI / value aliasing
        self.assert_(f1.args[0] is v2)

tests.append(TestObjCache)

# ---------------------------------------------------------------------------

class TestTargetMachines(unittest.TestCase):
    '''Exercise target machines

    Require PTX backend
    '''
    def test_native(self):
        m, _ = self._build_module()
        tm = le.EngineBuilder.new(m).select_target()

        self.assertTrue(tm.target_name)
        self.assertTrue(tm.target_data)
        self.assertTrue(tm.target_short_description)
        self.assertTrue(tm.triple)
        self.assertIn('foo', tm.emit_assembly(m).decode('utf-8'))
        self.assertTrue(le.get_host_cpu_name())

    def test_ptx(self):
        if lc.HAS_PTX:
            arch = 'ptx64'
        elif lc.HAS_NVPTX:
            arch = 'nvptx64'
        else:
            return # skip this test
        m, func = self._build_module()
        func.calling_convention = lc.CC_PTX_KERNEL # set calling conv
        ptxtm = le.TargetMachine.lookup(arch=arch, cpu='compute_20')
        self.assertTrue(ptxtm.triple)
        self.assertTrue(ptxtm.cpu)
        ptxasm = ptxtm.emit_assembly(m).decode('utf-8')
        self.assertIn('foo', ptxasm)
        if lc.HAS_NVPTX:
            self.assertIn('.address_size 64', ptxasm)
        self.assertIn('compute_20', ptxasm)

    def _build_module(self):
        m = Module.new('TestTargetMachines')

        fnty = Type.function(Type.void(), [])
        func = m.add_function(fnty, name='foo')

        bldr = Builder.new(func.append_basic_block('entry'))
        bldr.ret_void()
        m.verify()
        return m, func

    def _build_bad_archname(self):
        with self.assertRaises(RuntimeError):
            tm = TargetMachine.lookup("ain't no arch name")

tests.append(TestTargetMachines)

# ---------------------------------------------------------------------------

class TestNative(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def _make_module(self):
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')

        fty = Type.function(Type.int(), [])
        f = m.add_function(fty, name='main')

        bldr = Builder.new(f.append_basic_block('entry'))
        bldr.ret(Constant.int(Type.int(), 0xab))

        return m

    def _compile(self, src):
        dst = os.path.join(self.tmpdir, 'llvmobj.out')
        s = subprocess.call(['cc', '-o', dst, src])
        if s != 0:
            raise Exception("Cannot compile")

        s = subprocess.call([dst])
        self.assertEqual(s, 0xab)

    def test_assembly(self):
        if sys.platform == 'darwin':
            # skip this test on MacOSX for now
            return

        m = self._make_module()
        output = m.to_native_assembly()

        src = os.path.join(self.tmpdir, 'llvmasm.s')
        with open(src, 'wb') as fout:
            fout.write(output)

        self._compile(src)

    def test_object(self):
        if sys.platform == 'darwin':
            # skip this test on MacOSX for now
            return

        m = self._make_module()
        output = m.to_native_object()

        src = os.path.join(self.tmpdir, 'llvmobj.o')
        with open(src, 'wb') as fout:
            fout.write(output)

        self._compile(src)

if sys.platform != 'win32':
    tests.append(TestNative)

# ---------------------------------------------------------------------------

class TestNativeAsm(unittest.TestCase):

    def test_asm(self):
        m = Module.new('module1')

        foo = m.add_function(Type.function(Type.int(),
                                           [Type.int(), Type.int()]),
                             name="foo")
        bldr = Builder.new(foo.append_basic_block('entry'))
        x = bldr.add(foo.args[0], foo.args[1])
        bldr.ret(x)

        att_syntax = m.to_native_assembly()
        os.environ["LLVMPY_OPTIONS"] = "-x86-asm-syntax=intel"
        lc.parse_environment_options(sys.argv[0], "LLVMPY_OPTIONS")
        intel_syntax = m.to_native_assembly()

        self.assertNotEqual(att_syntax, intel_syntax)

tests.append(TestNativeAsm)

# ---------------------------------------------------------------------------

class TestUses(unittest.TestCase):

    def test_uses(self):
        m = Module.new('a')
        t = Type.int()
        ft = Type.function(t, [t, t, t])
        f = m.add_function(ft, "func")
        b = f.append_basic_block('entry')
        bld = Builder.new(b)
        tmp1 = bld.add(Constant.int(t, 100), f.args[0], "tmp1")
        tmp2 = bld.add(tmp1, f.args[1], "tmp2")
        tmp3 = bld.add(tmp1, f.args[2], "tmp3")
        bld.ret(tmp3)

        # Testing use count
        self.assertEqual(f.args[0].use_count, 1)
        self.assertEqual(f.args[1].use_count, 1)
        self.assertEqual(f.args[2].use_count, 1)
        self.assertEqual(tmp1.use_count, 2)
        self.assertEqual(tmp2.use_count, 0)
        self.assertEqual(tmp3.use_count, 1)

        # Testing uses
        self.assert_(f.args[0].uses[0] is tmp1)
        self.assertEqual(len(f.args[0].uses), 1)
        self.assert_(f.args[1].uses[0] is tmp2)
        self.assertEqual(len(f.args[1].uses), 1)
        self.assert_(f.args[2].uses[0] is tmp3)
        self.assertEqual(len(f.args[2].uses), 1)
        self.assertEqual(len(tmp1.uses), 2)
        self.assertEqual(len(tmp2.uses), 0)
        self.assertEqual(len(tmp3.uses), 1)

tests.append(TestUses)

# ---------------------------------------------------------------------------

class TestMetaData(unittest.TestCase):
    # test module metadata
    def test_metadata(self):
        m = Module.new('a')
        t = Type.int()
        metadata = MetaData.get(m, [Constant.int(t, 100),
                                    MetaDataString.get(m, 'abcdef'),
                                    None])
        MetaData.add_named_operand(m, 'foo', metadata)
        self.assertEqual(MetaData.get_named_operands(m, 'foo'), [metadata])
        self.assertEqual(MetaData.get_named_operands(m, 'bar'), [])
        self.assertEqual(len(metadata.operands), 3)
        self.assertEqual(metadata.operands[0].z_ext_value, 100)
        self.assertEqual(metadata.operands[1].string, 'abcdef')
        self.assertTrue(metadata.operands[2] is None)

tests.append(TestMetaData)

# ---------------------------------------------------------------------------

class TestInlining(unittest.TestCase):
    def test_inline_call(self):
        mod = Module.new(__name__)
        callee = mod.add_function(Type.function(Type.int(), [Type.int()]),
                                  name='bar')

        builder = Builder.new(callee.append_basic_block('entry'))
        builder.ret(builder.add(callee.args[0], callee.args[0]))

        caller = mod.add_function(Type.function(Type.int(), []),
                                  name='foo')

        builder = Builder.new(caller.append_basic_block('entry'))
        callinst = builder.call(callee, [Constant.int(Type.int(), 1234)])
        builder.ret(callinst)

        pre_inlining = str(caller)
        self.assertIn('call', pre_inlining)

        self.assertTrue(inline_function(callinst))

        post_inlining = str(caller)
        self.assertNotIn('call', post_inlining)
        self.assertIn('2468', post_inlining)

tests.append(TestInlining)

# ---------------------------------------------------------------------------

class TestIssue10(unittest.TestCase):
    def test_issue10(self):
        m = Module.new('a')
        ti = Type.int()
        tf = Type.function(ti, [ti, ti])

        f = m.add_function(tf, "func1")

        bb = f.append_basic_block('entry')

        b = Builder.new(bb)

        # There are no instructions in bb. Positioning of the
        # builder at beginning (or end) should succeed (trivially).
        b.position_at_end(bb)
        b.position_at_beginning(bb)

tests.append(TestIssue10)

# ---------------------------------------------------------------------------

class TestOpaque(unittest.TestCase):

    def test_opaque(self):
        # Create an opaque type
        ts = Type.opaque('mystruct')
        self.assertTrue('type opaque' in str(ts))
        self.assertTrue(ts.is_opaque)
        self.assertTrue(ts.is_identified)
        self.assertFalse(ts.is_literal)
        #print(ts)

        # Create a recursive type
        ts.set_body([Type.int(), Type.pointer(ts)])

        self.assertEqual(ts.elements[0], Type.int())
        self.assertEqual(ts.elements[1], Type.pointer(ts))
        self.assertEqual(ts.elements[1].pointee, ts)
        self.assertFalse(ts.is_opaque) # is not longer a opaque type
        #print(ts)

        with self.assertRaises(llvm.LLVMException):
            # Cannot redefine
            ts.set_body([])

    def test_opaque_with_no_name(self):
        with self.assertRaises(llvm.LLVMException):
            Type.opaque('')

tests.append(TestOpaque)

# ---------------------------------------------------------------------------
class TestCPUSupport(unittest.TestCase):

    def _build_test_module(self):
        mod     = Module.new('test')

        float   = Type.double()
        mysinty = Type.function( float, [float] )
        mysin   = mod.add_function(mysinty, "mysin")
        block   = mysin.append_basic_block("entry")
        b       = Builder.new(block)

        sqrt = Function.intrinsic(mod, lc.INTR_SQRT, [float])
        pow  = Function.intrinsic(mod, lc.INTR_POWI, [float])
        cos  = Function.intrinsic(mod, lc.INTR_COS,  [float])

        mysin.args[0].name = "x"
        x    = mysin.args[0]
        one  = Constant.real(float, "1")
        cosx = b.call(cos, [x], "cosx")
        cos2 = b.call(pow, [cosx, Constant.int(Type.int(), 2)], "cos2")
        onemc2 = b.fsub(one, cos2, "onemc2") # Should use fsub
        sin  = b.call(sqrt, [onemc2], "sin")
        b.ret(sin)
        return mod, mysin

    def _template(self, mattrs):
        mod, func = self._build_test_module()
        ee = self._build_engine(mod, mattrs=mattrs)

        arg = le.GenericValue.real(Type.double(), 1.234)
        retval = ee.run_function(func, [arg])
        
        golden = math.sin(1.234)
        answer = retval.as_real(Type.double())
        self.assertTrue(abs(answer-golden)/golden < 1e-5)


    def _build_engine(self, mod, mattrs):
        if mattrs:
            return EngineBuilder.new(mod).mattrs(mattrs).create()
        else:
            return EngineBuilder.new(mod).create()

    def test_cpu_support2(self):
        features = 'sse3', 'sse41', 'sse42', 'avx'
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print 'disable mattrs', mattrs
        self._template(mattrs)

    def test_cpu_support3(self):
        features = 'sse41', 'sse42', 'avx'
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print 'disable mattrs', mattrs
        self._template(mattrs)

    def test_cpu_support4(self):
        features = 'sse42', 'avx'
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print 'disable mattrs', mattrs
        self._template(mattrs)

    def test_cpu_support5(self):
        features = 'avx',
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print 'disable mattrs', mattrs
        self._template(mattrs)

    def test_cpu_support6(self):
        features = []
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print 'disable mattrs', mattrs
        self._template(mattrs)

tests.append(TestCPUSupport)

# ---------------------------------------------------------------------------
class TestIntrinsicBasic(unittest.TestCase):

    def _build_module(self, float):
        mod     = Module.new('test')
        functy  = Type.function(float, [float])
        func    = mod.add_function(functy, "mytest%s" % float)
        block   = func.append_basic_block("entry")
        b       = Builder.new(block)
        return mod, func, b

    def _template(self, mod, func, pyfunc):
        float = func.type.pointee.return_type
        ee = le.ExecutionEngine.new(mod)
        arg = le.GenericValue.real(float, 1.234)
        retval = ee.run_function(func, [arg])
        golden = pyfunc(1.234)
        answer = retval.as_real(float)
        self.assertTrue(abs(answer - golden) / golden < 1e-7)

    def test_sqrt_f32(self):
        float = Type.float()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_SQRT, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.sqrt)

    def test_sqrt_f64(self):
        float = Type.double()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_SQRT, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.sqrt)

    def test_cos_f32(self):
        if sys.platform == 'win32' and BITS == 32:
            # float32 support is known to fail on 32-bit Windows
            return
        float = Type.float()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_COS, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.cos)

    def test_cos_f64(self):
        float = Type.double()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_COS, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.cos)

    def test_sin_f32(self):
        if sys.platform == 'win32' and BITS == 32:
            # float32 support is known to fail on 32-bit Windows
            return
        float = Type.float()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_SIN, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.sin)

    def test_sin_f64(self):
        float = Type.double()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_SIN, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.sin)

    def test_powi_f32(self):
        float = Type.float()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_POWI, [float])
        b.ret(b.call(intr, [func.args[0], lc.Constant.int(Type.int(), 2)]))
        self._template(mod, func, lambda x: x**2)

    def test_powi_f64(self):
        float = Type.double()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_POWI, [float])
        b.ret(b.call(intr, [func.args[0], lc.Constant.int(Type.int(), 2)]))
        self._template(mod, func, lambda x: x**2)



tests.append(TestIntrinsicBasic)

# ---------------------------------------------------------------------------

class TestIntrinsic(unittest.TestCase):
    def test_bswap(self):
        # setup a function and a builder
        mod    = Module.new('test')
        functy = Type.function(Type.int(), [])
        func   = mod.add_function(functy, "showme")
        block  = func.append_basic_block("entry")
        b      = Builder.new(block)

        # let's do bswap on a 32-bit integer using llvm.bswap
        val   = Constant.int(Type.int(), 0x42)
        bswap = Function.intrinsic(mod, lc.INTR_BSWAP, [Type.int()])

        bswap_res = b.call(bswap, [val])
        b.ret(bswap_res)

        # logging.debug(mod)

        # the output is:
        #
        #    ; ModuleID = 'test'
        #
        #    define void @showme() {
        #    entry:
        #      %0 = call i32 @llvm.bswap.i32(i32 42)
        #      ret i32 %0
        #    }

        # let's run the function
        ee = le.ExecutionEngine.new(mod)
        retval = ee.run_function(func, [])
        self.assertEqual(retval.as_int(), 0x42000000)

    def test_mysin(self):
        if sys.platform == 'win32' and BITS == 32:
            # float32 support is known to fail on 32-bit Windows
            return

        # mysin(x) = sqrt(1.0 - pow(cos(x), 2))
        mod     = Module.new('test')

        float   = Type.float()
        mysinty = Type.function( float, [float] )
        mysin   = mod.add_function(mysinty, "mysin")
        block   = mysin.append_basic_block("entry")
        b       = Builder.new(block)

        sqrt = Function.intrinsic(mod, lc.INTR_SQRT, [float])
        pow  = Function.intrinsic(mod, lc.INTR_POWI, [float])
        cos  = Function.intrinsic(mod, lc.INTR_COS,  [float])

        mysin.args[0].name = "x"
        x    = mysin.args[0]
        one  = Constant.real(float, "1")
        cosx = b.call(cos, [x], "cosx")
        cos2 = b.call(pow, [cosx, Constant.int(Type.int(), 2)], "cos2")
        onemc2 = b.fsub(one, cos2, "onemc2") # Should use fsub
        sin  = b.call(sqrt, [onemc2], "sin")
        b.ret(sin)
        #logging.debug(mod)

#   ; ModuleID = 'test'
#
#   define void @showme() {
#   entry:
#       call i32 @llvm.bswap.i32( i32 42 )              ; <i32>:0 [#uses
#   }
#
#   declare i32 @llvm.bswap.i32(i32) nounwind readnone
#
#   define float @mysin(float %x) {
#   entry:
#       %cosx = call float @llvm.cos.f32( float %x )            ; <float
#       %cos2 = call float @llvm.powi.f32( float %cosx, i32 2 )
#       %onemc2 = sub float 1.000000e+00, %cos2         ; <float> [#uses
#       %sin = call float @llvm.sqrt.f32( float %onemc2 )
#       ret float %sin
#   }
#
#   declare float @llvm.sqrt.f32(float) nounwind readnone
#
#   declare float @llvm.powi.f32(float, i32) nounwind readnone
#
#   declare float @llvm.cos.f32(float) nounwind readnone

        # let's run the function
        ee = le.ExecutionEngine.new(mod)
        arg = le.GenericValue.real(Type.float(), 1.234)
        retval = ee.run_function(mysin, [arg])

        golden = math.sin(1.234)
        answer = retval.as_real(Type.float())
        self.assertTrue(abs(answer-golden)/golden < 1e-5)

tests.append(TestIntrinsic)

# ---------------------------------------------------------------------------

class TestVolatile(unittest.TestCase):

    def test_volatile(self):
        mod = Module.new('mod')
        functype = Type.function(Type.void(), [])
        func = mod.add_function(functype, name='foo')
        bb = func.append_basic_block('entry')
        bldr = Builder.new(bb)
        ptr = bldr.alloca(Type.int())

        # test load inst
        val = bldr.load(ptr)
        self.assertFalse(val.is_volatile, "default must be non-volatile")
        val.set_volatile(True)
        self.assertTrue(val.is_volatile, "fail to set volatile")
        val.set_volatile(False)
        self.assertFalse(val.is_volatile, "fail to unset volatile")

        # test store inst
        store_inst = bldr.store(val, ptr)
        self.assertFalse(store_inst.is_volatile, "default must be non-volatile")
        store_inst.set_volatile(True)
        self.assertTrue(store_inst.is_volatile, "fail to set volatile")
        store_inst.set_volatile(False)
        self.assertFalse(store_inst.is_volatile, "fail to unset volatile")

    def test_volatile_another(self):
        mod = Module.new('mod')
        functype = Type.function(Type.void(), [])
        func = mod.add_function(functype, name='foo')
        bb = func.append_basic_block('entry')
        bldr = Builder.new(bb)
        ptr = bldr.alloca(Type.int())

        # test load inst
        val = bldr.load(ptr, volatile=True)
        self.assertTrue(val.is_volatile, "volatile kwarg does not work")
        val.set_volatile(False)
        self.assertFalse(val.is_volatile, "fail to unset volatile")
        val.set_volatile(True)
        self.assertTrue(val.is_volatile, "fail to set volatile")

        # test store inst
        store_inst = bldr.store(val, ptr, volatile=True)
        self.assertTrue(store_inst.is_volatile, "volatile kwarg does not work")
        store_inst.set_volatile(False)
        self.assertFalse(store_inst.is_volatile, "fail to unset volatile")
        store_inst.set_volatile(True)
        self.assertTrue(store_inst.is_volatile, "fail to set volatile")

tests.append(TestVolatile)

# ---------------------------------------------------------------------------

class TestNamedMetaData(unittest.TestCase):
    def test_named_md(self):
        m = Module.new('test_named_md')
        nmd = m.get_or_insert_named_metadata('something')
        md = MetaData.get(m, [Constant.int(Type.int(), 0xbeef)])
        nmd.add(md)
        self.assertTrue(str(nmd).startswith('!something'))
        ir = str(m)
        self.assertTrue('!something' in ir)

tests.append(TestNamedMetaData)

# ---------------------------------------------------------------------------

def run(verbosity=1):
    print('llvmpy is installed in: ' + os.path.dirname(__file__))
    print('llvmpy version: ' + llvm.__version__)
    print(sys.version)

    suite = unittest.TestSuite()
    for cls in tests:
        suite.addTest(unittest.makeSuite(cls))

    # The default stream fails in IPython qtconsole on Windows,
    # so just using sys.stdout
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    return runner.run(suite)


if __name__ == '__main__':
    run()
