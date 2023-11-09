# This provides bot behavior and interacts with game logic

import time
import asyncio
import discord
from discord import app_commands
from constants import UBSR_GUILD, ALIEN_GAMER_ROLE_ID, MIN_PLAYERS, JOIN_TIME, LOBBY_TIME, ACTION_TIME, DISCUSSION_TIME, LYNCH_TIME
from classes import GameState
from ui_elements import JoinGameView, ShowRoleView, ShowActionView, ShootView
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
        self.game = Game(self)
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

    def get_gamer_role(self) -> discord.Role:
        if (self.gamer_role is None):
            self.gamer_role = self.game_channel.guild.get_role(ALIEN_GAMER_ROLE_ID)

        return self.gamer_role
    
    async def start_game(self, interaction: discord.Interaction) -> None:
        """Starts the game. Called by bot command."""

        # TODO: Consider making a new thread for each game

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

        if (len(self.game.players) < MIN_PLAYERS):
            await self.stop_game(f"Not enough players ({len(self.game.players)}). Minimum is {MIN_PLAYERS}.")
            return

        self.game.init_game()

        # TODO: Announce joined players

        joined_players = str([f"{pl.member.nick} ({pl.member.name})" for pl in list(self.game.players.values())])

        print(f"Joined players ({len(self.game.players)}): {joined_players}")

        role_view = ShowRoleView(self.game)
        game_start_msg = f"{len(self.game.players)} player(s) joined.\n# Game is starting!\nSee your role:"

        await interaction.channel.send(game_start_msg, view=role_view)

        for pl in list(self.game.players.values()):
            await pl.member.add_roles(self.get_gamer_role())

        await asyncio.sleep(LOBBY_TIME)
        await self.game.run()

    async def action_phase(self):
        """Called by core."""

        action_time_epoch = int(time.time()) + ACTION_TIME
        action_view = ShowActionView(self.game)
        action_phase_text = f"🔍 **Action phase started!** Time expires: <t:{action_time_epoch}:R>\n\n**+1 Action Point!**\n\nSee your points and actions:"

        action_phase_msg = await self.game_channel.send(action_phase_text, view=action_view)

        for pl in list(self.game.players.values()):
            await pl.member.remove_roles(self.get_gamer_role())

        await asyncio.sleep(ACTION_TIME)

        await action_phase_msg.edit(content=f"Action phase ended. Time expired.", view=None)
        
    async def discussion_phase(self):
        """Called by core."""

        discussion_time_epoch = int(time.time()) + DISCUSSION_TIME
        discussion_phase_msg = await self.game_channel.send(f"Discussion phase started! Time expires: <t:{discussion_time_epoch}:R>")

        for pl in list(self.game.players.values()):
            await pl.member.add_roles(self.get_gamer_role())

        await asyncio.sleep(DISCUSSION_TIME)

        await discussion_phase_msg.edit(content=f"Discussion phase ended. Time expired.")
    
    async def lynch_phase(self, gun_player):
        """Called by core."""
        lynch_time_epoch = int(time.time()) + LYNCH_TIME
        gun_player_name = gun_player.member.nick or gun_player.member.name

        msg = f"Lynch phase started! Time expires: <t:{lynch_time_epoch}:R>\n\n🔫 **{gun_player_name}** has the gun!"
        lynch_phase_msg = await self.game_channel.send(msg, view=ShootView(game=self.game, gun_player=gun_player))

        await asyncio.sleep(LYNCH_TIME)

        await lynch_phase_msg.edit(content=f"Lynch phase ended. Time expired.", view=None)
    
    async def announce_killed_player(self, killed_player_name: str) -> None:
        """Called by core."""
        await self.game_channel.send(f"# ⚠️ {killed_player_name} was killed! 🔪")

    async def announce_shot_player(self, shot_player_name: str) -> None:
        """Called by core."""
        await self.game_channel.send(f"# 🔫 {shot_player_name} was shot!")
    
    async def stop_game(self, end_text: str):
        """Stops the game and removes the Alien Gamer role from all players.
        Called by core."""

        await self.game_channel.send(f"\n# Game ended. {end_text}")

        for pl in list(self.game.players.values()):
            await pl.member.remove_roles(self.get_gamer_role())
        
        self.game.reset_game()
    
    async def abort_game(self, interaction: discord.Interaction) -> None:
        """Aborts the game and removes the Alien Gamer role from all players.
        Called by bot command."""

        await interaction.response.send_message("Game aborted", ephemeral=True)

        await self.stop_game("Game aborted by admin.")