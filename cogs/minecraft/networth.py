import discord
import aiomysql
import yaml

from discord import app_commands
from discord.ext import commands
from utils import listInventory, checkPlayer, logCommand

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

class networth(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Networth command
    @app_commands.command(name="networth", description="View your item worth!")
    async def networth(self, interaction: discord.Interaction):
        await checkPlayer(self.bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                inventory = await listInventory(interaction.user.id)
                if inventory != {}:
                    description = ""
                    networth = 0
                    for item in inventory.items():
                        val_cursor = 'SELECT SellValue FROM items WHERE ItemName=%s'
                        await cursor.execute(val_cursor, (item[0],))
                        val = await cursor.fetchone()

                        buy_cursor = 'SELECT CostValue FROM items WHERE ItemName=%s'
                        await cursor.execute(buy_cursor, (item[0],))
                        buy = await cursor.fetchone()
                        
                        add = val[0]
                        add2 = buy[0]
                        networth+=add
                        networth+=add2
                        description = str(networth)
                    
                    bal_cursor = 'SELECT Coins FROM wallets WHERE UserID=%s'
                    await cursor.execute(bal_cursor, (interaction.user.id,))
                    bal_pt = await cursor.fetchone()
                    bal = bal_pt[0]
                    totalVal = networth+bal
                    
                    embed = discord.Embed(title=f"{logo_emoji} Networth", description=f"Your items are worth **${description}**\n\nYour total value is **${f"{totalVal:,}"}**", color=discord.Color.from_str(minecraft_color))
                else:
                    embed = discord.Embed(title=f"{logo_emoji} Nil Inventory", description=f"You do not have an inventory!", color=discord.Color.from_str(minecraft_color))

                await interaction.followup.send(embed=embed)

        await logCommand(interaction)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(networth(bot))
