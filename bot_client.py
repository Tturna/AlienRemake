import time
import asyncio
import discord
from discord import app_commands
from constants import UBSR_GUILD, GAME_CHANNEL_ID, JOIN_TIME, LOBBY_TIME, ACTION_TIME, DISCUSSION_TIME, LYNCH_TIME
from classes import GameState, JoinGameView
from core import Game

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
        self.game = Game()
        self.game_channel = None

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=UBSR_GUILD)
        await self.tree.sync(guild=UBSR_GUILD)

    def is_game_running(self) -> bool:
        return self.game.game_state is not GameState.ENDED

    def is_action_phase(self) -> bool:
        return self.game.game_state is GameState.ACTION_PHASE
    
    async def start_game(self, interaction: discord.Interaction):
        self.game.game_state = GameState.JOIN_PHASE
        self.game_channel = interaction.channel

        join_game_view = JoinGameView(self.game.add_player)

        expire_time_epoch = int(time.time()) + JOIN_TIME

        # await interaction.response.send_message("Game started", ephemeral=True)
        # print(f"Time epoch +{JOIN_TIME}: {expire_time_epoch}")
        
        await interaction.response.send_message("Starting game", ephemeral=True)
        join_msg = await interaction.channel.send(f"Game starting. Join now! Time expires: <t:{expire_time_epoch}:R>", view=join_game_view)

        await asyncio.sleep(JOIN_TIME)

        join_game_view.children[0].disabled = True
        await join_msg.edit(content=f"Game starting. Join time expired.", view=join_game_view)

        join_game_view.stop()
        print("Join time ended.")

        # TODO: Abort if not enough players joined

        self.game.init_game(self)

        joined_players = str([f"{pl.user.nick} ({pl.user.name})" for pl in list(self.game.players.values())])

        print(f"Joined players ({len(self.game.players)}): {joined_players}")
        await interaction.channel.send(f"{len(self.game.players)} players joined. Game is starting soon!")

        await asyncio.sleep(LOBBY_TIME)
        await self.game.run()

    async def action_phase(self):
        action_time_epoch = int(time.time()) + ACTION_TIME
        action_phase_msg = await self.game_channel.send(f"Action phase started! Time expires: <t:{action_time_epoch}:R>")

        await asyncio.sleep(ACTION_TIME)

        await action_phase_msg.edit(content=f"Action phase ended. Time expired.")
        