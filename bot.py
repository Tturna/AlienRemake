# This provides an interface to the bot commands and events

import discord
import json
from constants import TTURNA_ID, GAME_CHANNEL_ID
from classes import Role
from bot_client import MyClient

intents = discord.Intents.default()
client = MyClient(intents=intents)

# EVENTS -----------------------------------------------------------------------

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

# COMMANDS ---------------------------------------------------------------------

@client.tree.command()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'Pong, {interaction.user.mention}')

@client.tree.command()
async def start(interaction: discord.Interaction):

    if (interaction.user.id != TTURNA_ID):
        print(f"{interaction.user.name} tried to start the game")
        await interaction.response.send_message(f"You can't start the game", ephemeral=True)
        return

    if (interaction.channel.id != GAME_CHANNEL_ID):
        await interaction.response.send_message(f"Wrong channel", ephemeral=True)
        return
    
    if (client.is_game_running()):
        await interaction.response.send_message("Game already running", ephemeral=True)
        return

    await client.start_game(interaction)

@client.tree.command()
async def abort(interaction: discord.Interaction):
    global game_state

    if (interaction.user.id != TTURNA_ID):
        print(f"{interaction.user.name} tried to stop the game")
        await interaction.response.send_message(f"You can't stop the game", ephemeral=True)
        return

    if (interaction.channel.id != GAME_CHANNEL_ID):
        await interaction.response.send_message(f"Wrong channel", ephemeral=True)
        return

    await client.abort_game(interaction)

@client.tree.command()
async def role(interaction: discord.Interaction):
    """Show your role and description."""

    if (interaction.channel.id != GAME_CHANNEL_ID):
        await interaction.response.send_message(f"Wrong channel", ephemeral=True)
        return
    
    if (not client.is_game_running()):
        await interaction.response.send_message("🚫 Game not running", ephemeral=True)
        return

    player = client.game.players.get(interaction.user.id)
    
    if (player.role == Role.ALIEN):
        role_text = "You are the alien 👽"
        instruction = "Kill all humans and don't get caught 🔪"
    else:
        role_text = "You are a human 🕵️"
        instruction = "Find and eliminate the alien 👽"
    
    footprint = player.description.footprint.name.lower()
    height = player.description.height.name.lower()
    haircolor = player.description.haircolor.name.lower()
    description = f"**Your description:**\nFootprint: {footprint}\nHeight: {height}\nHaircolor: {haircolor}"

    await interaction.response.send_message(f"## {role_text}\n{instruction}\n\n{description}", ephemeral=True)

with open('secret.json', 'r') as f:
    cont = json.load(f)
    client.run(cont['token'])