import discord
from discord import app_commands
import json
from enum import Enum

UBSR_GUILD = discord.Object(id=984851431469236315)
TTURNA_USER = discord.Object(id=207646629140889601)
ROBOTICS_CHANNEL = discord.Object(id=1119326839060570133)

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


intents = discord.Intents.default()
client = MyClient(intents=intents)

class GameState(Enum):
    OFF = 0
    ON = 1

game_state = GameState.OFF

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
        msg = f'Game already running'
    else:
        game_state = GameState.ON
        msg = f'Game started, {interaction.user.mention}'

    await interaction.response.send_message(msg, ephemeral=True)

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