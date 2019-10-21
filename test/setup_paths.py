import os
import sys
from unittest.mock import MagicMock


def setupPaths():
    PATH_SRC = os.path.join(os.path.dirname(__file__), "..", "aroundtheclock")
    sys.path.append(PATH_SRC)


def importFakeRPiModule():
    sys.modules["RPi"] = MagicMock()
    sys.modules["RPi.GPIO"] = MagicMock()
