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

def trueFalse(inp):
    if inp == True:
        return 1
    elif inp == False:
        return 0

class settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Settings command
    @app_commands.command(name="settings", description="Customize the server settings for the bot!")
    @app_commands.describe(enabled="Enable/Disable the bot on this server")
    @app_commands.describe(game_channel="The channel the bot uses for game announcements")
    @commands.has_permissions(administrator=True)
    async def settings(self, interaction: discord.Interaction, enabled: Optional[bool], game_channel: Optional[discord.TextChannel]) -> None:
        await checkPlayer(self.bot, interaction.user.id)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                sql = "SELECT * FROM server_settings WHERE serverID = %s"
                await cursor.execute(sql, (interaction.guild.id,))
                server_settings = await cursor.fetchone()
                
                if server_settings:
                    isEnabled = trueFalse(enabled)
                    sql = "UPDATE server_settings SET enabled=%s, botChannel=%s WHERE serverID = %s"
                    await cursor.execute(sql, (isEnabled, game_channel.id, interaction.guild.id))
                    await conn.commit()
                    embed = discord.Embed(title=f"Server Settings Updated", 
                                  description=f"\n\nYou have toggled the bot to: **{str(enabled)}**.\nYou have changed the game channel to: {game_channel.mention}",
                                  color=admin_color)
                else:
                    embed = discord.Embed(title=f"Server Missing", 
                                  description=f"\n\nCould not find this server in the database.",
                                  color=admin_color)
                    
                await interaction.response.send_message(embed=embed, ephemeral=True)
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(settings(bot))