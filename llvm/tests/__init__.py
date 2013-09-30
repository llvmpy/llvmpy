from __future__ import print_function
import sys
import os
import unittest
import llvm

tests = []

def run(verbosity=1):
    print('llvmpy is installed in: ' + os.path.dirname(__file__))
    print('llvmpy version: ' + llvm.__version__)
    print(sys.version)

    files = filter(lambda s: s.startswith('test_') and s.endswith('.py'),
                   os.listdir(os.path.dirname(__file__)))

    for f in files:
        fname = f.split('.', 1)[0]
        __import__('.'.join([__name__, fname]))

    suite = unittest.TestSuite()
    for cls in tests:
        suite.addTest(unittest.makeSuite(cls))

    # The default stream fails in IPython qtconsole on Windows,
    # so just using sys.stdout
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    return runner.run(suite)

if __name__ == '__main__':
    unittest.main()

