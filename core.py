# This provides all the game logic

import random
import discord
from classes import Player, Role, GameState, Height, Footprint, Haircolor

class Game:
    def __init__(self) -> None:
        self.game_state = GameState.ENDED
        self.players = dict()
        self.bot_client = None
        self.alien_player_id = None
        self.killed_player = None
        self.evidence = None

    def add_player(self, user: discord.User):
        if (self.players.get(user.id) is not None):
            return False

        self.players[user.id] = Player(user)
        return True
    
    def set_player_action(self, user_id: int, action_wrapper, target_id: int, callback):
        player = self.players.get(user_id)
        target = self.players.get(target_id)

        # the wrapper sets all the data needed for the actions and
        # returns the action to be called at the end of the action phase

        # make sure the action is used with valid arguments
        result = action_wrapper(player, target)
        if (type(result) == str):
            return result

        player.action_function = action_wrapper(player, target)
        player.action_callback = callback
    
    def set_evidence(self, killed_player: Player, evidence: Height or Footprint or Haircolor):
        self.killed_player = killed_player
        self.evidence = evidence

    def init_game(self, bot_client):
        self.bot_client = bot_client
        self.alien_player_id = random.choice(list(self.players.keys()))

        alien_player = self.players.get(self.alien_player_id)
        alien_player.role = Role.ALIEN

        print(f"The Alien is {alien_player.user.nick} ({alien_player.user.name})")

        # choose a couple random items that can be found this game
    
    def check_game_end(self) -> None or str:
        alien_alive = False
        alive_count = 0

        for pl in list(self.players.values()):
            if pl.role == Role.ALIEN:
                alien_alive = True
            
            if pl.alive:
                alive_count += 1
        
        if (alien_alive and alive_count == 1):
            # alien wins
            return "Alien wins!"
        elif (not alien_alive):
            # humans win
            return "Humans win!"
        
        # game not ended
        return None

    async def evaluate_actions(self) -> None or str:
        print("Evaluating actions")
        players = list(self.players.values())

        # Make sure the alien's action is evaluated first so evidence is set before investigations
        alien_player = self.players.get(self.alien_player_id)

        if (alien_player.action_function):
            alien_result = alien_player.action_function(self)
            await alien_player.action_callback(alien_result)

        for pl in players:
            print(f"{pl.user.nick} ({pl.role.name}), action: {pl.action_function}")
            if (pl.role == Role.ALIEN): continue

            if (pl.action_function):
                result = pl.action_function(self)
                
                if (not pl.alive):

                    # TODO: Figure out a way to tell a player they're dead even when they don't do an action
                    # Maybe just don't tell them and rely on the global announcement?
                    result += f"\n\n# ⚠️ You were killed by {alien_player.user.nick}!"

                await pl.action_callback(result)

        for pl in players:
            pl.reset_action_state()
        
        # TODO: Announce killed player

        # return self.check_game_end()

    async def run(self):
        win_text = None

        # Run the game until the game ends itself or something manually sets the game state to ENDED
        while win_text is None or self.game_state != GameState.ENDED:
            self.game_state = GameState.ACTION_PHASE
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
            await self.bot_client.lynch_phase()

            # Check for aborts
            if self.game_state == GameState.ENDED: return
        
        print(win_text)
        await self.bot_client.stop_game(win_text)
        self.reset_game()
    
    def reset_game(self):
        self.game_state = GameState.ENDED
        self.players = dict()
