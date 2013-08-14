import sys
import re

buf = []
with open(sys.argv[1], 'r') as fin:
    tripleline = re.compile('^target\s+triple\s+=\s+')
    for line in fin.readlines():
        if not tripleline.match(line):
            buf.append(line)

with open(sys.argv[1], 'w') as fout:
    for line in buf:
        fout.write(line)


