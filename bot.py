import discord
from discord import app_commands
import json
from constants import TTURNA_ID, GAME_CHANNEL_ID
from bot_client import MyClient
from actions import Action

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
        print(f"{interaction.user.id} tried to start the game")
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
async def stop(interaction: discord.Interaction):
    global game_state

    if (interaction.user.id != TTURNA_ID):
        await interaction.response.send_message(f"You can't stop the game", ephemeral=True)
        return

    if (interaction.channel.id != GAME_CHANNEL_ID):
        await interaction.response.send_message(f"Wrong channel", ephemeral=True)
        return

    # implement

@client.tree.command()
@app_commands.describe(action="The action you want to perform")
@app_commands.describe(target="The player you want to perform the action on")
async def action(interaction: discord.Interaction, action: Action, target: discord.User = None):
    if (not client.is_action_phase()):
        await interaction.response.send_message("Not in action phase", ephemeral=True)
        return

    action_wrapper, leaving_quarters = action.value
    client.game.set_player_action(interaction.user.id, action_wrapper, leaving_quarters, target.id if target != None else None)

    await interaction.response.send_message(f"Action set to {action.name}", ephemeral=True)

with open('secret.json', 'r') as f:
    cont = json.load(f)
    client.run(cont['token'])