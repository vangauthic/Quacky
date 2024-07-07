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

class register(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Register command
    @app_commands.command(name="register", description="Register your server with the bot!")
    @commands.has_permissions(administrator=True)
    async def register(self, interaction: discord.Interaction) -> None:
        await checkPlayer(self.bot, interaction.user.id)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                sql = "SELECT * FROM server_settings WHERE serverID = %s"
                await cursor.execute(sql, (interaction.guild.id,))
                server_settings = await cursor.fetchone()
                
                if server_settings:
                    embed = discord.Embed(title=f"Server Already Registered", 
                                  description=f"\n\nThis server is already registered with **{self.bot.user.name}**",
                                  color=admin_color)
                else:
                    sql = 'INSERT INTO server_settings (serverID) VALUES (%s)'
                    await cursor.execute(sql, (interaction.guild.id,))
                    await conn.commit()
                    embed = discord.Embed(title=f"Server Registered", 
                                  description=f"\n\nServer successfully registered with **{self.bot.user.name}**",
                                  color=admin_color)
                    
                await interaction.response.send_message(embed=embed, ephemeral=True)
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(register(bot))