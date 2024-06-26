import discord
import yaml
import json
import aiomysql


from discord import app_commands
from discord.ext import commands
from utils import checkPlayer, convert_json_to_dict, hasAdmin

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = data["Roles"]["ADMIN_ROLE_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

class deleteitem(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="deleteitem", description="Deletes an item from the bot!")
    @app_commands.describe(item="The name of the item")
    async def deleteitem(self, interaction: discord.Interaction, item: str) -> None:
        await checkPlayer(self.bot, interaction.user.id)
        
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        if await hasAdmin(interaction):
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    item_cursor = 'SELECT * FROM items WHERE ItemName=%s'
                    await cursor.execute(item_cursor, (item,))
                    added_item = await cursor.fetchone()
                    if added_item is None:
                        embed = discord.Embed(title=f"{logo_emoji} Item Doesn't Exist", description=f"**{item}** does not exist!", color=admin_color)
                    else:
                        inv_cursor = 'SELECT * FROM inventories'
                        await cursor.execute(inv_cursor)
                        inventories = await cursor.fetchall()

                        for inventory in inventories:
                            inventory_dict = await convert_json_to_dict(inventory['Items'])
                            
                            if item in inventory_dict:
                                del inventory_dict[item]

                                inventory_json = json.dumps(inventory_dict)
                                
                                sql = 'UPDATE inventories SET Items=%s WHERE UserId=%s'
                                await cursor.execute(sql, (inventory_json, inventory['UserId']))
                                await conn.commit()

                        sql = 'DELETE FROM items WHERE ItemName=?'
                        await cursor.execute(sql, (item,))
                        await conn.commit()

                        embed = discord.Embed(title=f"{logo_emoji} Item Deleted", description=f"Successfully deleted the item **{item}**!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

    @deleteitem.autocomplete("item")
    async def removeitem_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            names = [item['ItemName'] for item in self.bot.items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(deleteitem(bot), guilds=[discord.Object(id=admin_guild_id)])