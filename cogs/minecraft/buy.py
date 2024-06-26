import discord
import aiomysql
import yaml

from discord import app_commands
from discord.ext import commands
from utils import addItem, checkPlayer, logCommand

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

class buy(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Buy command
    @app_commands.command(name="buy", description="Buy new items and upgrades!")
    @app_commands.describe(item="The name of the item", amount="The amount to buy")
    async def buy(self, interaction: discord.Interaction, item: str, amount: int):
        await checkPlayer(self.bot, interaction.user.id)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                item_cursor = 'SELECT * FROM items WHERE ItemName=%s AND CanBuy=1'
                await cursor.execute(item_cursor, (item,))
                point = await cursor.fetchone()
                
                if point:
                    cost = point['CostValue'] * amount
                    emoji = point['Emoji']

                    wallet_cursor = 'SELECT * FROM wallets WHERE UserId=%s'
                    await cursor.execute(wallet_cursor, (interaction.user.id,))
                    bal_point = await cursor.fetchone()

                    if bal_point:
                        balance = bal_point['Coins']

                        if balance >= cost:
                            await addItem(self.bot, interaction.user.id, item, amount)
                            
                            sql = 'UPDATE wallets SET Coins=Coins-%s WHERE UserId=%s'
                            await cursor.execute(sql, (cost, interaction.user.id))
                            await conn.commit()

                            description = f"\n\nSuccessfully purchased **{amount}** {emoji} {item.capitalize()} for ${f"{cost:,}"}!" if emoji else f"\n\nSuccessfully purchased **{amount}** {item.capitalize()} for ${cost}!"
                            embed = discord.Embed(title=f"{logo_emoji} Purchased Item", description=description, color=discord.Color.from_str(minecraft_color))
                        else:
                            embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description="You do not have enough funds!", color=discord.Color.from_str(minecraft_color))
                    else:
                        embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description="You do not have enough funds!", color=discord.Color.from_str(minecraft_color))
                else:
                    embed = discord.Embed(title=f"{logo_emoji} Bad Item", description=f"The item, **{item}**, does not exist!", color=discord.Color.red())

                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await logCommand(interaction)

    @buy.autocomplete("item")
    async def buy_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            buyable_items = [item for item in self.bot.items if item.get('CanBuy', 0) == 1]
            names = [item['ItemName'] for item in buyable_items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(buy(bot))