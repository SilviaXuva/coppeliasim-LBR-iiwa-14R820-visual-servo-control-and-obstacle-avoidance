from .coppelia_sim import CoppeliaSim
from .objects import *

from .objects import __all__ as objects_all

__all__ = ["CoppeliaSim"] + objects_all
