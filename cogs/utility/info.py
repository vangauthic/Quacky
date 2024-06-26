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

class info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Info command
    @app_commands.command(name="info", description="See a user's information. Includes a bare-bones Social Media search.")
    @app_commands.describe(member="member")
    async def info(self, interaction: discord.Interaction, member: discord.Member) -> None:
        await checkPlayer(self. bot, interaction.user.id)

        if await hasAdmin(interaction):
            socialsearch = "https://discoverprofile.com/"+member.name+"/"
            embed = discord.Embed(title=f"{logo_emoji} User Info", description=f"Avatar: {member.display_avatar.url}\nUsername: {member.name}\nNickname: {member.nick}\nID: {member.id}\nSocial Search: {socialsearch}", color=admin_color)
            await interaction.response.send_message(content=f"", embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(info(bot), guilds=[discord.Object(id=admin_guild_id)])