import os
from subprocess import call
import sys
"""
This script is used in order to enable importing of modules relative
to the top level directory of the project
"""



PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
#check if PROJECT_ROOT has been permanently added to the path
if sys.path.count(PROJECT_ROOT) == 1:
    print "Altering..."
    home_dir = os.path.expanduser("~")
    bash_rc = open(home_dir+"/.profile","a")
    line = 'export PYTHONPATH="${PYTHONPATH}:'+PROJECT_ROOT+'"\n'
    bash_rc.write(line)
    bash_rc.close()
    print "run source ~/.profile for changes to take effect."
    print "This file will need to be re-run if the directory is moved or the repository is re-downloaded"
if not os.path.isfile("config.py"):
    config = open("config.py","w")
    config.write('PROJECT_ROOT="'+PROJECT_ROOT+'/"')
    config.close()
