from constants import JOIN_TIME
import discord
from enum import Enum
import random

class GameState(Enum):
    ENDED = 0
    JOIN_PHASE = 1
    LOBBY_PHASE = 2
    DISCUSSION_PHASE = 3
    ACTION_PHASE = 4
    LYNCH_PHASE = 5

# Views

class JoinGameView(discord.ui.View):
    def __init__(self, add_player_function):
        super().__init__(timeout=JOIN_TIME)
        self.add_player_function = add_player_function
    
    @discord.ui.button(label='Join', style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        success = self.add_player_function(interaction.user)

        if (not success):
            await interaction.response.send_message("Joining failed. You might be in the game already", ephemeral=True)
            return

        await interaction.response.send_message("You have joined successfully", ephemeral=True)
        print(f"{interaction.user.nick} joined the game")

# Player

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
    def __init__(self, user: discord.User) -> None:
        self._user_object = user
        self.description = Description(
            footprint = random.choice(list(Footprint)),
            height = random.choice(list(Height)),
            haircolor = random.choice(list(Haircolor))
        )
        self.role = Role.HUMAN
        self.action_function = None
        self.leaving_quarters = False

    user = property(fget=(lambda self: self._user_object))