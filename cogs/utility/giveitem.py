import discord
import yaml

from discord import app_commands
from discord.ext import commands
from utils import addItem, checkPlayer, hasAdmin

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = data["Roles"]["ADMIN_ROLE_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

class giveitem(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="giveitem", description="Give an item to a player!")
    @app_commands.describe(member="The player to give to")
    @app_commands.describe(item="The name of the item")
    @app_commands.describe(amount="The amount to give")
    async def giveitem(self, interaction: discord.Interaction, member: discord.Member, item: str, amount: int) -> None:
        await checkPlayer(self.bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            given_item = await addItem(self.bot, member.id, item, amount)
            if given_item:
                embed = discord.Embed(title=f"{logo_emoji} Item Given", description=f"Successfully gave the item **{item}** to **{member.name}**!", color=admin_color)
            else:
                embed = discord.Embed(title=f"{logo_emoji} Item Give Failure", description=f"**{item}** doesn't exist!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

    @giveitem.autocomplete("item")
    async def giveitem_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            names = [item['ItemName'] for item in self.bot.items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(giveitem(bot), guilds=[discord.Object(id=admin_guild_id)])