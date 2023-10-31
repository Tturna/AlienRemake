from enum import Enum
import random
from classes import Player

def scout_wrapper(target: Player):
    if target.leaving_quarters:

        def scout_action():
            # get random description from target
            description = target.description
            desc_features = {k: v for k, v in description.__dict__.items() if not k.startswith('__')}
            feature_key = random.choice(list(desc_features.keys()))
            print(f"pl({target.id}) has {feature_key} {desc_features[feature_key].name}")
        
        return scout_action
    return None

def hide_wrapper(target=None):
    return None

def investigate_wrapper(target=None):
    return None

def loot_wrapper(target=None):
    return None

def donate_wrapper(target=None):
    return None

def protect_wrapper(target=None):
    return None

def use_item_wrapper(target=None):
    return None

def kill_wrapper(target=None):
    return None

class Action(Enum):
    """This is a list of all actions that can be performed by a player.
    The first value is the function that is called when the action is performed.
    The second value indicates whether the action will make the player leave their quarters.
    """
    SCOUT = (scout_wrapper, True)
    HIDE = (hide_wrapper, False)
    INVESTIGATE = (investigate_wrapper, True)
    LOOT = (loot_wrapper, True)
    DONATE = (donate_wrapper, False)
    PROTECT = (protect_wrapper, True)
    USE_ITEM = (use_item_wrapper, False)
    KILL = (kill_wrapper, True)