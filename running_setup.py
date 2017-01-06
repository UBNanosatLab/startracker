import os
from subprocess import call
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
print PROJECT_ROOT
config = open("config.py","w")
config.write('PROJECT_ROOT="'+PROJECT_ROOT+'/"')
config.close()
