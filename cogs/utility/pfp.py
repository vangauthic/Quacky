import discord
import yaml

from discord import app_commands
from discord.ext import commands
from utils import checkPlayer

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = data["Roles"]["ADMIN_ROLE_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

class pfp(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #See Profile Picture command
    @app_commands.command(name="pfp", description="See a user's profile picture")
    @app_commands.describe(member="member")
    async def pfp(self, interaction: discord.Interaction, member: discord.Member) -> None:
        await checkPlayer(self. bot, interaction.user.id)
        await interaction.response.send_message(content=f"{member.display_avatar.url}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(pfp(bot), guilds=[discord.Object(id=admin_guild_id)])