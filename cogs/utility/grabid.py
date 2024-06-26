import discord
import yaml

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

class grabid(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Grab ID command
    @app_commands.command(name="grabid", description="Grab a user's ID")
    @app_commands.describe(member="member")
    async def grabid(self, interaction: discord.Interaction, member: discord.Member) -> None:
        await checkPlayer(self. bot, interaction.user.id)

        if await hasAdmin(interaction):
            userid = member.id
            await interaction.response.send_message(content=f"<@{userid}> ID: {userid}", ephemeral=True)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(grabid(bot), guilds=[discord.Object(id=admin_guild_id)])