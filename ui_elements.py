import discord
from discord.interactions import Interaction
from classes import Player, Role, GameState
from constants import JOIN_TIME, LYNCH_TIME
from actions import ActionsEnum

# TODO: Make these views more modular

class ShootTargetSelect(discord.ui.UserSelect):
    def __init__(self, game):
        self.game = game
        super().__init__(placeholder="Target", min_values=1, max_values=1)
    
    async def callback(self, interaction: Interaction):
        target_id = self.values[0].id

        if (self.game.game_state != GameState.LYNCH_PHASE):
            await interaction.response.send_message("🚫 You can't shoot now", ephemeral=True)
            return

        if (target_id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 That player is not in the game", ephemeral=True)
            return

        target = self.game.players.get(target_id)
        self.game.shot_player = target

        await interaction.response.send_message(f"✅ You decide to shoot {self.values[0]}", ephemeral=True)

class ShootTargetSelectView(discord.ui.View):
    def __init__(self, game):
        super().__init__()
        self.add_item(ShootTargetSelect(game))

class TargetSelect(discord.ui.UserSelect):
    def __init__(self, action_item: ActionsEnum, game):
        self.action_item = action_item
        self.game = game
        super().__init__(placeholder="Select a target", min_values=1, max_values=1)
    
    async def callback(self, interaction: Interaction):
        target_id = self.values[0].id

        if (target_id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 That player is not in the game", ephemeral=True)
            return
        
        target_name = self.values[0].nick or self.values[0].name
        action = self.action_item.value

        msg = f"✅ You decide to **{action.description} {target_name}**..."

        async def result_callback(result: str):
            await interaction.edit_original_response(content=msg + f"\n\n{result}")

        # print(f"{interaction.user.nick} action: {action_wrapper}, target: {target.nick if target != None else 'None'}")
        error_text = self.game.set_player_action(
            user_id=interaction.user.id,
            action_wrapper=action.function,
            target_id=target_id,
            callback=result_callback
        )

        if (error_text is not None):
            msg = f"🚫 Action failed:\n**{error_text}**"

        await interaction.response.send_message(msg, ephemeral=True)

class TargetSelectView(discord.ui.View):
    def __init__(self, action_item: ActionsEnum, game):
        super().__init__()
        self.add_item(TargetSelect(action_item=action_item, game=game))

class ActionSelect(discord.ui.Select):
    def __init__(self, player: Player, game):

        # options = [
        #     discord.SelectOption(label=action_item.value.description, value=action_item.name) for action_item in ActionsEnum if (player.role in action_item.value.roles)
        # ]

        options = [discord.SelectOption(label="No Action", value="None")]

        for action_item in ActionsEnum:
            action = action_item.value

            if (player.role in action.roles):
                if (player.action_points < action.cost): continue
                options.append(discord.SelectOption(label=f"{action.description}", value=action_item.name))

        self.game = game
        super().__init__(placeholder="Select an action", options=options)
    
    async def callback(self, interaction: Interaction):
        if (self.game.game_state != GameState.ACTION_PHASE):
            await interaction.response.send_message("🚫 You can't set an action now", ephemeral=True)
            return

        if (self.values[0] == "None"):
            await interaction.response.send_message("✅ You decide to do nothing...", ephemeral=True)

            error_text = self.game.set_player_action(
                user_id=interaction.user.id,
                action_wrapper=None,
                target_id=None,
                callback=None
            )
            return

        action_item = ActionsEnum[self.values[0]]

        if (action_item.value.takes_target):
            await interaction.response.send_message("Select a target", ephemeral=True, view=TargetSelectView(action_item, self.game), delete_after=15)
        else:
            action = action_item.value
            msg = f"✅ You decide to **{action.description}**..."

            async def result_callback(result: str):
                await interaction.edit_original_response(content=msg + f"\n\n{result}")

            # print(f"{interaction.user.nick} action: {action_wrapper}, target: {target.nick if target != None else 'None'}")
            error_text = self.game.set_player_action(
                user_id=interaction.user.id,
                action_wrapper=action.function,
                target_id=None,
                callback=result_callback
            )

            if (error_text is not None):
                msg = f"🚫 Action failed:\n**{error_text}**"

            await interaction.response.send_message(msg, ephemeral=True)

class ActionSelectView(discord.ui.View):
    def __init__(self, *, player: Player, game):
        super().__init__()
        self.add_item(ActionSelect(player, game))

class JoinGameView(discord.ui.View):
    def __init__(self, add_player_function):
        super().__init__(timeout=JOIN_TIME)
        self.add_player_function = add_player_function
    
    @discord.ui.button(label='Join', style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        success = self.add_player_function(interaction.user)

        if (not success):
            await interaction.response.send_message("🚫 Joining failed. You might be in the game already", ephemeral=True)
            return

        await interaction.response.send_message("✅ You have joined successfully", ephemeral=True)
        print(f"{interaction.user.name} joined the game")


class ShowRoleView(discord.ui.View):
    def __init__(self, game):
        super().__init__()
        self.game = game
    
    @discord.ui.button(label='Show role', style=discord.ButtonStyle.green)
    async def show_role(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (interaction.user.id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players.get(interaction.user.id)
        
        if (player.role == Role.ALIEN):
            role_text = "You are the alien 👽"
            instruction = "Kill all humans and don't get caught 🔪"
        else:
            role_text = "You are a human 🕵️"
            instruction = "Find and eliminate the alien 👽"
        
        footprint = player.description.footprint.name.lower()
        height = player.description.height.name.lower()
        haircolor = player.description.haircolor.name.lower()
        description = f"**Your description:**\nFootprint: **{footprint}**\nHeight: **{height}**\nHaircolor: **{haircolor}**"

        await interaction.response.send_message(f"## {role_text}\n{instruction}\n\n{description}", ephemeral=True)

class ShowActionView(discord.ui.View):
    def __init__(self, game):
        super().__init__()
        self.game = game
    
    @discord.ui.button(label='Show Points', style=discord.ButtonStyle.blurple)
    async def show_action_points(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (interaction.user.id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players.get(interaction.user.id)

        if (not player.alive):
            await interaction.response.send_message("🚫 You are dead", ephemeral=True)
            return

        await interaction.response.send_message(f"You have **{player.action_points}** action points.", ephemeral=True)
    
    @discord.ui.button(label='Show Actions', style=discord.ButtonStyle.blurple)
    async def show_available_actions(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if (interaction.user.id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return
        
        player = self.game.players.get(interaction.user.id)

        if (not player.alive):
            await interaction.response.send_message("🚫 You are dead", ephemeral=True)
            return

        actions = ""
        
        for action_item in ActionsEnum:
            action = action_item.value

            if (player.role in action.roles):
                surround = "**" if (player.action_points >= action.cost) else "*"
                actions += f"{surround}{action.description}{surround}\n"
        
        await interaction.response.send_message(f"**Available actions:**\n\n{actions}\nSelect an action with the `Set Action` button.", ephemeral=True)
    
    @discord.ui.button(label='Set Action', style=discord.ButtonStyle.green)
    async def set_action(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (interaction.user.id not in self.game.players.keys()):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return

        player = self.game.players.get(interaction.user.id)

        # await interaction.response.send_modal(ActionModal())
        await interaction.response.send_message("Select an action", ephemeral=True, view=ActionSelectView(player=player, game=self.game), delete_after=15)

class ShootView(discord.ui.View):
    def __init__(self, game, gun_player: Player):
        super().__init__()
        self.game = game
        self.gun_player = gun_player
    
    @discord.ui.button(label='Shoot', style=discord.ButtonStyle.red)
    async def shoot(self, interaction: Interaction, button: discord.ui.Button):
        player = self.game.players.get(interaction.user.id)

        if (player is None):
            await interaction.response.send_message("🚫 You are not in the game", ephemeral=True)
            return
        
        if (not player.alive):
            await interaction.response.send_message("🚫 You are dead", ephemeral=True)
            return
        
        if (interaction.user.id != self.gun_player.member.id):
            await interaction.response.send_message("🚫 You don't have the gun", ephemeral=True)
            return
    
        await interaction.response.send_message("Select a target", ephemeral=True, view=ShootTargetSelectView(self.game), delete_after=15)