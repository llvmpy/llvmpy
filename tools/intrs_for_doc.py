#!/usr/bin/env python

import os

NCOLS = 4
INF   = '../llvm/_intrinsic_ids.py'
OUTF  = '../www/src/intrinsics.csv'

intrs = []
for line in file(INF):
    if line.startswith('INTR_'):
        if 'INTR_ALPHA_'  not in line and  \
           'INTR_ARM_'    not in line and  \
           'INTR_BFIN_'   not in line and  \
           'INTR_PPC_'    not in line and  \
           'INTR_SPU_'    not in line and  \
           'INTR_X86_'    not in line and  \
           'INTR_XCORE_'  not in line:
            intrs.append(line.split()[0])

outf = open(OUTF, 'wt')
i = 0
while i < len(intrs):
    print >>outf, "`" + "`,`".join(intrs[i:min(i+NCOLS,len(intrs)+1)]) + "`"
    i += NCOLS
