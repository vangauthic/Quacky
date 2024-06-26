import discord
import random
import yaml
import math

from discord import app_commands
from discord.ext import commands
from utils import addItem, checkPlayer, hasItem, logCommand

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

minecraft_color = data["Embeds"]["MINECRAFT_COLOR"]
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]
empty_left_emoji = data["Emojis"]["EMPTY_LEFT_EMOJI"]
empty_middle_emoji = data["Emojis"]["EMPTY_MIDDLE_EMOJI"]
empty_right_emoji = data["Emojis"]["EMPTY_RIGHT_EMOJI"]
full_left_emoji = data["Emojis"]["FULL_LEFT_EMOJI"]
full_middle_emoji = data["Emojis"]["FULL_MIDDLE_EMOJI"]
full_right_emoji = data["Emojis"]["FULL_RIGHT_EMOJI"]
mob_full_heart_emoji = data["Emojis"]["MOB_FULL_HEART_EMOJI"]
mob_half_heart_emoji = data["Emojis"]["MOB_HALF_HEART_EMOJI"]
empty_heart_emoji = data["Emojis"]["EMPTY_HEART_EMOJI"]
rocks = data["Rocks"]
recipes = data["Recipes"]

cooldown = 30

#Tree Chop
class chopTree(discord.ui.View):
    def __init__(self, bot: commands.Bot, treeLvl: int, toChop: int):
        super().__init__()
        self.treeLvl = treeLvl
        self.toChop = toChop
        self.initialTree = toChop
        self.bot = bot

    @discord.ui.button(label='Chop', style=discord.ButtonStyle.green)
    async def chop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.toChop <= 0:
            self.toChop = 0
            await addItem(self.bot, interaction.user.id, 'Log', self.initialTree)
            main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nYou have harvested the tree and gained **{self.initialTree}** wood!', color=discord.Color.from_str(minecraft_color))
            view = chopTree(self.bot, self.treeLvl, self.toChop)
            view.chop.disabled = True
            await interaction.response.edit_message(embed=main, view=view)
        else:
            self.toChop -= self.treeLvl
            if self.toChop <= 0:
                self.toChop = 0
                await addItem(self.bot, interaction.user.id, 'Log', self.initialTree)
                main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nYou have harvested the tree and gained **{self.initialTree}** wood!', color=discord.Color.from_str(minecraft_color))
                view = chopTree(self.bot, self.treeLvl, self.toChop)
                view.chop.disabled = True
                await interaction.response.edit_message(embed=main, view=view)
            else:
                main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nPress the button below to keep chopping! Chops Left: **{self.toChop}**', color=discord.Color.from_str(minecraft_color))
                await interaction.response.edit_message(embed=main)

class chop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Chop command
    @app_commands.command(name="chop", description="Chop trees for wood!")
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.id, i.user.id))
    async def chop(self, interaction: discord.Interaction):
        await checkPlayer(self.bot, interaction.user.id)
        
        treeLvl = 1

        axe_levels = {
                'Wooden Axe': 2,
                'Stone Axe': 3,
                'Iron Axe': 4,
                'Diamond Axe': 5,
                'Netherite Axe': 6
            }

        for axe, level in axe_levels.items():
            has_axe = await hasItem(self.bot, interaction.user.id, axe)
            if has_axe[0]:
                treeLvl = level
                break

        toChop = random.randint(4, 18) * (treeLvl / 1.5)
        toChop = math.ceil(toChop)
        if toChop > 36:
            toChop = 36
        if treeLvl > 0:
            main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nPress the button below to start choppping! Chops Left: **{toChop}**', color=discord.Color.from_str(minecraft_color))
            await interaction.response.send_message(embed=main, view=chopTree(self.bot, treeLvl, toChop), ephemeral=True) #change to pretty embed later
        else:
            main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nYou need to buy an axe!', color=discord.Color.from_str(minecraft_color))
            await interaction.response.send_message(embed=main, ephemeral=True)

        await logCommand(interaction)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(chop(bot))