import discord
import emoji
import yaml
import re
import aiomysql

from discord import app_commands
from discord.ext import commands
from typing import Optional
from utils import checkPlayer, hasAdmin

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = data["Roles"]["ADMIN_ROLE_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

def trueFalse(value):
    if value:
        return value, 1
    else:
        return 0, 0

def is_valid_emoji(content):
    if emoji.is_emoji(content):
        return True

    custom_emoji_pattern = re.compile(r"<a?:(\w+):(\d+)>")
    return bool(custom_emoji_pattern.match(content))

class additem(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Add Item command
    @app_commands.command(name="additem", description="Add a new item to the bot!")
    @app_commands.describe(item="The name of the item")
    @app_commands.describe(sell="The sell value of the item (optional)")
    @app_commands.describe(cost="The cost of the item (optional)")
    @app_commands.describe(emoji="The emoji of the item (optional)")
    @app_commands.describe(can_smelt="Can the item be smelted? (True/False)")
    async def additem(self, interaction: discord.Interaction, item: str, sell: Optional[int], cost: Optional[int], emoji: Optional[str], can_smelt: Optional[bool]) -> None:
        await checkPlayer(self.bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)
        if await hasAdmin(interaction):
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                    sql = 'SELECT * FROM items WHERE ItemName=%s'
                    await cursor.execute(sql, (item,))
                    item_exists = await cursor.fetchone()
                    if item_exists is None:
                    
                        sellValue, canSell = trueFalse(sell)
                        costValue, canBuy = trueFalse(cost)
                        smeltVault, canSmelt = trueFalse(can_smelt) # smeltValue is useless, don't use
                        
                        sql = 'INSERT INTO items (ItemName, SellValue, CanSell, CostValue, CanBuy, Emoji, CanSmelt) VALUES (%s,%s,%s,%s,%s,%s,%s)'
                        await cursor.execute(sql, (item, sellValue, canSell, costValue, canBuy, emoji, canSmelt))
                        await conn.commit()

                        if emoji:
                            is_valid = is_valid_emoji(emoji)
                            if not is_valid:
                                embed = discord.Embed(title=f"{logo_emoji} Invalid Emoji", description=f"**{emoji}** is not a valid emoji!", color=admin_color)
                                await interaction.followup.send(embed=embed)
                                return

                        embed = discord.Embed(title=f"{logo_emoji} Item Added", description=f"""
                                                                                Successfully added the item **{item}**!

                                                                                Sell Value: {sellValue}
                                                                                Can Sell: {canSell}
                                                                                Cost Value: {costValue}
                                                                                Can Buy: {canBuy}
                                                                                Emoji: {emoji}
                                                                                Can Smelt: {canSmelt}
                                                                                """, color=admin_color)
                    else:
                        embed = discord.Embed(title=f"{logo_emoji} Item Already Exists", description=f"**{item}** is already an item!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(additem(bot), guilds=[discord.Object(id=admin_guild_id)])