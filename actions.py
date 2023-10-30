from player import Player
from enum import Enum
import random

def scout(target: Player):
    if target.leaving_quarters:

        def scout_action():
            # get random description from target
            description = target.description
            desc_features = {k: v for k, v in description.__dict__.items() if not k.startswith('__')}
            feature_key = random.choice(list(desc_features.keys()))
            print(f"pl({target.id}) has {feature_key} {desc_features[feature_key].name}")
        
        return scout_action
    return None

def hide():
    pass

def investigate():
    pass

def loot():
    pass

def donate():
    pass

def protect():
    pass

def use_item():
    pass

def kill():
    pass

class Action(Enum):
    """This is a list of all actions that can be performed by a player.
    The first value is the function that is called when the action is performed.
    The second value indicates whether the action will make the player leave their quarters.
    """
    SCOUT = (scout, True)
    HIDE = (hide, False)
    INVESTIGATE = (investigate, True)
    LOOT = (loot, True)
    DONATE = (donate, False)
    PROTECT = (protect, True)
    USE_ITEM = (use_item, False)
    KILL = (kill, True)