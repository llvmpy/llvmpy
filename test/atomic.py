from llvm.core import *
import unittest

test_these_orderings = list(filter(bool, map(lambda s:s.strip(),
'''
unordered
monotonic
acquire
release
acq_rel
seq_cst
'''.splitlines())))

test_these_atomic_op = list(filter(bool, map(lambda s:s.strip(),
'''
xchg
add
sub
and
nand
or
xor
max
min
umax
umin
'''.splitlines())))

class TestAtomic(unittest.TestCase):
    def test_atomic_cmpxchg(self):
        mod = Module.new('mod')
        functype = Type.function(Type.void(), [])
        func = mod.add_function(functype, name='foo')
        bb = func.append_basic_block('entry')
        bldr = Builder.new(bb)
        ptr = bldr.alloca(Type.int())

        old = bldr.load(ptr)
        new = Constant.int(Type.int(), 1234)


        for ordering in test_these_orderings:
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

        for ordering in test_these_orderings:
            inst = bldr.atomic_rmw('xchg', ptr, val, ordering)
            self.assertEqual(ordering, str(inst).split(' ')[-1])


        for op in test_these_atomic_op:
            inst = bldr.atomic_rmw(op, ptr, val, ordering)
            self.assertEqual(op, str(inst).strip().split(' ')[3])

        inst = bldr.atomic_rmw('xchg', ptr, val, ordering, crossthread=False)
        self.assertEqual('singlethread', str(inst).strip().split(' ')[-2])


        for op in test_these_atomic_op:
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

        for ordering in test_these_orderings:
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
            self.assertEqual(['fence', ordering], str(fenced).strip().split(' '))

if __name__ == '__main__':
    unittest.main()
