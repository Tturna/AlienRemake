# This is supposed to be the start of the Alien game logic
# The point is to add Discord functionality later

import random
import discord
from actions import Action
from classes import Player, Role, GameState

class Game:
    def __init__(self) -> None:
        self.game_state = GameState.ENDED
        self.players = dict()
        self.bot_client = None

    def add_player(self, user: discord.User):
        if (self.players.get(user.id) is not None):
            return False

        self.players[user.id] = Player(user)
        return True
    
    def set_player_action(self, user_id, action_wrapper, leaves_quarters, target_id):
        player = self.players.get(user_id)
        target = self.players.get(target_id)

        player.action_function = action_wrapper(target)
        player.leaving_quarters = leaves_quarters
        player.target = target

    def init_game(self, bot_client):
        self.bot_client = bot_client
        alien_player = random.choice(list(self.players.values()))
        alien_player.role = Role.ALIEN

        print(f"The Alien is {alien_player.user.nick} ({alien_player.user.name})")

        # choose a couple random items that can be found this game

    def evaluate_actions(self) -> bool:
        for pl in list(self.players.values()):
            if (pl.action_function != None):
                pl.action_function()

            pl.action_function = None
            pl.leaving_quarters = False
        
        # Check if game ended
        return False

    async def run(self):
        game_ended = False

        while game_ended == False:
            self.game_state = GameState.ACTION_PHASE
            await self.bot_client.action_phase()

            game_ended = self.evaluate_actions()

            if game_ended: break

            self.game_state = GameState.DISCUSSION_PHASE
            await self.bot_client.discussion_phase()

            self.game_state = GameState.LYNCH_PHASE
            game_ended = await self.bot_client.lynch_phase()


if __name__ == "__main__":

    # Make sure discussion is open
    # Wait for a bit
    # time.sleep(3)

    # Action phase
    print("Discussion is over. Choose your action.")
    for pl in players:
        print(f"pl({pl.id}), choose your action!")
        action_input = input("Action? (scout, hide, investigate, loot, donate, protect, use_item, kill): ")
        target_input = input("Target? (pl_id, leave empty if action doesn't require target.): ")
        action_wrapper, leaves_quarters = Action[action_input.upper()].value
        pl.leaving_quarters = leaves_quarters
        
        if target_input == "":
            pl.action_function = action_wrapper()
        else:
            # Get player with target id
            target = next((p for p in players if p.id == int(target_input)), None)
            pl.action_function = action_wrapper(target=target)

    # Evaluate actions
    # evaluate_actions(players)

    # Wait a bit
    # time.sleep(3)

    # print("Discussion started.")