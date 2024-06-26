import discord
import yaml
import aiomysql

from discord import app_commands
from discord.ext import commands
from utils import checkPlayer, hasAdmin

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = data["Roles"]["ADMIN_ROLE_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

class givecoins(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="givecoins", description="Gives a player coins!")
    @app_commands.describe(member="The player to give to")
    async def givecoins(self, interaction: discord.Interaction, member: discord.Member, amount: int) -> None:
        await checkPlayer(self.bot, member.id)

        if await hasAdmin(interaction):
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    
                    sql = 'UPDATE wallets SET Coins=Coins+%s WHERE UserId=%s'
                    await cursor.execute(sql, (amount, member.id))
                    await conn.commit()

                    embed = discord.Embed(title=f"{logo_emoji} Coins Added", description=f"Successfully gave {member.mention} **${amount}**!", color=admin_color)
                    await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(givecoins(bot), guilds=[discord.Object(id=admin_guild_id)])