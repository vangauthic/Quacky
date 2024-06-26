import discord
import aiomysql
import yaml

from discord import app_commands
from discord.ext import commands
from utils import checkPlayer, logCommand

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

class balance(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Balance command
    @app_commands.command(name="balance", description="View your balance")
    async def balance(self, interaction: discord.Interaction):
        await checkPlayer(self.bot, interaction.user.id)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                sql = 'SELECT * FROM wallets WHERE UserId=%s'
                await cursor.execute(sql, (interaction.user.id,))
                wallet = await cursor.fetchone()
                if wallet is None:
                    sql = 'INSERT INTO wallets (UserId, Coins) VALUES (%s,%s)'
                    await cursor.execute(sql, (interaction.user.id, 0))
                    await conn.commit()

                sql = 'SELECT * FROM wallets WHERE UserId=%s'
                await cursor.execute(sql, (interaction.user.id,))
                wallet = await cursor.fetchone()
                balance = wallet['Coins']

                main = discord.Embed(title=f"{logo_emoji} Wallet", description=f"You have **${f"{balance:,}"}**", color=discord.Color.from_str(minecraft_color))

        await interaction.response.send_message(embed=main, ephemeral=True)
        await logCommand(interaction)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(balance(bot))