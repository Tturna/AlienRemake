from enum import Enum
import random
from classes import Player, Description

def get_random_description(description: Description):
    desc_features = {k: v for k, v in description.__dict__.items() if not k.startswith('__')}
    feature_key = random.choice(list(desc_features.keys()))

    return desc_features[feature_key]

# Action wrappers
# All wrappers should return a function that returns a string representing
# the result of the action. The inner function should take the core game object as an optional argument.
# The wrapper should take the calling player and an optional target player as arguments.
# If the arguments to the wrapper are fucked, it should return a string telling the user what's wrong.

# The point of wrappers is to initialize players with data such as if they are hiding or not.
# They return an inner function that is called at the end of the action phase.

def scout_wrapper(player: Player, target: Player):
    if (target is None):
        return "Scout action requires a player target."
    
    if (target.user.id == player.user.id):
        return "You can't scout yourself."

    if (not target.alive):
        return "You can't target dead players."

    player.leaving_quarters = True

    def scout_action(game=None) -> str:
        if (not target.leaving_quarters):
            return f"❗ {target.user.nick} didn't leave their quarters."

        rng_description = get_random_description(target.description)

        feature_name = rng_description.__class__.__name__
        feature_quality = rng_description.name

        result = f"❗ {target.user.nick} left their quarters.\n**{target.user.nick} has a *{feature_name}* of type *{feature_quality}***"

        return result
    
    return scout_action

def hide_wrapper(player: Player, target: Player = None):
    player.hiding = True

    def hide_action(game=None) -> str:
        msg = "You hide in your quarters."
        
        if (player.attacked and len(player.protectors) > 0):
            msg += f"\n❗ *You hear violent screams outside your door...*"

    return hide_action

def investigate_wrapper(player: Player, target: Player = None):
    player.leaving_quarters = True

    def investigate_action(game=None):
        if (game.killed_player == None):
            return f"❗ No one died!"

        evidence = game.evidence

        feature_name = evidence.__class__.__name__
        feature_quality = evidence.name

        result = f"❗ You found a crime scene!\n**The killer has a *{feature_name}* of type *{feature_quality}***"

        return result
    
    return investigate_action

def loot_wrapper(player: Player, target: Player = None):
    return None

def donate_wrapper(player: Player, target: Player = None):
    return None

def protect_wrapper(player: Player, target: Player = None):
    if (target is None):
        return "Protect action requires a player target."

    if (not target.alive):
        return "You can't target dead players."

    player.leaving_quarters = True

    def protect_action(game=None):
        if (target.hiding):
            msg = f"❗ *You look for {target.user.nick} but can't find them...*"
        else:
            msg = f"❗ You are protecting {target.user.nick}."

        target.protectors.append(player)
        return msg
    
    return protect_action

def use_item_wrapper(player: Player, target: Player = None):
    return None

def kill_wrapper(player: Player, target: Player = None):
    if (target is None):
        return "Kill action requires a player target."
    
    if (target.user.id == player.user.id):
        return "You can't target yourself."
    
    if (not target.alive):
        return "You can't target dead players."

    player.leaving_quarters = True
    target.attacked = True

    def kill_action(game=None):
        protected = len(target.protectors) > 0
        kill_target = target

        if (target.hiding):
            msg = f"❗ You couldn't find {target.user.nick}. Your attack failed!"

        elif (protected):
            msg = f"❗ {target.user.nick} is not alone. Your attack failed!"
        
        elif (target.hiding and protected):
            kill_target = target.protectors[0]
            msg = f"You couldn't find {target.user.nick}, but you found {kill_target.user.nick}! You killed them instead."
            kill_target.alive = False

            rng_description = get_random_description(kill_target.description)
            game.set_evidence(kill_target, rng_description)
        else:
            msg = f"You killed {target.user.nick}!"
            target.alive = False

            rng_description = get_random_description(target.description)
            game.set_evidence(kill_target, rng_description)

        return msg
    
    return kill_action

class Action(Enum):
    """This is a list of all actions that can be performed by a player.
    The first value is the function that is called when the action is performed.
    The second value is a description of the action.
    """
    SCOUT = (scout_wrapper, "Scout (1p) - Leave your quarters to find out a description of someone if they leave their quarters.")
    HIDE = (hide_wrapper, "Hide (2p) - Hide in your quarters. You can't be killed or inspected.")
    INVESTIGATE = (investigate_wrapper, "Investigate (1p) - Leave to find clues about kills that happen during this action phase.")
    LOOT = (loot_wrapper, "Loot (1p) - Leave to look for useful items.")
    DONATE = (donate_wrapper, "Donate - Stay in your quarters and give your action point to someone else.")
    PROTECT = (protect_wrapper, "Protect (2p) - Protect someone. They can't be killed. If they hide and they are attacked, you die.")
    USE_ITEM = (use_item_wrapper, "Use Item (1p) - Stay in your quarters and use an active item if you have one.")
    KILL = (kill_wrapper, "Kill (2p) - Kill unless target hides or is protected. If hidden and protected, the protector dies.")
