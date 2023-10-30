from enum import Enum
import random

class Footprint(Enum):
    SMALL = 0
    BIG = 0

class Height(Enum):
    SHORT = 0
    TALL = 0

class Haircolor(Enum):
    RED = 0
    BLACK = 1
    BROWN = 2

class Role(Enum):
    HUMAN = 0
    ALIEN = 1

class Description():
    def __init__(self, footprint, height, haircolor) -> None:
        self._footprint = footprint
        self._height = height
        self._haircolor = haircolor

    footprint = property(fget=lambda self: self._footprint)
    height = property(fget=lambda self: self._height)
    haircolor = property(fget=lambda self: self._haircolor)

class Player:
    def __init__(self) -> None:
        self._id = random.randint(0, 1000000)
        self.description = Description(
            footprint = random.choice(list(Footprint)),
            height = random.choice(list(Height)),
            haircolor = random.choice(list(Haircolor))
        )
        self.role = Role.HUMAN
        self.action_function = None
        self.leaving_quarters = False

    id = property(fget=(lambda self: self._id))