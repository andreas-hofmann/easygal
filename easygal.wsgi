import os
import sys

sys.path.append(os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

import easygal

easygal.create_directories()

application = easygal.egapp
