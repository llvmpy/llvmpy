from os import chdir
from os.path import dirname
import sys, subprocess

scriptdir = dirname(__file__)
chdir(scriptdir)

subprocess.check_call([sys.executable, 'gen/gen.py', 'api', 'src'])
