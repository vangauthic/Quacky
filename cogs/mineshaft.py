import discord
import aiosqlite
import asyncio
import random
import yaml
import math
import secrets
import string
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils import addItem, removeItem, listInventory, convert_json_to_dict, checkPlayer, hasItem, logCommand

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

def generate_progress_bar(percentage: int):

    total_segments = 15
    filled_segments = int((percentage / 100) * total_segments)

    progress_bar = ""

    progress_bar += full_left_emoji if filled_segments > 0 else empty_left_emoji

    for _ in range(1, total_segments - 1):
        if filled_segments > 0:
            progress_bar += full_middle_emoji
            filled_segments -= 1
        else:
            progress_bar += empty_middle_emoji

    progress_bar += full_right_emoji if filled_segments > 0 else empty_right_emoji

    return progress_bar

def generate_health(health: int):
    
    full_hearts = health // 2
    half_hearts = health % 2
    empty_hearts = 10 - full_hearts - half_hearts
    
    return (mob_full_heart_emoji * full_hearts) + (mob_half_heart_emoji * half_hearts) + (empty_heart_emoji * empty_hearts)

#Crafting Table View
class Craft(discord.ui.View):
    def __init__(self, item):
        super().__init__()
        self.item = item

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiosqlite.connect('quacky.db') as db:
            inventory = await listInventory(interaction.user.id)

            reqItems = data['Recipes'][self.item]
            
            required_items_count = {}
            for item in reqItems:
                item_name = list(item.keys())[0]
                if item_name == "":
                    continue
                else:
                    if item_name in required_items_count:
                        required_items_count[item_name] += 1
                    else:
                        required_items_count[item_name] = 1
            
            has_all_items = True
            for item, count in required_items_count.items():
                if inventory.get(item, 0) < count:
                    has_all_items = False
                    break
            
            if has_all_items:
                for item, count in required_items_count.items():
                    await removeItem(interaction.user.id, item, count) #let's test
                
                await addItem(interaction.user.id, self.item, 1)

                embed = discord.Embed(title=f"{logo_emoji} Item Crafted", description=f"Successfully crafted **{self.item}**!", color=discord.Color.from_str(minecraft_color))
            else:
                embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"You do not have the required items to craft **{self.item}**!", color=discord.Color.from_str(minecraft_color))

            await interaction.response.edit_message(embed=embed, view=None)

    #Cancel Button
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        main = discord.Embed(title=f"{logo_emoji} Crafting Table", description=f"Recipe cancelled.", color=discord.Color.from_str(minecraft_color))

        await interaction.response.send_message(embed=main, ephemeral=True)
        return

#Tree Chop
class chopTree(discord.ui.View):
    def __init__(self, treeLvl: int, toChop: int):
        super().__init__()
        self.treeLvl = treeLvl
        self.toChop = toChop
        self.initialTree = toChop

    @discord.ui.button(label='Chop', style=discord.ButtonStyle.green)
    async def chop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.toChop <= 0:
            self.toChop = 0
            await addItem(interaction.user.id, 'Log', self.initialTree)
            main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nYou have harvested the tree and gained **{self.initialTree}** wood!', color=discord.Color.from_str(minecraft_color))
            view = chopTree(self.treeLvl, self.toChop)
            view.chop.disabled = True
            await interaction.response.edit_message(embed=main, view=view)
        else:
            self.toChop -= self.treeLvl
            if self.toChop <= 0:
                self.toChop = 0
                await addItem(interaction.user.id, 'Log', self.initialTree)
                main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nYou have harvested the tree and gained **{self.initialTree}** wood!', color=discord.Color.from_str(minecraft_color))
                view = chopTree(self.treeLvl, self.toChop)
                view.chop.disabled = True
                await interaction.response.edit_message(embed=main, view=view)
            else:
                main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nPress the button below to keep chopping! Chops Left: **{self.toChop}**', color=discord.Color.from_str(minecraft_color))
                await interaction.response.edit_message(embed=main)

