import discord
import random
from enum import Enum

class GameState(Enum):
    ENDED = 0
    JOIN_PHASE = 1
    LOBBY_PHASE = 2
    DISCUSSION_PHASE = 3
    ACTION_PHASE = 4
    LYNCH_PHASE = 5

# Player

class Footprint(Enum):
    SMALL = 0
    BIG = 1

class Height(Enum):
    SHORT = 0
    TALL = 1

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

    def get_random_description(self):
        desc_features = {k: v for k, v in self.__dict__.items() if not k.startswith('__')}
        feature_key = random.choice(list(desc_features.keys()))

        return desc_features[feature_key]

class Player:
    def __init__(self, member: discord.Member) -> None:
        self._member_object = member
        self.description = Description(
            footprint = random.choice(list(Footprint)),
            height = random.choice(list(Height)),
            haircolor = random.choice(list(Haircolor))
        )
        self.role = Role.HUMAN
        self.action_function = None
        self.leaving_quarters = False
        self.hiding = False
        self.attacked = False
        self.protectors = []
        self.action_callback = None
        self.alive = True
        self.action_points = 0
    
    def reset_action_state(self) -> None:
        self.action_function = None
        self.leaving_quarters = False
        self.hiding = False
        self.attacked = False
        self.protectors = []
        self.action_callback = None

    member = property(fget=(lambda self: self._member_object))