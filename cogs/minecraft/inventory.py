import discord
import aiomysql
import yaml

from discord import app_commands
from discord.ext import commands
from utils import listInventory, checkPlayer, logCommand

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

class inventory(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Inventory command
    @app_commands.command(name="inventory", description="View your items!")
    async def inventory(self, interaction: discord.Interaction):
        await checkPlayer(self.bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                inventory = await listInventory(self.bot, interaction.user.id)
                if inventory != {}:
                    description = ""
                    for item, quantity in inventory.items():
                        sql = 'SELECT Emoji FROM items WHERE ItemName=%s'
                        await cursor.execute(sql, (item,))
                        emoji = await cursor.fetchone() #misclick of hell, but /inventory works now

                        if emoji:
                            description += f"{emoji['Emoji']} **{item}**: {quantity}\n"
                        else:
                            description += f"**{item}**: {quantity}\n"
                    
                    embed = discord.Embed(title=f"{logo_emoji} Inventory", description=description, color=discord.Color.from_str(minecraft_color))
                else:
                    embed = discord.Embed(title=f"{logo_emoji} Nil Inventory", description=f"You do not have an inventory!", color=discord.Color.from_str(minecraft_color))

                await interaction.followup.send(embed=embed)

        await logCommand(interaction)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(inventory(bot))