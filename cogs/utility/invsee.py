import discord
import yaml
import aiomysql

from discord import app_commands
from discord.ext import commands
from utils import listInventory, checkPlayer, hasAdmin

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = data["Roles"]["ADMIN_ROLE_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

class invsee(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="invsee", description="Check a player's inventory!")
    @app_commands.describe(member="The player to give to")
    async def invsee(self, interaction: discord.Interaction, member: discord.Member) -> None:
        await checkPlayer(self. bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    inventory = await listInventory(member.id)
                    if inventory != {}:
                        description = ""
                        for item, quantity in inventory.items():
                            emoji_cursor = 'SELECT Emoji FROM items WHERE ItemName=%s'
                            await cursor.execute(emoji_cursor, (item,))
                            emoji = await cursor.fetchone()

                            if emoji[0] != '':
                                description += f"{emoji[0]} **{item}**: {f"{quantity:,}"}\n"
                            else:
                                description += f"**{item}**: {quantity}\n"
                        
                        embed = discord.Embed(title=f"{logo_emoji} {member.name}'s ||({member.id})|| Inventory", description=description, color=admin_color)
                    else:
                        embed = discord.Embed(title=f"{logo_emoji} Nil Inventory", description=f"**{member.name}** does not have an inventory!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(invsee(bot), guilds=[discord.Object(id=admin_guild_id)])