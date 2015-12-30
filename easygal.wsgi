import os
import sys

sys.path.append(os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from easygal import EasyGal

gal = EasyGal()
application = gal.get_app()
