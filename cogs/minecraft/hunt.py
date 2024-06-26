import discord
import aiomysql
import asyncio
import random
import yaml
import math
import secrets
import string

from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils import addItem, removeItem, listInventory, convert_json_to_dict, checkPlayer, hasItem, logCommand

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

def generate_health(health: int):
    
    full_hearts = health // 2
    half_hearts = health % 2
    empty_hearts = 10 - full_hearts - half_hearts
    
    return (mob_full_heart_emoji * full_hearts) + (mob_half_heart_emoji * half_hearts) + (empty_heart_emoji * empty_hearts)

class hunt(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #hUNT command
    @app_commands.command(name="hunt", description="Hunt for mobs!")
    @app_commands.describe(dim="The dimension name")
    @app_commands.checks.cooldown(1, 1.0, key=lambda i: (i.guild_id, i.user.id))
    async def hunt(self, interaction: discord.Interaction, dim: str):
        await checkPlayer(self.bot, interaction.user.id) 
            
        embed = discord.Embed(title=f"{logo_emoji} Hunt", description="Loading...", color=discord.Color.from_str(minecraft_color))
        await interaction.response.send_message(embed=embed, ephemeral=True)

        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                sql = 'SELECT * FROM dimensions WHERE DimName=%s'
                if await cursor.execute(sql, (dim,)):
                    mobs_cursor = 'SELECT * FROM dimensions WHERE DimName=%s'
                    await cursor.execute(mobs_cursor, (dim,))
                    mob = await cursor.fetchone()
                    mob = await convert_json_to_dict(mob['Mobs'])

                    mobPicked = random.choice(list(mob.keys()))

                    mobStats = mob[mobPicked]
                    mobDrop = mobStats[0]
                    mobHealth = mobStats[1]

                    playerDmg = 0

                    sword_values = {
                        "Wooden Sword": 4
                    }

                    sharpness_values = {
                        "Sharpness 1": 3
                    }

                    for sword, value in sword_values.items():
                        has_sword = await hasItem(self.bot, interaction.user.id, sword)
                        if has_sword[0]:
                            playerDmg = value

                    for sharpness, value in sharpness_values.items():
                        addDmg = value
                        for sword, value in sword_values.items():
                            has_sword = await hasItem(self.bot, interaction.user.id, sword)
                            has_sharpness = await hasItem(self.bot, interaction.user.id, sharpness)
                            if has_sharpness[0] and has_sword[0]:
                                playerDmg += addDmg
                    
                    if playerDmg == 0:
                        embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"You don't have a sword! Type **/shop** to buy one!", color=discord.Color.from_str(minecraft_color))
                        await interaction.edit_original_response(embed=embed)
                        return
                    
                    while mobHealth > 0:
                        N = 3
                        randStr = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(N))

                        def check(message):
                            return message.channel == interaction.channel and message.author == interaction.user
                        
                        health = generate_health(mobHealth)
                        embed = discord.Embed(title=f"{logo_emoji} Hunt", description=f"Type `{randStr}` and send it in this channel to attack **{mobPicked}**!\n\n{health}", color=discord.Color.green())
                        await interaction.edit_original_response(embed=embed)

                        try:
                            answer = await self.bot.wait_for('message', check=check, timeout=60.0)
                        except asyncio.TimeoutError:
                            embed = discord.Embed(title=f"{logo_emoji} Hunt", description="You took too long! The mob escaped!", color=discord.Color.from_str(minecraft_color))
                            await interaction.edit_original_response(embed=embed)
                            return

                        if answer.content.upper() == randStr:
                            await answer.delete()
                            mobHealth -= playerDmg

                    if mobHealth <= 0:
                        embed = discord.Embed(title=f"{logo_emoji} Hunt", description=f"You defeated **{mobPicked}** and got **{mobDrop}**!", color=discord.Color.from_str(minecraft_color))
                        await interaction.edit_original_response(embed=embed)
                        await addItem(self.bot, interaction.user.id, mobDrop, 1)

        await logCommand(interaction)

    @hunt.autocomplete("dim")
    async def mine_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.dimensions != []:
            names = [dimension['DimName'] for dimension in self.bot.dimensions]
            if current != "":
                matches = [dimension for dimension in names if dimension.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(hunt(bot))