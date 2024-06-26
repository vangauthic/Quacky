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

class DimensionCog(commands.GroupCog, name="dimension"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="create", description="Create a dimension!")
    @app_commands.describe(name="The dimension name")
    async def dimension_create(self, interaction: discord.Interaction, name: str) -> None:
        await checkPlayer(self. bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    dim_cursor = 'SELECT * FROM dimensions WHERE DimName=%s'
                    await cursor.execute(dim_cursor, (name,))
                    dimension = await cursor.fetchone()
                    if dimension is None:
                        sql = 'INSERT INTO dimensions (DimName) VALUES (%s)'
                        await cursor.execute(sql, (name,))
                        await conn.commit()

                        embed = discord.Embed(title=f"{logo_emoji} Dimension Created", description=f"The dimension **{name}** has been created!", color=admin_color)
                    else:
                        embed = discord.Embed(title=f"{logo_emoji} Dimension Already Exists", description=f"The dimension **{name}** already exists!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="remove", description="Removes a dimension!")
    @app_commands.describe(name="The dimension name")
    async def dimension_remove(self, interaction: discord.Interaction, name: str) -> None:
        await checkPlayer(self. bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    dim_cursor = 'SELECT * FROM dimensions WHERE DimName=%s'
                    await cursor.execute(dim_cursor, (name,))
                    dimension = await cursor.fetchone()
                    if dimension is None:
                        embed = discord.Embed(title=f"{logo_emoji} Dimension Doesn't Exist", description=f"The dimension **{name}** doesn't exist!", color=admin_color)
                    else:
                        sql = 'DELETE FROM dimensions WHERE DimName=%s'
                        await cursor.execute(sql, (name,))
                        await conn.commit()

                        embed = discord.Embed(title=f"{logo_emoji} Dimension Removed", description=f"The dimension **{name}** has been removed!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

    @dimension_remove.autocomplete("name")
    async def dimension_remove_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.dimensions != []:
            names = [dimension['DimName'] for dimension in self.bot.dimensions]
            if current != "":
                matches = [dimension for dimension in names if dimension.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

    @app_commands.command(name="addblock", description="Adds a block to a dimension")
    @app_commands.describe(name="The dimension name")
    @app_commands.describe(item="The item name")
    async def dimension_addblock(self, interaction: discord.Interaction, name: str, item: str) -> None:
        await checkPlayer(self. bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    dim_cursor = 'SELECT * FROM dimensions WHERE DimName=%s'
                    await cursor.execute(dim_cursor, (name,))
                    dimension = await cursor.fetchone()
                    if dimension is None:
                        embed = discord.Embed(title=f"{logo_emoji} Dimension Doesn't Exist", description=f"The dimension **{name}** doesn't exist!", color=admin_color)
                    else:
                        item_cursor = 'SELECT * FROM items WHERE ItemName=%s'
                        await cursor.execute(item_cursor, (item,))
                        item = await cursor.fetchone()
                        if item is None:
                            embed = discord.Embed(title=f"{logo_emoji} Item Doesn't Exist", description=f"**{item}** doesn't exist!", color=admin_color)
                            await interaction.followup.send(embed=embed)
                        else:
                            block_dict = await convert_json_to_dict(dimension[2])

                            if item[1] in block_dict:
                                embed = discord.Embed(title=f"{logo_emoji} Block Already In Dimension", description=f"**{item}** already exsists in the dimension **{name}**!", color=admin_color)
                                await interaction.followup.send(embed=embed)
                            else:
                                block_dict[item[1]] = item[0]
                                block_json = json.dumps(block_dict)
                                sql = 'UPDATE dimensions SET Blocks=%s WHERE DimName=%s'
                                await cursor.execute(sql, (block_json, name))
                                await conn.commit()
                                embed = discord.Embed(title=f"{logo_emoji} Block Added", description=f"**{item}** has been added to the dimension **{name}**!", color=admin_color)
                                await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
            await interaction.followup.send(embed=embed)

    @dimension_addblock.autocomplete("name")
    async def dimension_addblock_name_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.dimensions != []:
            names = [dimension['DimName'] for dimension in self.bot.dimensions]
            if current != "":
                matches = [dimension for dimension in names if dimension.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]
    
    @dimension_addblock.autocomplete("item")
    async def dimension_addblock_item_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            names = [item['ItemName'] for item in self.bot.items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]
    
    @app_commands.command(name="addmob", description="Adds a mob to a dimension")
    @app_commands.describe(name="The dimension name")
    @app_commands.describe(mob="The mob name")
    @app_commands.describe(drop="The item the mob drops")
    @app_commands.describe(health="The mob health")
    async def dimension_addmob(self, interaction: discord.Interaction, name: str, mob: str, drop: str, health: int) -> None:
        await checkPlayer(self. bot, interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    dim_cursor = 'SELECT * FROM dimensions WHERE DimName=%s'
                    await cursor.execute(dim_cursor, (name,))
                    dimension = await cursor.fetchone()
                    if dimension is None:
                        embed = discord.Embed(title=f"{logo_emoji} Dimension Doesn't Exist", description=f"The dimension **{name}** doesn't exist!", color=admin_color)
                    else:
                        item_cursor = 'SELECT * FROM items WHERE ItemName=%s'
                        await cursor.execute(item_cursor, (drop,))
                        item = await cursor.fetchone()
                        if item is None:
                            embed = discord.Embed(title=f"{logo_emoji} Item Doesn't Exist", description=f"**{drop}** doesn't exist!", color=admin_color)
                            await interaction.followup.send(embed=embed)
                        else:
                            mob_dict = await convert_json_to_dict(dimension[3])

                            if mob in mob_dict:
                                embed = discord.Embed(title=f"{logo_emoji} Mob Already In Dimension", description=f"**{mob}** already exsists in the dimension **{name}**!", color=admin_color)
                                await interaction.followup.send(embed=embed)
                            else:
                                mob_dict[mob] = [drop, health]
                                mob_json = json.dumps(mob_dict)
                                sql = 'UPDATE dimensions SET Mobs=%s WHERE DimName=%s'
                                await cursor.execute(sql, (mob_json, name))
                                await conn.commit()
                                embed = discord.Embed(title=f"{logo_emoji} Mob Added", description=f"**{mob}** has been added to the dimension **{name}**!", color=admin_color)
                                await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
            await interaction.followup.send(embed=embed)

    @dimension_addmob.autocomplete("name")
    async def dimension_addblock_name_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.dimensions != []:
            names = [dimension['DimName'] for dimension in self.bot.dimensions]
            if current != "":
                matches = [dimension for dimension in names if dimension.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]
    
    @dimension_addmob.autocomplete("drop")
    async def dimension_addblock_item_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            names = [item['ItemName'] for item in self.bot.items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DimensionCog(bot), guilds=[discord.Object(id=admin_guild_id)])