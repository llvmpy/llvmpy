import math
import os
import subprocess
udt = os.path.join('.', 'test_sdivmod64.run')

def testcase(dividend, divisor):
    print 'divmod64(%d, %d)' % (dividend, divisor)

    procargs = ('%s %s %s' % (udt, dividend, divisor)).split()
    result = subprocess.check_output(procargs)
    gotQ, gotR = map(int, result.splitlines())

    expectQ = dividend // divisor
    expectR = dividend % divisor

    print 'Q = %d, R = %d' % (gotQ, gotR)

    if expectQ != gotQ:
        raise ValueError("invalid quotient: got=%d but expect=%d" %
                         (gotQ, expectQ))
    if expectR != gotR:
        raise ValueError("invalid remainder: got=%d but expect=%d" %
                         (gotR, expectR))
    print 'OK'

def testsequence():
    subjects = [
        (0, 1),
        (0, 0xffffffff),
        (1, 2),
        (1, 983219),
        (2, 2),
        (3, 2),
        (1024, 2),
        (2048, 512),
        (21321, 512),
        (9329189, 1031),
        (0xffffffff, 2),
        (0xffffffff, 0xffff),
        (0x1ffffffff, 2),
        (0x1ffffffff, 0xffff),
        (0xffff, 0xffffffff),
        (0x0fffffffffffffff, 0xffff),
        (0x7fffffffffffffff, 0x7fffffffffffffff),
        (0x7fffffffffffffff, 0x7ffffffffffffff0),
        (0x7fffffffffffffff, 87655678587161901),
    ]

    for dvd, dvr in subjects:
        testcase(dvd, dvr)
        testcase(dvd, -dvr)
        testcase(-dvd, dvr)
        testcase(-dvd, -dvr)

if __name__ == '__main__':
    testsequence()
