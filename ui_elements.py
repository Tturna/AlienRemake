import discord
from discord.interactions import Interaction
from classes import Player, Role
from constants import JOIN_TIME
from actions import ActionsEnum

# Selects

class ActionSelect(discord.ui.Select):
    def __init__(self, player: Player):

        options = [
            discord.SelectOption(label=action_item.value.description, value=action_item.name) for action_item in ActionsEnum if (player.role in action_item.value.roles)
        ]

        super().__init__(placeholder="Select an action", options=options)
    
    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(f"You selected {self.values[0]}", ephemeral=True)

# Views

class ActionSelectView(discord.ui.View):
    def __init__(self, *, player: Player):
        super().__init__()
        self.add_item(ActionSelect(player=player))

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

        if (interaction.user.id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players.get(interaction.user.id)
        
        if (player.role == Role.ALIEN):
            role_text = "You are the alien 👽"
            instruction = "Kill all humans and don't get caught 🔪"
        else:
            role_text = "You are a human 🕵️"
            instruction = "Find and eliminate the alien 👽"
        
        footprint = player.description.footprint.name.lower()
        height = player.description.height.name.lower()
        haircolor = player.description.haircolor.name.lower()
        description = f"**Your description:**\nFootprint: **{footprint}**\nHeight: **{height}**\nHaircolor: **{haircolor}**"

        await interaction.response.send_message(f"## {role_text}\n{instruction}\n\n{description}", ephemeral=True)

class ShowActionView(discord.ui.View):
    def __init__(self, game):
        super().__init__()
        self.game = game
    
    @discord.ui.button(label='Show Points', style=discord.ButtonStyle.blurple)
    async def show_action_points(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (interaction.user.id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players[interaction.user.id]
        await interaction.response.send_message(f"You have **{player.action_points}** action points.", ephemeral=True)
    
    @discord.ui.button(label='Show Actions', style=discord.ButtonStyle.blurple)
    async def show_available_actions(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if (interaction.user.id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players.get(interaction.user.id)

        actions = ""
        
        for action_item in ActionsEnum:
            action = action_item.value

            if (player.role in action.roles):
                surround = "**" if (player.action_points >= action.cost) else "*"
                actions += f"{surround}{action.description}{surround}\n"
        
        await interaction.response.send_message(f"**Available actions:**\n\n{actions}\nSelect an action with the `Set Action` button.", ephemeral=True)
    
    @discord.ui.button(label='Set Action', style=discord.ButtonStyle.green)
    async def set_action(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (interaction.user.id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players.get(interaction.user.id)

        # await interaction.response.send_modal(ActionModal())
        await interaction.response.send_message("Select an action", ephemeral=True, view=ActionSelectView(player=player))