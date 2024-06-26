import discord
import aiomysql
import random
import yaml

from discord import app_commands
from discord.ext import commands
from utils import addItem, convert_json_to_dict, checkPlayer, hasItem, logCommand

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

class mine(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Mine command
    @app_commands.command(name="mine", description="Mine for resources!")
    @app_commands.describe(dim="The dimension name")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def mine(self, interaction: discord.Interaction, dim: str):
       await checkPlayer(self.bot, interaction.user.id)
       async with self.bot.pool.acquire() as conn:
           async with conn.cursor(aiomysql.DictCursor) as cursor:
            userHarv = 0
            toGet = 1

            pickaxe_values = {
                "Wooden Pickaxe": 1,
                "Stone Pickaxe": 1,
                "Iron Pickaxe": 2,
                "Diamond Pickaxe": 3,
                "Netherite Pickaxe": 4
            }

            fortune_values = {
                "Fortune 1": 2,
                "Fortune 2": 3,
                "Fortune 3": 4
            }

            for pickaxe, value in pickaxe_values.items():
                    has_pickaxe = await hasItem(self.bot, interaction.user.id, pickaxe)
                    if has_pickaxe[0]:
                        userHarv = value
                
            for fortune, value in fortune_values.items():
                    has_fortune = await hasItem(self.bot, interaction.user.id, fortune)
                    if has_fortune[0]:
                        toGet = random.randint(1, value)

            block_cursor = 'SELECT Blocks FROM dimensions WHERE DimName=%s'
            await cursor.execute(block_cursor, (dim,))
            block = await cursor.fetchone()
            if block:
                print(block)
                block = random.choice(block)
                block_dict = await convert_json_to_dict(block)
                block = random.choice(list(block_dict))

                harv_cursor = 'SELECT HarvestLevel FROM items WHERE ItemName=%s'
                await cursor.execute(harv_cursor, (block,))
                harvLvl = await cursor.fetchone()

                item_cursor = 'SELECT * FROM items WHERE ItemName=%s'
                await cursor.execute(item_cursor, (block,))
                item_n = await cursor.fetchone()
                item_name = item_n['ItemName']
                
                emoji_cursor = 'SELECT Emoji FROM items WHERE ItemName=%s'
                await cursor.execute(emoji_cursor, (block,))
                emoji = await cursor.fetchone()

                if userHarv >= harvLvl[0]:
                    #jake sucks a penis YES
                    # ur gf's penis give me those emojis 💦💦💦💦
                    embed = discord.Embed(title=f"{logo_emoji} Block Mined", description=f"\n\nYou mined {toGet} {emoji[0]} **{item_name}**", color=discord.Color.from_str(minecraft_color))
                    await addItem(self.bot, interaction.user.id, item_name, toGet)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                elif userHarv == 0:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou tried to mine rocks with your hand and broke your fingers dumbass! Type **/shop** to buy a pickaxe!", color=discord.Color.from_str(minecraft_color))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou can't mine **{item_name}**! Type **/shop** to buy a better pickaxe!", color=discord.Color.from_str(minecraft_color))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                    embed = discord.Embed(title=f"{logo_emoji} Invalid Dimension", description=f"\n\nThat dimension does not exist!", color=discord.Color.from_str(minecraft_color))
                    await interaction.response.send_message(embed=embed, ephemeral=True)

       await logCommand(interaction)

    @mine.autocomplete("dim")
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
    await bot.add_cog(mine(bot))