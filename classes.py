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

# TODO: Make it so only players can press these buttons 
class JoinGameView(discord.ui.View):
    def __init__(self, add_player_function):
        super().__init__(timeout=JOIN_TIME)
        self.add_player_function = add_player_function
    
    @discord.ui.button(label='Join', style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        success = self.add_player_function(interaction.user)

        if (not success):
            await interaction.response.send_message("🚫 Joining failed. You might be in the game already", ephemeral=True)
            return

        await interaction.response.send_message("✅ You have joined successfully", ephemeral=True)
        print(f"{interaction.user.name} joined the game")


class ShowRoleView(discord.ui.View):
    def __init__(self, game):
        super().__init__()
        self.game = game
    
    @discord.ui.button(label='Show role', style=discord.ButtonStyle.green)
    async def show_role(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (not self.game.players.has(interaction.user.id)):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players.get(interaction.user.id)
        
        if (player.role == Role.ALIEN):
            instruction = "Kill all humans 🔪"
            article = "an"
        else:
            instruction = "Find and eliminate the alien 👽"
            article = "a"

        await interaction.response.send_message(f"## You are {article} {player.role.name}\n{instruction}", ephemeral=True)

class ActionView(discord.ui.View):
    def __init__(self, game):
        super().__init__()
        self.game = game
    
    @discord.ui.button(label='Show Points', style=discord.ButtonStyle.blurple)
    async def show_action_points(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (not self.game.players.has(interaction.user.id)):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players[interaction.user.id]
        await interaction.response.send_message(f"You have {player.action_points} action points.", ephemeral=True)
    
    @discord.ui.button(label='Show Actions', style=discord.ButtonStyle.green)
    async def show_available_actions(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (not self.game.players.has(interaction.user.id)):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        role = self.game.players[interaction.user.id].role

        # TODO: Figure out a better way to do actions so that they can be more dynamic
        if (role == Role.ALIEN):
            actions = "Kill (2p)"
        else:
            # actions = "Scout (1p)\nHide (2p)\nInvestigate (1p)\nLoot (1p)\nDonate (1p)\nProtect (2p\nUse Item (1p)"
            actions = "Scout (1p)\nHide (2p)\nInvestigate (1p)\nProtect (2p)"
        
        await interaction.response.send_message(f"Available actions:\n{actions}", ephemeral=True)

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
        self.hiding = False
        self.attacked = False
        self.protectors = []
        self.action_callback = None
        self.alive = True
        self.action_points = 0
    
    def reset_action_state(self):
        self.action_function = None
        self.leaving_quarters = False
        self.hiding = False
        self.attacked = False
        self.protectors = []
        self.action_callback = None

    user = property(fget=(lambda self: self._user_object))