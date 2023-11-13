# This provides all the game logic

import random
import discord
from typing import Callable
from classes import Player, Role, GameState, Height, Footprint, Haircolor

# TODO: Check if Python has singletons or something
class Game:
    def __init__(self, bot_client) -> None:
        self.bot_client = bot_client
        self.game_state = GameState.ENDED
        self.players = dict()
        self.alien_player_id = None
        self.killed_player = None
        self.shot_player = None
        self.evidence = None

    def add_player(self, member: discord.Member) -> bool:
        """Adds a player to the game if not in already. Returns True if successful, otherwise False."""
        if (self.players.get(member.id) is not None):
            return False

        self.players[member.id] = Player(member)
        return True
    
    def set_player_action(self, user_id: int, action_wrapper: Callable, target_id: int, callback: Callable) -> None or str:
        """Sets the action for a player. Returns None if successful, otherwise returns an error message."""

        player = self.players.get(user_id)

        if (action_wrapper is None):
            player.action_function = None
            player.action_callback = None
            return None

        target = self.players.get(target_id)

        # the wrapper sets all the data needed for the actions and
        # returns the action to be called at the end of the action phase
        # or an error message if the action failed

        # make sure the action is used with valid arguments
        result = action_wrapper(player, target)
        if (type(result) == str):
            return result

        player.action_function = result
        player.action_callback = callback
    
    def set_evidence(self, killed_player: Player, evidence: Height or Footprint or Haircolor):
        """Sets the evidence for the next discussion and lynch phases."""
        self.killed_player = killed_player
        self.evidence = evidence

    def init_game(self):
        """Initializes the game. Called when the game starts with enough players."""
        self.alien_player_id = random.choice(list(self.players.keys()))

        alien_player = self.players.get(self.alien_player_id)
        alien_player.role = Role.ALIEN

        print(f"The Alien is {alien_player.member.nick} ({alien_player.member.name})")

        # choose a couple random items that can be found this game
    
    def check_game_end(self) -> None or str:
        """Checks if the game has ended. Returns None if not, otherwise returns a string with the win text."""

        alien_alive = False
        alive_count = 0

        for pl in list(self.players.values()):
            if pl.role == Role.ALIEN and pl.alive:
                alien_alive = True
            
            if pl.alive:
                alive_count += 1
        
        if (alien_alive and alive_count == 1):
            # alien wins
            return "Alien wins! 👽🔪"
        elif (not alien_alive):
            # humans win
            return "Humans win! 🥳"
        
        # game not ended
        return None

    async def evaluate_actions(self) -> None or str:
        """Evaluates the actions of all players. Returns None if the game hasn't ended, otherwise returns a string with the win text."""

        print("Evaluating actions")
        players = list(self.players.values())

        alien_player = self.players.get(self.alien_player_id)

        # This system exists because actions need to happen in a certain order. Example:

        # Hiding has to happen before protecting, otherwise the protector doesn't know if their target is hiding.
        # Hiding and protecting have to happen before killing, otherwise it defeats the purpose.
        # Killing has to happen before investigating so that players get clues.

        # TODO: Figure out a better action evluation system that doesn't rely on the action function name

        hiders = []
        protectors = []
        killers = []
        investigators = []
        therest = []

        all_actors = [hiders, protectors, killers, investigators, therest]

        for pl in players:
            if (not pl.alive): continue

            if (pl.action_function):
                if (pl.action_function.__name__ == "hide_wrapper"):
                    hiders.append(pl)
                elif (pl.action_function.__name__ == "protect_wrapper"):
                    protectors.append(pl)
                elif (pl.action_function.__name__ == "kill_wrapper"):
                    killers.append(pl)
                elif (pl.action_function.__name__ == "investigate_wrapper"):
                    investigators.append(pl)
                else:
                    therest.append(pl)
        
        for specific_actors in all_actors:
            for pl in specific_actors:
                print(f"{pl.member.nick} ({pl.role.name}), action: {pl.action_function}")

                result = pl.action_function(self)

                if (not pl.alive):
                    killer_name = alien_player.member.nick if alien_player.member.nick else alien_player.member.name
                    result += f"\n\n# You were killed by {killer_name}!"

                await pl.action_callback(result)

        if (self.killed_player is not None):
            killed_player_name = self.killed_player.member.nick if self.killed_player.member.nick else self.killed_player.member.name
            await self.bot_client.announce_killed_player(killed_player_name)

        for pl in players:
            pl.reset_action_state()
        
        self.evidence = None
        self.killed_player = None

        # return self.check_game_end()

    async def run(self):
        """Iterate through the game phases until the game ends."""

        win_text = None

        # Run the game until the game ends itself or something manually sets the game state to ENDED
        while win_text is None or self.game_state != GameState.ENDED:
            self.game_state = GameState.ACTION_PHASE

            # Increment action points
            for pl in list(self.players.values()):
                if (pl.alive):
                    pl.action_points += 1

            await self.bot_client.action_phase()

            # Check for aborts
            if self.game_state == GameState.ENDED: return

            win_text = await self.evaluate_actions()

            if win_text is not None: break

            self.game_state = GameState.DISCUSSION_PHASE
            await self.bot_client.discussion_phase()

            # Check for aborts
            if self.game_state == GameState.ENDED: return

            self.game_state = GameState.LYNCH_PHASE

            # pick random player to give the gun to
            
            gun_player = None

            for pl in list(self.players.values()):
                if (pl.alive):
                    gun_player = pl
                    break
            
            if (gun_player is None):
                win_text = "No one is left alive. How did this happen?"
                break

            await self.bot_client.lynch_phase(gun_player)

            # check if someone was shot
            if (self.shot_player is not None):
                self.shot_player.alive = False
                await self.bot_client.announce_shot_player(self.shot_player.member.nick or self.shot_player.member.name)
                self.shot_player = None

                win_text = self.check_game_end()
                if win_text is not None: break

            # Check for aborts
            if self.game_state == GameState.ENDED: return
        
        print(win_text)
        await self.bot_client.stop_game(win_text)
        self.reset_game()
    
    def reset_game(self):
        """Resets the game state. Called when the game ends."""

        self.game_state = GameState.ENDED
        self.players = dict()
