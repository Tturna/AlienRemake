from enum import Enum
import random
from classes import Player, Description, Role

def get_random_description(description: Description):
    desc_features = {k: v for k, v in description.__dict__.items() if not k.startswith('__')}
    feature_key = random.choice(list(desc_features.keys()))

    return desc_features[feature_key]

# TODO: Unit tests

# Action wrappers
# All wrappers should return a function that returns a string representing
# the result of the action. The inner function should take the core game object as an optional argument.
# The wrapper should take the calling player and an optional target player as arguments.
# If the arguments to the wrapper are fucked, it should return a string telling the user what's wrong.

# The point of wrappers is to initialize players with data such as if they are hiding or not.
# They return an inner function that is called at the end of the action phase.

def scout_wrapper(player: Player, target: Player):
    if (player.role == Role.ALIEN):
        return "You can't scout as the alien."

    if (target is None):
        return "Scout action requires a valid player target."
    
    if (target.user.id == player.user.id):
        return "You can't scout yourself."

    if (not target.alive):
        return "You can't target dead players."
    
    if (player.action_points < 1):
        return "Not enough action points!"

    player.leaving_quarters = True

    def scout_action(game=None) -> str:
        player.action_points -= 1

        target_name = target.user.nick if target.user.nick else target.user.name

        if (not target.leaving_quarters):
            return f"❗ {target_name} didn't leave their quarters."

        rng_description = get_random_description(target.description)

        feature_name = rng_description.__class__.__name__
        feature_quality = rng_description.name

        result = f"❗ {target_name} left their quarters.\n**{target_name} has a *{feature_name}* of type *{feature_quality}***"

        return result
    
    return scout_action

def hide_wrapper(player: Player, target: Player = None):
    if (player.role == Role.ALIEN):
        return "You can't hide as the alien."
    
    if (player.action_points < 2):
        return "Not enough action points!"

    player.hiding = True

    def hide_action(game=None) -> str:
        player.action_points -= 2

        msg = "You hide in your quarters."
        
        if (player.attacked and len(player.protectors) > 0):
            msg += f"\n❗ *You hear violent screams outside your door...*"
        
        return msg

    return hide_action

def investigate_wrapper(player: Player, target: Player = None):
    if (player.role == Role.ALIEN):
        return "You can't investigate as the alien."
    
    if (player.action_points < 1):
        return "Not enough action points!"

    player.leaving_quarters = True

    def investigate_action(game=None):
        player.action_points -= 1

        if (game.killed_player == None):
            return f"❗ No one died!"
        
        if (game.evidence == None):
            return f"❗ You didn't find any evidence!"

        evidence = game.evidence

        feature_name = evidence.__class__.__name__
        feature_quality = evidence.name

        result = f"❗ You found a crime scene!\n**The killer has a *{feature_name}* of type *{feature_quality}***"
    
        return result
    
    return investigate_action

def loot_wrapper(player: Player, target: Player = None):
    return "Not implemented yet."

# TODO: Make sure donate works

def donate_wrapper(player: Player, target: Player = None):
    if (target is None):
        return "Donate action requires a valid player target."
    
    if (target.user.id == player.user.id):
        return "You can't donate to yourself."
    
    if (not target.alive):
        return "You can't target dead players."
    
    if (player.action_points < 1):
        return "You don't have anything to donate!"
    
    def donate_action(game=None):
        print("Donation!!!!")
        print(f"{player.user.name} has {player.action_points} action points")
        print(f"{target.user.name} has {target.action_points} action points")
        player.action_points -= 1
        target.action_points += 1
        print(f"{player.user.name} donated 1 action point to {target.user.name}")
        print(f"{player.user.name} has {player.action_points} action points")
        print(f"{target.user.name} has {target.action_points} action points")

        target_name = target.user.nick if target.user.nick else target.user.name

        return f"❗ You donated an action point to {target_name}."
    
    return donate_action

def protect_wrapper(player: Player, target: Player = None):
    if (player.role == Role.ALIEN):
        return "You can't protect as the alien."

    if (target is None):
        return "Protect action requires a valid player target."

    if (not target.alive):
        return "You can't target dead players."
    
    if (player.action_points < 2):
        return "Not enough action points!"
    
    player.leaving_quarters = True

    def protect_action(game=None):
        player.action_points -= 2

        target_name = target.user.nick if target.user.nick else target.user.name

        if (target.hiding):
            msg = f"❗ *You look for {target_name} but can't find them...*"
        else:
            msg = f"❗ You are protecting {target_name}."

        target.protectors.append(player)
        return msg
    
    return protect_action

def use_item_wrapper(player: Player, target: Player = None):
    return "Not implemented yet."

def kill_wrapper(player: Player, target: Player = None):
    if (player.role == Role.HUMAN):
        return "You can't kill as a human."

    if (target is None):
        return "Kill action requires a valid player target."
    
    if (target.user.id == player.user.id):
        return "You can't target yourself."
    
    if (not target.alive):
        return "You can't target dead players."
    
    if (player.action_points < 2):
        return "Not enough action points!"
    
    player.leaving_quarters = True
    target.attacked = True

    def kill_action(game=None):
        player.action_points -= 2

        target_name = target.user.nick if target.user.nick else target.user.name

        protected = len(target.protectors) > 0
        kill_target = target

        if (target.hiding):
            msg = f"❗ You couldn't find {target_name}. Your attack failed!"

        elif (protected):
            msg = f"❗ {target_name} is not alone. Your attack failed!"
        
        elif (target.hiding and protected):
            kill_target = target.protectors[0]
            kill_target_name = kill_target.user.nick if kill_target.user.nick else kill_target.user.name

            msg = f"You couldn't find {target_name}, but you found {kill_target_name}! You killed them instead."
            kill_target.alive = False

            rng_description = get_random_description(kill_target.description)
            game.set_evidence(kill_target, rng_description)
        else:
            msg = f"🔪 **You killed {target_name}!**"
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
