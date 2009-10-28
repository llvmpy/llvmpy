#!/usr/bin/env python

import os

intrs = []
for line in file('../llvm/_intrinsic_ids.py'):
    if line.startswith('INTR_'):
        if 'INTR_ARM_'    not in line and  \
           'INTR_BFIN_'   not in line and  \
           'INTR_PPC_'    not in line and  \
           'INTR_SPU_'    not in line and  \
           'INTR_X86_'    not in line and  \
           'INTR_XCORE_'  not in line:
            intrs.append(line.split()[0])

i = 0
while i < len(intrs):
    print "`" + "`,`".join(intrs[i:min(i+3,len(intrs)+1)]) + "`"
    i += 3
