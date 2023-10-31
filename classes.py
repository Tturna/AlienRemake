from constants import UBSR_GUILD
import discord
from discord import app_commands
from enum import Enum
import random

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=UBSR_GUILD)
        await self.tree.sync(guild=UBSR_GUILD)

class GameState(Enum):
    OFF = 0
    ON = 1

# Views

class JoinGameView(discord.ui.View):
    def __init__(self, add_player_function: function):
        super().__init__(timeout=20)
        self.add_player_function = add_player_function
    
    @discord.ui.button(label='Join', style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        success = self.add_player_function(interaction.user.id)

        if (not success):
            await interaction.response.send_message("Joining failed. You might be in the game already", ephemeral=True)
            return

        await interaction.response.send_message("You have joined successfully", ephemeral=True)

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
    def __init__(self, user_id) -> None:
        self._id = user_id
        self.description = Description(
            footprint = random.choice(list(Footprint)),
            height = random.choice(list(Height)),
            haircolor = random.choice(list(Haircolor))
        )
        self.role = Role.HUMAN
        self.action_function = None
        self.leaving_quarters = False

    id = property(fget=(lambda self: self._id))