# This is supposed to be the start of the Alien game logic
# The point is to add Discord functionality later

import random
import time
from actions import Action
from classes import Player, Role

def evaluate_actions(players: tuple[Player]):
    for pl in players:
        if (pl.action_function != None):
            pl.action_function()

        pl.action_function = None
        pl.leaving_quarters = False

def init_game(players: tuple[Player]):
    alien_index = random.randint(0, len(players) - 1)
    players[alien_index].role = Role.ALIEN

    # choose a couple random items that can be found this game

# Make sure discussion is open
# Wait for a bit
time.sleep(3)

# Reveal roles
for pl in players:
    print(f"pl({pl.id}), you are {pl.role.name}!")
    print(f"Footprint: {pl.description.footprint.name}")

# Wait a bit
time.sleep(3)

# Action phase
print("Discussion is over. Choose your action.")
for pl in players:
    print(f"pl({pl.id}), choose your action!")
    action_input = input("Action? (scout, hide, investigate, loot, donate, protect, use_item, kill): ")
    target_input = input("Target? (pl_id, leave empty if action doesn't require target.): ")
    action_wrapper, leaves_quarters = Action[action_input.upper()].value
    pl.leaving_quarters = leaves_quarters
    
    if target_input == "":
        pl.action_function = action_wrapper()
    else:
        # Get player with target id
        target = next((p for p in players if p.id == int(target_input)), None)
        pl.action_function = action_wrapper(target=target)

# Evaluate actions
evaluate_actions(players)

# Wait a bit
time.sleep(3)

print("Discussion started.")