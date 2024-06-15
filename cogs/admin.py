import discord
import aiosqlite
import emoji
import yaml
import json
import re
import types
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional
from utils import addItem, removeItem, listInventory, checkPlayer, convert_json_to_dict, hasAdmin

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = data["Roles"]["ADMIN_ROLE_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

def trueFalse(value):
    if value:
        return value, 1
    else:
        return 0, 0

def is_valid_emoji(content):
    if emoji.is_emoji(content):
        return True

    custom_emoji_pattern = re.compile(r"<a?:(\w+):(\d+)>")
    return bool(custom_emoji_pattern.match(content))

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def cog_load(self):
        self.itemsCache.start()
        self.dimensionsCache.start()

    @tasks.loop(seconds = 30)
    async def itemsCache(self):
        async with aiosqlite.connect('quacky.db') as db:
            cursor = await db.execute('SELECT * FROM items')
            items = await cursor.fetchall()
            
            column_names = [description[0] for description in cursor.description]
            
            items_list = []
            for row in items:
                item_dict = dict(zip(column_names, row))
                items_list.append(item_dict)

            self.bot.items = items_list

    @itemsCache.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=30)
    async def dimensionsCache(self):
        async with aiosqlite.connect('quacky.db') as db:
            cursor = await db.execute('SELECT * FROM dimensions')
            dimensions = await cursor.fetchall()
            
            dimensions_list = [{'DimId': dimension[0], 'DimName': dimension[1]} for dimension in dimensions]
            
            self.bot.dimensions = dimensions_list

    @dimensionsCache.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()

    #Clear command
    @app_commands.command(name="clear", description="Clear messages")
    @app_commands.describe(clear="clear")
    async def clear(self, interaction: discord.Interaction, clear: int) -> None:
        await checkPlayer(interaction.user.id)

        if await hasAdmin(interaction):
            toclear = clear
            await interaction.channel.purge(limit=toclear)
            userid = interaction.user.id

            embed = discord.Embed(title=f"{logo_emoji} Messages Cleared", description=f"{toclear} messages cleared by <@{userid}>.", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    #Grab ID command
    @app_commands.command(name="grabid", description="Grab a user's ID")
    @app_commands.describe(member="member")
    async def grabid(self, interaction: discord.Interaction, member: discord.Member) -> None:
        await checkPlayer(interaction.user.id)

        if await hasAdmin(interaction):
            userid = member.id
            await interaction.response.send_message(content=f"<@{userid}> ID: {userid}", ephemeral=True)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    #See Profile Picture command
    @app_commands.command(name="pfp", description="See a user's profile picture")
    @app_commands.describe(member="member")
    async def pfp(self, interaction: discord.Interaction, member: discord.Member) -> None:
        await checkPlayer(interaction.user.id)
        await interaction.response.send_message(content=f"{member.display_avatar.url}")

    #Info command
    @app_commands.command(name="info", description="See a user's information. Includes a bare-bones Social Media search.")
    @app_commands.describe(member="member")
    async def info(self, interaction: discord.Interaction, member: discord.Member) -> None:
        await checkPlayer(interaction.user.id)

        if await hasAdmin(interaction):
            socialsearch = "https://discoverprofile.com/"+member.name+"/"
            embed = discord.Embed(title=f"{logo_emoji} User Info", description=f"Avatar: {member.display_avatar.url}\nUsername: {member.name}\nNickname: {member.nick}\nID: {member.id}\nSocial Search: {socialsearch}", color=admin_color)
            await interaction.response.send_message(content=f"", embed=embed, ephemeral=True)

    #Add Item command
    @app_commands.command(name="additem", description="Add a new item to the bot!")
    @app_commands.describe(item="The name of the item")
    @app_commands.describe(sell="The sell value of the item (optional)")
    @app_commands.describe(cost="The cost of the item (optional)")
    @app_commands.describe(emoji="The emoji of the item (optional)")
    @app_commands.describe(can_smelt="Can the item be smelted? (True/False)")
    async def additem(self, interaction: discord.Interaction, item: str, sell: Optional[int], cost: Optional[int], emoji: Optional[str], can_smelt: Optional[bool]) -> None:
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                
                cursor = await db.execute('SELECT * FROM items WHERE ItemName=?', (item,))
                item_exists = await cursor.fetchone()
                if item_exists is None:
                
                    sellValue, canSell = trueFalse(sell)
                    costValue, canBuy = trueFalse(cost)
                    smeltVault, canSmelt = trueFalse(can_smelt) # smeltValue is useless, don't use
                    
                    await db.execute('INSERT INTO items (ItemName, SellValue, CanSell, CostValue, CanBuy, Emoji, CanSmelt) VALUES (?,?,?,?,?,?,?)', (item, sellValue, canSell, costValue, canBuy, emoji, canSmelt))
                    await db.commit()

                    if emoji:
                        is_valid = is_valid_emoji(emoji)
                        if not is_valid:
                            embed = discord.Embed(title=f"{logo_emoji} Invalid Emoji", description=f"**{emoji}** is not a valid emoji!", color=admin_color)
                            await interaction.followup.send(embed=embed)
                            return

                    embed = discord.Embed(title=f"{logo_emoji} Item Added", description=f"""
Successfully added the item **{item}**!

Sell Value: {sellValue}
Can Sell: {canSell}
Cost Value: {costValue}
Can Buy: {canBuy}
Emoji: {emoji}
Can Smelt: {canSmelt}
""", color=admin_color)
                else:
                    embed = discord.Embed(title=f"{logo_emoji} Item Already Exists", description=f"**{item}** is already an item!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="deleteitem", description="Deletes an item from the bot!")
    @app_commands.describe(item="The name of the item")
    async def deleteitem(self, interaction: discord.Interaction, item: str) -> None:
        await checkPlayer(interaction.user.id)
        
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                cursor = await db.execute('SELECT * FROM items WHERE ItemName=?', (item,))
                added_item = await cursor.fetchone()
                if added_item is None:
                    embed = discord.Embed(title=f"{logo_emoji} Item Doesn't Exist", description=f"**{item}** does not exist!", color=admin_color)
                else:
                    cursor = await db.execute('SELECT * FROM inventories')
                    inventories = await cursor.fetchall()

                    for inventory in inventories:
                        inventory_dict = await convert_json_to_dict(inventory[2])
                        
                        if item in inventory_dict:
                            del inventory_dict[item]

                            inventory_json = json.dumps(inventory_dict)
                            
                            await db.execute("UPDATE inventories SET Items=? WHERE UserId=?", (inventory_json, inventory[1]))
                            await db.commit()

                    await db.execute('DELETE FROM items WHERE ItemName=?', (item,))
                    await db.commit()

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
    
    @app_commands.command(name="takeitem", description="Take an item from a player!")
    @app_commands.describe(member="The player to take from")
    @app_commands.describe(item="The name of the item")
    @app_commands.describe(amount="The amount to take")
    async def takeitem(self, interaction: discord.Interaction, member: discord.Member, item: str, amount: int) -> None:
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            removed_item = await removeItem(member.id, item, amount)
            if removed_item:
                embed = discord.Embed(title=f"{logo_emoji} Item Removed", description=f"Successfully took the item **{item}** from **{member.name}**!", color=admin_color)
            else:
                embed = discord.Embed(title=f"{logo_emoji} Item Removal Failure", description=f"**{item}** doesn't exist!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

    @takeitem.autocomplete("item")
    async def takeitem_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            names = [item['ItemName'] for item in self.bot.items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

    @app_commands.command(name="giveitem", description="Give an item to a player!")
    @app_commands.describe(member="The player to give to")
    @app_commands.describe(item="The name of the item")
    @app_commands.describe(amount="The amount to give")
    async def giveitem(self, interaction: discord.Interaction, member: discord.Member, item: str, amount: int) -> None:
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            given_item = await addItem(member.id, item, amount)
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

    @app_commands.command(name="invsee", description="Check a player's inventory!")
    @app_commands.describe(member="The player to give to")
    async def invsee(self, interaction: discord.Interaction, member: discord.Member) -> None:
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                inventory = await listInventory(member.id)
                if inventory != {}:
                    description = ""
                    for item, quantity in inventory.items():
                        emoji_cursor = await db.execute('SELECT Emoji FROM items WHERE ItemName=?', (item,))
                        emoji = await emoji_cursor.fetchone()

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

    @app_commands.command(name="givecoins", description="Gives a player coins!")
    @app_commands.describe(member="The player to give to")
    async def givecoins(self, interaction: discord.Interaction, member: discord.Member, amount: int) -> None:
        await checkPlayer(member.id)

        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                await db.execute('UPDATE wallets SET Coins=Coins+? WHERE UserId=?', (amount, member.id))
                await db.commit()

                embed = discord.Embed(title=f"{logo_emoji} Coins Added", description=f"Successfully gave {member.mention} **${amount}**!", color=admin_color)
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="takecoins", description="Takes a player's coins!")
    @app_commands.describe(member="The player to take from")
    async def takecoins(self, interaction: discord.Interaction, member: discord.Member, amount: int) -> None:
        await checkPlayer(member.id)

        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                await db.execute('UPDATE wallets SET Coins=Coins-? WHERE UserId=?', (amount, member.id))
                await db.commit()

                embed = discord.Embed(title=f"{logo_emoji} Coins Taken", description=f"Successfully took **${amount}** from {member.mention}!", color=admin_color)
                await interaction.response.send_message(embed=embed, ephemeral=True)

    #Erase a table from a DB, good for resets.
    @app_commands.command(name="erasetable", description="Remove a table from a database!")
    @app_commands.describe(database="The database to remove from")
    @app_commands.describe(table="The table to remove")
    async def erasedb(self, interaction: discord.Interaction, database: str, table: str) -> None:
        await checkPlayer(interaction.user.id)
        if await hasAdmin(interaction):
            async with aiosqlite.connect(f'{database}.db') as db:
                if db:
                    dropped = await db.execute(f'DROP TABLE IF EXISTS {table}')
                    if dropped:
                        embed = discord.Embed(title=f"{logo_emoji} Table Dropped", description=f"Successfully dropped **{table}** from **{database}**", color=admin_color)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(title=f"{logo_emoji} Invalid Database", description=f"The database {database} does not exist!", color=admin_color)
                    await interaction.response.send_message(embed=embed, ephemeral=True)

    #Fucking Quack Bitch
    @app_commands.command(name="quack", description="Annoy everyone.")
    @app_commands.describe(amount="The times to send quack GIF")
    async def quack(self, interaction: discord.Interaction, amount: int) -> None:
        if await hasAdmin(interaction):
            if amount > 69:
                amount = 69
            for x in range(amount):
                await interaction.channel.send(content='https://tenor.com/view/quack-gif-19489985')

class DimensionCog(commands.GroupCog, name="dimension"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="create", description="Create a dimension!")
    @app_commands.describe(name="The dimension name")
    async def dimension_create(self, interaction: discord.Interaction, name: str) -> None:
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                cursor = await db.execute('SELECT * FROM dimensions WHERE DimName=?', (name,))
                dimension = await cursor.fetchone()
                if dimension is None:
                    await db.execute('INSERT INTO dimensions (DimName) VALUES (?)', (name,))
                    await db.commit()

                    embed = discord.Embed(title=f"{logo_emoji} Dimension Created", description=f"The dimension **{name}** has been created!", color=admin_color)
                else:
                    embed = discord.Embed(title=f"{logo_emoji} Dimension Already Exists", description=f"The dimension **{name}** already exists!", color=admin_color)
        else:
            embed = discord.Embed(title=f"{logo_emoji} No Permission", description="You do not have permission to use this command!", color=admin_color)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="remove", description="Removes a dimension!")
    @app_commands.describe(name="The dimension name")
    async def dimension_remove(self, interaction: discord.Interaction, name: str) -> None:
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                cursor = await db.execute('SELECT * FROM dimensions WHERE DimName=?', (name,))
                dimension = await cursor.fetchone()
                if dimension is None:
                    embed = discord.Embed(title=f"{logo_emoji} Dimension Doesn't Exist", description=f"The dimension **{name}** doesn't exist!", color=admin_color)
                else:
                    await db.execute('DELETE FROM dimensions WHERE DimName=?', (name,))
                    await db.commit()

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
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                cursor = await db.execute('SELECT * FROM dimensions WHERE DimName=?', (name,))
                dimension = await cursor.fetchone()
                if dimension is None:
                    embed = discord.Embed(title=f"{logo_emoji} Dimension Doesn't Exist", description=f"The dimension **{name}** doesn't exist!", color=admin_color)
                else:
                    cursor = await db.execute('SELECT * FROM items WHERE ItemName=?', (item,))
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
                            await db.execute("UPDATE dimensions SET Blocks=? WHERE DimName=?", (block_json, name))
                            await db.commit()
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
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await hasAdmin(interaction):
            async with aiosqlite.connect('quacky.db') as db:
                cursor = await db.execute('SELECT * FROM dimensions WHERE DimName=?', (name,))
                dimension = await cursor.fetchone()
                if dimension is None:
                    embed = discord.Embed(title=f"{logo_emoji} Dimension Doesn't Exist", description=f"The dimension **{name}** doesn't exist!", color=admin_color)
                else:
                    cursor = await db.execute('SELECT * FROM items WHERE ItemName=?', (drop,))
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
                            await db.execute("UPDATE dimensions SET Mobs=? WHERE DimName=?", (mob_json, name))
                            await db.commit()
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
    await bot.add_cog(Admin(bot), guilds=[discord.Object(id=admin_guild_id)])
    await bot.add_cog(DimensionCog(bot), guilds=[discord.Object(id=admin_guild_id)])