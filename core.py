# This is supposed to be the start of the Alien game logic
# The point is to add Discord functionality later

import random
import time

FOOTPRINT_TYPES = ("small", "big")
HEIGHT_TYPES = ("short", "tall")
HAIRCOLOR_TYPES = ("red", "black", "brown")
ROLE_HUMAN = 0
ROLE_ALIEN = 1

class Player:
    # Set up properties or something so stuff like id can't be changed
    def __init__(self) -> None:
        self._id = random.randint(0, 1000000)
        self.description = {
            "footprint": random.choice(FOOTPRINT_TYPES),
            "height": random.choice(FOOTPRINT_TYPES),
            "haircolor":random.choice(FOOTPRINT_TYPES)
        }
        self.role = ROLE_HUMAN

        @property
        def id(self):
            return self._id

# Create a new player instance for each player who wants to join
# This would be replaced by a thing that gets all joined players on Discord
player_count = input("Player count? Replace this with a Discord thing.")
player_count = int(player_count)

players = []
alien_index = random.randint(0, player_count - 1)

for _ in range(player_count):
    p = Player()
    players.append(p)

players = tuple(players)
players[alien_index].role = ROLE_ALIEN

# Start the game
print(f"Game is starting! {player_count} players joined.")

# Make sure discussion is open
# Wait for a bit
time.sleep(5)

# Reveal roles
for pl in players:
    print(f"pl({pl.id}), you are {pl.role}!")

# Wait a bit
time.sleep(5)

# Action phase
print("Discussion is over. Choose your action.")