class Mineshaft(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Inventory command
    @app_commands.command(name="inventory", description="View your items!")
    async def inventory(self, interaction: discord.Interaction):
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)
        async with aiosqlite.connect('quacky.db') as db:
            inventory = await listInventory(interaction.user.id)
            if inventory != {}:
                description = ""
                for item, quantity in inventory.items():
                    emoji_cursor = await db.execute('SELECT Emoji FROM items WHERE ItemName=?', (item,))
                    emoji = await emoji_cursor.fetchone()

                    if emoji[0] != '':
                        description += f"{emoji[0]} **{item}**: {quantity}\n"
                    else:
                        description += f"**{item}**: {quantity}\n"
                
                embed = discord.Embed(title=f"{logo_emoji} Inventory", description=description, color=discord.Color.from_str(minecraft_color))
            else:
                embed = discord.Embed(title=f"{logo_emoji} Nil Inventory", description=f"You do not have an inventory!", color=discord.Color.from_str(minecraft_color))

            await interaction.followup.send(embed=embed)

        await logCommand(interaction)

    #Networth command
    @app_commands.command(name="networth", description="View your item worth!")
    async def networth(self, interaction: discord.Interaction):
        await checkPlayer(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)
        async with aiosqlite.connect('quacky.db') as db:
            inventory = await listInventory(interaction.user.id)
            if inventory != {}:
                description = ""
                networth = 0
                for item in inventory.items():
                    val_cursor = await db.execute('SELECT SellValue FROM items WHERE ItemName=?', (item[0],))
                    buy_cursor = await db.execute('SELECT CostValue FROM items WHERE ItemName=?', (item[0],))
                    buy = await buy_cursor.fetchone()
                    val = await val_cursor.fetchone()
                    add = val[0]
                    add2 = buy[0]
                    networth+=add
                    networth+=add2
                    description = str(networth)
                
                bal_cursor = await db.execute('SELECT Coins FROM wallets WHERE UserID=?', (interaction.user.id,))
                bal_pt = await bal_cursor.fetchone()
                bal = bal_pt[0]
                totalVal = networth+bal
                
                embed = discord.Embed(title=f"{logo_emoji} Networth", description=f"Your items are worth **${description}**\n\nYour total value is **${f"{totalVal:,}"}**", color=discord.Color.from_str(minecraft_color))
            else:
                embed = discord.Embed(title=f"{logo_emoji} Nil Inventory", description=f"You do not have an inventory!", color=discord.Color.from_str(minecraft_color))

            await interaction.followup.send(embed=embed)

        await logCommand(interaction)

    #Mine command
    @app_commands.command(name="mine", description="Mine for resources!")
    @app_commands.describe(dim="The dimension name")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def mine(self, interaction: discord.Interaction, dim: str):
       await checkPlayer(interaction.user.id)
       async with aiosqlite.connect('quacky.db') as db:
           userHarv = 0
           toGet = 1

           pickaxe_values = {
               "Wooden Pickaxe": 1,
               "Stone Pickaxe": 1,
               "Iron Pickaxe": 2,
               "Diamond Pickaxe": 3,
               "Netherite Pickaxe": 4
           }

           fortune_values = {
               "Fortune 1": 2,
               "Fortune 2": 3,
               "Fortune 3": 4
           }

           for pickaxe, value in pickaxe_values.items():
                has_pickaxe = await hasItem(interaction.user.id, pickaxe)
                if has_pickaxe[0]:
                    userHarv = value
            
           for fortune, value in fortune_values.items():
                has_fortune = await hasItem(interaction.user.id, fortune)
                if has_fortune[0]:
                    toGet = random.randint(1, value)

           block_cursor = await db.execute(f'SELECT Blocks FROM dimensions WHERE DimName=?', (dim,))
           block = await block_cursor.fetchone()
           #print(block)
           #print(random.choice(block))
           if block:
                block = random.choice(block)
                block_dict = await convert_json_to_dict(block)
                block = random.choice(list(block_dict))
                #print(block)
                harv_cursor = await db.execute(f'SELECT HarvestLevel FROM items WHERE ItemName=?', (block,))
                item_cursor = await db.execute(f'SELECT * FROM items WHERE ItemName=?', (block,))
                item_n = await item_cursor.fetchone()
                item_name = item_n[1]
                harvLvl = await harv_cursor.fetchone()
                emoji_cursor = await db.execute('SELECT Emoji FROM items WHERE ItemName=?', (block,))
                emoji = await emoji_cursor.fetchone()

                if userHarv >= harvLvl[0]:
                    #jake sucks a penis YES
                    # ur gf's penis give me those emojis 💦💦💦💦
                    embed = discord.Embed(title=f"{logo_emoji} Block Mined", description=f"\n\nYou mined {toGet} {emoji[0]} **{item_name}**", color=discord.Color.from_str(minecraft_color))
                    await addItem(interaction.user.id, item_name, toGet)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                elif userHarv == 0:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou tried to mine rocks with your hand and broke your fingers dumbass! Type **/shop** to buy a pickaxe!", color=discord.Color.from_str(minecraft_color))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou can't mine **{item_name}**! Type **/shop** to buy a better pickaxe!", color=discord.Color.from_str(minecraft_color))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
           else:
                embed = discord.Embed(title=f"{logo_emoji} Invalid Dimension", description=f"\n\nThat dimension does not exist!", color=discord.Color.from_str(minecraft_color))
                await interaction.response.send_message(embed=embed, ephemeral=True)

       await logCommand(interaction)

    @mine.autocomplete("dim")
    async def mine_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.dimensions != []:
            names = [dimension['DimName'] for dimension in self.bot.dimensions]
            if current != "":
                matches = [dimension for dimension in names if dimension.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]
        
    #Refine command
    @app_commands.command(name="refine", description="Refine your resources!")
    @app_commands.describe(item="The name of the item", amount="The amount to refine")
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    async def refine(self, interaction: discord.Interaction, item: str, amount: int):
       await checkPlayer(interaction.user.id)
       async with aiosqlite.connect('quacky.db') as db:
            if await hasItem(interaction.user.id, "Furnace"):
                inventory_cursor = await db.execute('SELECT * FROM inventories WHERE UserID=?', (interaction.user.id,))
                ecurs1 = await db.execute('SELECT * FROM items WHERE ItemName=?', ("Coal",))
                emoji1 = await ecurs1.fetchone()
                emoji1 = emoji1[8]
                ecurs2 = await db.execute('SELECT * FROM items WHERE ItemName=?', (item,))
                emojiRaw = await ecurs2.fetchone()
                emojiRaw = emojiRaw[8]
                inventory = await inventory_cursor.fetchone()
                inv = await convert_json_to_dict(inventory[2])

                if "Coal" in inv:
                    userCoal = inv["Coal"]
                else:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou have **NO** {emoji1} Coal!", color=discord.Color.from_str(minecraft_color))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return 

                if item in inv:
                    userItems = inv[item]
                else:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou have **NO** {emojiRaw} {item}!", color=discord.Color.from_str(minecraft_color))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return 

                refinable_items = ["Copper Ore", "Iron Ore", "Silver Ore", "Gold Ore", "Cobblestone"]

                if item in refinable_items:
                    if userItems:
                        wantSmelt = amount
                        if userItems >= wantSmelt:
                            reqCoal = (wantSmelt / 8)
                            if reqCoal < 1:
                                reqCoal = 1
                            if userCoal >= reqCoal:
                                await removeItem(interaction.user.id, "Coal", reqCoal)
                                await removeItem(interaction.user.id, item, wantSmelt)

                                if item.split()[0] == "Cobblestone":
                                    refinedItem = f"Stone"
                                else:
                                    refinedItem = f"{item.split()[0]} Ingot"

                                ecurs3 = await db.execute('SELECT * FROM items WHERE ItemName=?', (refinedItem,))
                                emojiRefine = await ecurs3.fetchone()
                                emojiRefine = emojiRefine[8]
                                
                                ts = datetime.now() + timedelta(seconds=10)
                                timestamp = int(ts.timestamp())

                                for x in range(1, 11):
                                    percentage = x * 10

                                    progress_bar = generate_progress_bar(percentage)

                                    embed = discord.Embed(title=f"{logo_emoji} Items Smelted", description=f"\n\nYou are smelting {wantSmelt} {emojiRaw} **{item}** into {wantSmelt} {emojiRefine} **{refinedItem}** in {10 - x} seconds!\n{progress_bar}", color=discord.Color.from_str(minecraft_color))
                                    
                                    if x == 1:
                                        await interaction.response.send_message(embed=embed, ephemeral=True)
                                    else:
                                        await interaction.edit_original_response(embed=embed)
                                    await asyncio.sleep(1)

                                await addItem(interaction.user.id, refinedItem, wantSmelt)
                                
                                embed = discord.Embed(title=f"{logo_emoji} Items Smelted", description=f"\n\nYou have turned {wantSmelt} {emojiRaw} **{item}** into {wantSmelt} {emojiRefine} **{refinedItem}**!", color=discord.Color.from_str(minecraft_color))
                                await interaction.edit_original_response(embed=embed)
                            else:
                                embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou do not have enough {emoji1} Coal!", color=discord.Color.from_str(minecraft_color))
                                await interaction.response.send_message(embed=embed, ephemeral=True)
                        else:
                            embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou do not have enough {emojiRaw} **{item}**!", color=discord.Color.from_str(minecraft_color))
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                    else:
                        embed = discord.Embed(title=f"{logo_emoji} Invalid Item", description=f"\n\n{emojiRaw} {item} is not in your inventory or does not exist!", color=discord.Color.from_str(minecraft_color))
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(title=f"{logo_emoji} Invalid Item", description=f"\n\n{emojiRaw} {item} can not be smelted!", color=discord.Color.from_str(minecraft_color))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"\n\nYou don't have a furnace! Type **/recipe** to craft one!", color=discord.Color.from_str(minecraft_color))
                await interaction.response.send_message(embed=embed, ephemeral=True)

       await logCommand(interaction)
    
    @refine.autocomplete("item")
    async def refine_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            refinable_items = [item for item in self.bot.items if item.get('CanSmelt', 0) == 1]
            names = [item['ItemName'] for item in refinable_items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

    #Sell command
    @app_commands.command(name="sell", description="Sell your items")
    @app_commands.describe(item="The name of the item", amount="The amount to sell")
    async def sell(self, interaction: discord.Interaction, item: str, amount: int):
         await checkPlayer(interaction.user.id)
         async with aiosqlite.connect('quacky.db') as db:
            inventory_cursor = await db.execute('SELECT * FROM inventories WHERE UserID=?', (interaction.user.id,))
            inventory = await inventory_cursor.fetchone()
            if not inventory:
                await db.execute('INSERT INTO inventories (UserId) VALUES (?)', (interaction.user.id,))
                await db.commit()
            
            sell_cursor = await db.execute('SELECT * FROM items WHERE CanSell=1 AND ItemName=?', (item,))
            itemVals = await sell_cursor.fetchone()

            if itemVals:
                inv = await convert_json_to_dict(inventory[2])

                if inv[item] >= amount:
                    sellValue = itemVals[2]
                    itemName = itemVals[1]
                    itemEmoji = itemVals[8]
                    earned = sellValue * amount

                    await db.execute('UPDATE wallets SET Coins=Coins+? WHERE UserId=?', (earned, interaction.user.id))
                    await db.commit()

                    embed = discord.Embed(title=f"{logo_emoji} Item(s) Sold", description=f"You sold **{amount}** {itemEmoji} {itemName} for **${f"{earned:,}**"}", color=discord.Color.from_str(minecraft_color))
                else:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"You do not have enough of **{item}** to sell that much!", color=discord.Color.red())
            else:
                embed = discord.Embed(title=f"{logo_emoji} Bad Item", description=f"The item, **{item}**, does not exist!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await logCommand(interaction)

    @sell.autocomplete("item")
    async def sell_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            sellable_items = [item for item in self.bot.items if item.get('CanSell', 0) == 1]
            names = [item['ItemName'] for item in sellable_items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

    #Balance command
    @app_commands.command(name="balance", description="View your balance")
    async def balance(self, interaction: discord.Interaction):
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('quacky.db') as db:
            cursor = await db.execute('SELECT * FROM wallets WHERE UserId=?', (interaction.user.id,))
            wallet = await cursor.fetchone()
            if wallet is None:
                await db.execute('INSERT INTO wallets (UserId, Coins) VALUES (?,?)', (interaction.user.id, 0))
                await db.commit()

            cursor = await db.execute('SELECT * FROM wallets WHERE UserId=?', (interaction.user.id,))
            wallet = await cursor.fetchone()
            balance = wallet[2]

            main = discord.Embed(title=f"{logo_emoji} Wallet", description=f"You have **${f"{balance:,}"}**", color=discord.Color.from_str(minecraft_color))

        await interaction.response.send_message(embed=main, ephemeral=True)
        await logCommand(interaction)

    #Shop command - completed by someone - 05/27/2024 - refined by andrew 05/28/2024
    @app_commands.command(name="shop", description="Buy new items and upgrades!")
    async def shop(self, interaction: discord.Interaction):
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('quacky.db') as db:
            shop_cursor = await db.execute('SELECT * FROM items WHERE CanBuy=1')
            shop_inventory = await shop_cursor.fetchall()

            description = ""
            for inventory in shop_inventory:
                if inventory[8] != "":
                    description += f"{inventory[8]} **{inventory[1]}**: ${f"{inventory[4]:,}"}\n"
                else:
                    description += f"**{inventory[1]}**: ${f"{inventory[4]:,}"}\n"

            embed = discord.Embed(title=f"{logo_emoji} Shop Items", description=description, color=discord.Color.from_str(minecraft_color))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await logCommand(interaction)

    #Buy command
    @app_commands.command(name="buy", description="Buy new items and upgrades!")
    @app_commands.describe(item="The name of the item", amount="The amount to buy")
    async def buy(self, interaction: discord.Interaction, item: str, amount: int):
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('quacky.db') as db:
            await db.execute('PRAGMA journal_mode=WAL;')

            cursor = await db.execute('SELECT * FROM items WHERE ItemName=? AND CanBuy=1', (item,))
            point = await cursor.fetchone()
            
            if point:
                cost = point[4] * amount
                emoji = point[8]

                wallet_cursor = await db.execute('SELECT * FROM wallets WHERE UserId=?', (interaction.user.id,))
                bal_point = await wallet_cursor.fetchone()

                if bal_point:
                    balance = bal_point[2]

                    if balance >= cost:
                        await addItem(interaction.user.id, item, amount)
                        await db.execute('UPDATE wallets SET Coins=Coins-? WHERE UserId=?', (cost, interaction.user.id))
                        await db.commit()

                        description = f"\n\nSuccessfully purchased **{amount}** {emoji} {item.capitalize()} for ${f"{cost:,}"}!" if emoji else f"\n\nSuccessfully purchased **{amount}** {item.capitalize()} for ${cost}!"
                        embed = discord.Embed(title=f"{logo_emoji} Purchased Item", description=description, color=discord.Color.from_str(minecraft_color))
                    else:
                        embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description="You do not have enough funds!", color=discord.Color.from_str(minecraft_color))
                else:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description="You do not have enough funds!", color=discord.Color.from_str(minecraft_color))
            else:
                embed = discord.Embed(title=f"{logo_emoji} Bad Item", description=f"The item, **{item}**, does not exist!", color=discord.Color.red())

            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await logCommand(interaction)

    @buy.autocomplete("item")
    async def buy_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items != []:
            buyable_items = [item for item in self.bot.items if item.get('CanBuy', 0) == 1]
            names = [item['ItemName'] for item in buyable_items]
            if current != "":
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

    #Chop command
    @app_commands.command(name="chop", description="Chop trees for wood!")
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
    async def chop(self, interaction: discord.Interaction):
        await checkPlayer(interaction.user.id)
        
        treeLvl = 1

        axe_levels = {
                'Wooden Axe': 2,
                'Stone Axe': 3,
                'Iron Axe': 4,
                'Diamond Axe': 5,
                'Netherite Axe': 6
            }

        for axe, level in axe_levels.items():
            has_axe = await hasItem(interaction.user.id, axe)
            if has_axe[0]:
                treeLvl = level
                break

        toChop = random.randint(4, 18) * (treeLvl / 1.5)
        toChop = math.ceil(toChop)
        if toChop > 36:
            toChop = 36
        if treeLvl > 0:
            main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nPress the button below to start choppping! Chops Left: **{toChop}**', color=discord.Color.from_str(minecraft_color))
            await interaction.response.send_message(embed=main, view=chopTree(treeLvl, toChop), ephemeral=True) #change to pretty embed later
        else:
            main = discord.Embed(title=f"{logo_emoji} Lumberyard", description=f'\n\nYou need to buy an axe!', color=discord.Color.from_str(minecraft_color))
            await interaction.response.send_message(embed=main, ephemeral=True)

        await logCommand(interaction)
    
    #Help command
    @app_commands.command(name="help", description="Get started with Quacky-3000")
    async def help(self, interaction: discord.Interaction):
        await checkPlayer(interaction.user.id)
        main = discord.Embed(title=f"{logo_emoji} Quacky-3000", description=f'\n\n**:dollar: Making Money**\nType **/chop** to start harvesting wood and build your empire!\n\n**:european_castle: Guilds**\nType **/guild** to get started with making your own guild or joining someone else!\n\n**:shopping_cart: Buying Items**\nType **/shop** to view the items for sale and **/buy** to purchase them!', color=0xFFFFFF)
        await interaction.response.send_message(embed=main, ephemeral=True)

        await logCommand(interaction)

    #hUNT command
    @app_commands.command(name="hunt", description="Hunt for mobs!")
    @app_commands.describe(dim="The dimension name")
    @app_commands.checks.cooldown(1, 1.0, key=lambda i: (i.guild_id, i.user.id))
    async def hunt(self, interaction: discord.Interaction, dim: str):
        await checkPlayer(interaction.user.id) 
            
        embed = discord.Embed(title=f"{logo_emoji} Hunt", description="Loading...", color=discord.Color.from_str(minecraft_color))
        await interaction.response.send_message(embed=embed, ephemeral=True)

        async with aiosqlite.connect('quacky.db') as db:
            if await db.execute('SELECT * FROM dimensions WHERE DimName=?', (dim,)):
                mobs_cursor = await db.execute('SELECT * FROM dimensions WHERE DimName=?', (dim,))
                mob = await mobs_cursor.fetchone()
                mob = await convert_json_to_dict(mob[3])

                mobPicked = random.choice(list(mob.keys()))

                mobStats = mob[mobPicked]
                mobDrop = mobStats[0]
                mobHealth = mobStats[1]

                playerDmg = 0

                sword_values = {
                    "Wooden Sword": 4
                }

                sharpness_values = {
                    "Sharpness 1": 3
                }

                for sword, value in sword_values.items():
                    has_sword = await hasItem(interaction.user.id, sword)
                    if has_sword[0]:
                        playerDmg = value

                for sharpness, value in sharpness_values.items():
                    addDmg = value
                    for sword, value in sword_values.items():
                        has_sword = await hasItem(interaction.user.id, sword)
                        has_sharpness = await hasItem(interaction.user.id, sharpness)
                        if has_sharpness[0] and has_sword[0]:
                            playerDmg += addDmg
                
                if playerDmg == 0:
                    embed = discord.Embed(title=f"{logo_emoji} LOW NETWORTH INDIVIDUAL", description=f"You don't have a sword! Type **/shop** to buy one!", color=discord.Color.from_str(minecraft_color))
                    await interaction.edit_original_response(embed=embed)
                    return
                
                while mobHealth > 0:
                    N = 3
                    randStr = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(N))

                    def check(message):
                        return message.channel == interaction.channel and message.author == interaction.user
                    
                    health = generate_health(mobHealth)
                    embed = discord.Embed(title=f"{logo_emoji} Hunt", description=f"Type `{randStr}` and send it in this channel to attack **{mobPicked}**!\n\n{health}", color=discord.Color.green())
                    await interaction.edit_original_response(embed=embed)

                    try:
                        answer = await self.bot.wait_for('message', check=check, timeout=60.0)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(title=f"{logo_emoji} Hunt", description="You took too long! The mob escaped!", color=discord.Color.from_str(minecraft_color))
                        await interaction.edit_original_response(embed=embed)
                        return

                    if answer.content.upper() == randStr:
                        await answer.delete()
                        mobHealth -= playerDmg

                if mobHealth <= 0:
                    embed = discord.Embed(title=f"{logo_emoji} Hunt", description=f"You defeated **{mobPicked}** and got **{mobDrop}**!", color=discord.Color.from_str(minecraft_color))
                    await interaction.edit_original_response(embed=embed)
                    await addItem(interaction.user.id, mobDrop, 1)

        await logCommand(interaction)

    @hunt.autocomplete("dim")
    async def mine_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.dimensions != []:
            names = [dimension['DimName'] for dimension in self.bot.dimensions]
            if current != "":
                matches = [dimension for dimension in names if dimension.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]
    
    #Recipe command
    @app_commands.command(name="recipe", description="View the recipe of an item!")
    @app_commands.describe(item="The item you want to see the recipe for")
    async def recipe(self, interaction: discord.Interaction, item: str):
        await checkPlayer(interaction.user.id)

        empty = "<:empty:1250980038275235861> "


        if item in data["Recipes"]:
            blocks = data["Recipes"][item]

            description = f"**{item} Recipe**\n\n"
            counter = 0

            for block in blocks:
                for name, emoji in block.items():
                    if name == "":
                        description += empty
                    else:
                        description += f"{emoji} "
                        
                    counter += 1

                    if counter % 3 == 0:
                        description += "\n"
        else:
            description = f"**{item}** does not exist!"

        main = discord.Embed(title=f"{logo_emoji} Crafting Table", description=description, color=discord.Color.from_str(minecraft_color))
        await interaction.response.send_message(embed=main, ephemeral=True, view=Craft(item))

        await logCommand(interaction)
    
    @recipe.autocomplete("item")
    async def recipe_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if self.bot.items:
            recipes = data['Recipes']
            names = [item for item in recipes.keys()]
            if current:
                matches = [item for item in names if item.startswith(current)]
            else:
                matches = names
            return [app_commands.Choice(name=match, value=match) for match in matches][:25]
        return [app_commands.Choice(name="No Options Available")]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Mineshaft(bot))