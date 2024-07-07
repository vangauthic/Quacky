import discord
import aiomysql
import yaml

from discord import app_commands
from discord.ext import commands
from utils import checkPlayer, logCommand, checkServer

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

class shop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Shop command - completed by someone - 05/27/2024 - refined by andrew 05/28/2024
    @app_commands.command(name="shop", description="Buy new items and upgrades!")
    async def shop(self, interaction: discord.Interaction):
        if await checkServer(self.bot, interaction.guild.id):
            await checkPlayer(self.bot, interaction.user.id)
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    shop_cursor = 'SELECT * FROM items WHERE CanBuy=1'
                    await cursor.execute(shop_cursor)
                    shop_inventory = await cursor.fetchall()

                    description = ""
                    for inventory in shop_inventory:
                        if inventory['Emoji'] != "":
                            description += f"{inventory['Emoji']} **{inventory['ItemName']}**: ${f"{inventory['CostValue']:,}"}\n"
                        else:
                            description += f"**{inventory['ItemName']}**: ${f"{inventory['CostValue']:,}"}\n"

                    embed = discord.Embed(title=f"Shop Items", description=description, color=discord.Color.from_str(minecraft_color))
                    embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            
            await logCommand(interaction)
        else:
            embed = discord.Embed(title=f"Game Disabled",
                                  description="This server currently has the Quacky-3000 Minigame disabled.",
                                  color=discord.Color.red())
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(shop(bot))