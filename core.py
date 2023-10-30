# This is supposed to be the start of the Alien game logic
# The point is to add Discord functionality later

import random
import time
from player import Player, Role
from actions import Action

def evaluate_actions(players: tuple[Player]):
    for pl in players:
        if (pl.action_function != None):
            pl.action_function()

        pl.action_function = None
        pl.leaving_quarters = False

# Create a new player instance for each player who wants to join
# This would be replaced by a thing that gets all joined players on Discord
player_count = input("Player count? Replace this with a Discord thing.")
player_count = int(player_count)

players = [Player() for _ in range(player_count)]

# for _ in range(player_count):
#     p = Player()
#     players.append(p)

players = tuple(players)
alien_index = random.randint(0, player_count - 1)
players[alien_index].role = Role.ALIEN

# Start the game
print(f"Game is starting! {player_count} players joined.")

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