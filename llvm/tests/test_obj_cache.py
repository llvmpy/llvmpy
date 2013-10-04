import unittest
from llvm.core import Module, Type, GlobalVariable, Function, Builder
from .support import TestCase, tests

class TestObjCache(TestCase):

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
        b3 = f1.entry_basic_block
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

if __name__ == '__main__':
    unittest.main()

