import discord
import aiomysql
import yaml

from discord import app_commands
from discord.ext import commands
from utils import removeItem, convert_json_to_dict, checkPlayer, logCommand

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

class sell(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Sell command
    @app_commands.command(name="sell", description="Sell your items")
    @app_commands.describe(item="The name of the item", amount="The amount to sell")
    async def sell(self, interaction: discord.Interaction, item: str, amount: int):
         await checkPlayer(self.bot, interaction.user.id)
         async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                inventory_cursor = 'SELECT * FROM inventories WHERE UserID=%s'
                await cursor.execute(inventory_cursor, (interaction.user.id,))
                inventory = await cursor.fetchone()
                if not inventory:
                    sql = 'INSERT INTO inventories (UserId) VALUES (%s)'
                    await cursor.execute(sql, (interaction.user.id,))
                    await conn.commit()
                
                sell_cursor = 'SELECT * FROM items WHERE CanSell=1 AND ItemName=%s'
                await cursor.execute(sell_cursor, (item,))
                itemVals = await cursor.fetchone()

                if itemVals:
                    inv = await convert_json_to_dict(inventory['Items'])

                    if inv[item] >= amount:
                        sellValue = itemVals['SellValue']
                        itemName = itemVals['ItemName']
                        itemEmoji = itemVals['Emoji']
                        earned = sellValue * amount

                        sql = 'UPDATE wallets SET Coins=Coins+%s WHERE UserId=%s'
                        await cursor.execute(sql, (earned, interaction.user.id))
                        await removeItem(self.bot, interaction.user.id, item, amount)
                        await conn.commit()

                        embed = discord.Embed(title=f"{logo_emoji} Item(s) Sold", description=f"You sold **{amount}** {itemEmoji} {itemName} for **${f"{earned:,}**"}", color=discord.Color.from_str(minecraft_color))
                    else:
                        embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"You do not have enough of **{item}** to sell that much!", color=discord.Color.red())
                else:
                    embed = discord.Embed(title=f"{logo_emoji} Bad Item", description=f"The item, **{item}**, does not exist!", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)

            await logCommand(interaction)

    @sell.autocomplete("item")
    async def sell_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            sellable_items = [item for item in self.bot.items if item.get('CanSell', 0) == 1]
            names = [item['ItemName'] for item in sellable_items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(sell(bot))