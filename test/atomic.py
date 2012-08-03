from llvm.core import *
import unittest

test_these_orderings = filter(bool, map(lambda s:s.strip(),
'''
unordered
monotonic
acquire
release
acq_rel
seq_cst
'''.splitlines()))

class TestAtomic(unittest.TestCase):
    def test_atomic(self):
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
            self.assertEqual(ordering, str(inst).split(' ')[-1])


        inst = bldr.atomic_cmpxchg(ptr, old, new, ordering, crossthread=False)
        self.assertEqual('singlethread', str(inst).split(' ')[-2])

if __name__ == '__main__':
    unittest.main()
