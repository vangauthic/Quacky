import discord
import random
import yaml
import math
import asyncio

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

start = """
XXXXXX
XXXXXX
XXXXXX
XXXXXX
        """

class fish(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Fish command
    @app_commands.command(name="fish", description="Catch some fish!")
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.id, i.user.id))
    async def fish(self, interaction: discord.Interaction):
        await checkPlayer(self.bot, interaction.user.id)
        
        has_rod = await hasItem(self.bot, interaction.user.id, 'Fishing Rod')

        if has_rod[0]:
            ocean = """
                    """
            
            choices = ['<:water_fish:1258845763606286359>', '<:water:1258845762591395914>']

            for letter in start:
                if letter == 'X':
                    ocean += random.choice(choices)
                else:
                    ocean += letter

            numFish = ocean.count('<:water_fish:1258845763606286359>')
            print(numFish)
            toGet = math.ceil(numFish / 3)

            embed = discord.Embed(title=f"{logo_emoji} Fishing", description=f"Count the number of fish!", color=discord.Color.from_str(minecraft_color))
            await interaction.response.send_message(content=ocean, embed=embed, ephemeral=True)

            def check(message):
                return message.channel == interaction.channel and message.author == interaction.user
            
            try:
                answer = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                embed = discord.Embed(title=f"{logo_emoji} Fishing", description="You took too long! The fish swam away!", color=discord.Color.from_str(minecraft_color))
                await interaction.edit_original_response(embed=embed, content='')
                return
            
            if answer.content == str(numFish):
                await answer.delete()
                await addItem(self.bot, interaction.user.id, 'Raw Fish', toGet)
                embed = discord.Embed(title=f"{logo_emoji} Fishing", description=f"You caught **{toGet}** fish!", color=discord.Color.from_str(minecraft_color))
                await interaction.edit_original_response(embed=embed, content='')

        else:
            embed = discord.Embed(title=f"{logo_emoji} Fishing", description=f"You don't have a Fishing Rod! Type **/shop** to buy one!", color=discord.Color.from_str(minecraft_color))
            await interaction.response.send_message(embed=embed)
        

        await logCommand(interaction)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(fish(bot))