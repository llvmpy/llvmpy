from __future__ import print_function
import sys
import os
import unittest
import subprocess
import llvm

tests = []  # stores unittest.TestCase objects

# Isolated tests
# Tests that affect process-wide settings
isolated_tests = []  # stores modue name


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
        if cls:
            suite.addTest(unittest.makeSuite(cls))

    # The default stream fails in IPython qtconsole on Windows,
    # so just using sys.stdout

    kwargs = dict(verbosity=verbosity, stream=sys.stdout)

    if sys.version_info[:2] > (2, 6):
        kwargs['buffer'] = True
    runner = unittest.TextTestRunner(**kwargs)
    testresult = runner.run(suite)

    if testresult:
        # Run isolated tests
        print("run isolated tests".center(80, '-'))

        for test in isolated_tests:
            print(('testing %s' % test).center(80))

        cmd = [sys.executable, '-m', test]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        for line in p.stdout:
            print(line, end='')
        p.wait()
        if p.returncode:
            raise Exception("%s returned: %d" % p.returncode)

    return testresult


if __name__ == '__main__':
    unittest.main()

