import discord
import json
from constants import TTURNA_USER, ROBOTICS_CHANNEL
from classes import MyClient, GameState, Player, JoinGameView

intents = discord.Intents.default()
client = MyClient(intents=intents)

game_state = GameState.OFF
players = None

def add_player_to_game(id):
    players.append(Player(id))

join_game_view = JoinGameView(add_player_to_game)

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
    global game_state

    if (interaction.user.id != TTURNA_USER):
        await interaction.response.send_message(f"You can't start the game", ephemeral=True)
        return

    if (interaction.message.channel.id != ROBOTICS_CHANNEL):
        await interaction.response.send_message(f"Wrong channel", ephemeral=True)
        return
    
    if (game_state == GameState.ON):
        interaction.response.send_message("Game already running")
        return

    game_state = GameState.ON

    # await interaction.response.send_message("Game started", ephemeral=True)
    await interaction.channel.send("Game starting. Join now!", view=join_game_view)
    await join_game_view.wait()

    joined_players = "".join([pl.id for pl in players])

    await interaction.channel.send(f"Join time ended. Joined players: {joined_players}")

@client.tree.command()
async def stop(interaction: discord.Interaction):
    global game_state

    if (interaction.user.id != TTURNA_USER):
        await interaction.response.send_message(f"You can't stop the game", ephemeral=True)
        return

    if (interaction.message.channel.id != ROBOTICS_CHANNEL):
        await interaction.response.send_message(f"Wrong channel", ephemeral=True)
        return

    if (game_state == GameState.OFF):
        msg = f'Game is not running'
    else:
        game_state = GameState.OFF
        msg = f'Game stopped, {interaction.user.mention}'

    await interaction.response.send_message(msg, ephemeral=True)

# ------------------------------------------------------------------------------

with open('secret.json', 'r') as f:
    cont = json.load(f)
    client.run(cont['token'])