# This provides an interface to the bot commands and events

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
@app_commands.describe(action_choice="The action you want to perform")
@app_commands.describe(target="The player you want to perform the action on. This is optional for some actions.")
@app_commands.choices(action_choice=[
    app_commands.Choice(name=Action.SCOUT.value[1], value=Action.SCOUT.name),
    app_commands.Choice(name=Action.HIDE.value[1], value=Action.HIDE.name),
    app_commands.Choice(name=Action.INVESTIGATE.value[1], value=Action.INVESTIGATE.name),
    # app_commands.Choice(name=Action.LOOT.value[1], value=Action.LOOT.name),
    # app_commands.Choice(name=Action.DONATE.value[1], value=Action.DONATE.name),
    app_commands.Choice(name=Action.PROTECT.value[1], value=Action.PROTECT.name),
    # app_commands.Choice(name=Action.USE_ITEM.value[1], value=Action.USE_ITEM.name),
    app_commands.Choice(name=Action.KILL.value[1], value=Action.KILL.name)
])
async def action(interaction: discord.Interaction, action_choice: app_commands.Choice[str], target: discord.Member = None):
    """Set your action for the current action phase."""

    player = client.game.players.get(interaction.user.id)

    if (not player.alive):
        await interaction.response.send_message("🚫 You are dead", ephemeral=True)
        return

    if (not client.is_action_phase()):
        await interaction.response.send_message("🚫 Not in action phase", ephemeral=True)
        return

    action = Action[action_choice.value]

    action_wrapper, _ = action.value

    if (target != None):
        target_id = target.id
        target_name = target.nick if target.nick != None else target.name
        target_text = f"targeting **{target_name}**"
    else:
        target_id = None
        target_name = None
        target_text = "without a target"

    msg = f"✅ Action set to **{action.name}** {target_text}. You will see the result here after the action phase."

    async def callback(result: str):
        await interaction.edit_original_response(content=msg + f"\n\n{result}")

    # print(f"{interaction.user.nick} action: {action_wrapper}, target: {target.nick if target != None else 'None'}")
    error_text = client.game.set_player_action(
        user_id=interaction.user.id,
        action_wrapper=action_wrapper,
        target_id=target_id,
        callback=callback
    )

    if (error_text is not None):
        msg = f"🚫 Action failed:\n**{error_text}**"

    await interaction.response.send_message(msg, ephemeral=True)

with open('secret.json', 'r') as f:
    cont = json.load(f)
    client.run(cont['token'])