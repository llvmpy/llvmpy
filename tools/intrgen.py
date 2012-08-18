#!/usr/bin/env python
#
# Script to generate intrinsic IDs (found in core.py) from
# <llvm>/include/llvm/Intrinsics.gen. Call with path to the
# latter.

import sys

def gen(f, out=sys.stdout):
    intr = []
    maxw = 0
    flag = False
    for line in open(f):
        if line.startswith('#ifdef GET_INTRINSIC_ENUM_VALUES'):
            flag = True
        elif flag:
            if line.startswith('#endif'):
                break
            else:
                item = line.split()[0].replace(',', '')
                if len(item) > maxw:
                    maxw = len(item)
                intr.append(item)

    maxw = len('INTR_') + maxw
    idx = 1
    for i in intr:
        s = 'INTR_' + i.upper()
        out.write('%s = %d\n' % (s.ljust(maxw), idx))
        idx += 1

if __name__ == '__main__':
    gen(sys.argv[1])
