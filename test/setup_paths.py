import os
import sys


def setupPaths():
    PATH_SRC = os.path.join(os.path.dirname(__file__), "..", "aroundtheclock")
    sys.path.append(PATH_SRC)
