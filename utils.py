import discord
import aiosqlite
from datetime import datetime
import yaml
import json

admins = [1029146068996325447, 503641822141349888]

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = 1244846648392417372
logo_emoji = data["Emojis"]["LOGO"]
log_channel_id = data["Channels"]["LOG_CHANNEL_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])

async def convert_json_to_dict(json_str: str) -> dict:
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}

async def checkPlayer(user_id: int):
    async with aiosqlite.connect('quacky.db') as db:
        inventory_cursor = await db.execute('SELECT * FROM inventories WHERE UserId=?', (user_id,))
        player_inventory = await inventory_cursor.fetchone()
        if player_inventory is None:
            await db.execute('INSERT INTO inventories (UserId) VALUES (?)', (user_id,))
            await db.commit()
        
        wallet_cursor = await db.execute('SELECT * FROM wallets WHERE UserId=?', (user_id,))
        player_wallet = await wallet_cursor.fetchone()
        if player_wallet is None:
            await db.execute('INSERT INTO wallets (UserId) VALUES (?)', (user_id,))
            await db.commit()

        
    async with aiosqlite.connect('guilds.db') as db:
        profile_cursor = await db.execute('SELECT * FROM profiles WHERE UserId=?', (user_id,))
        player_profile = await profile_cursor.fetchone()
        if player_profile is None:
            await db.execute('INSERT INTO profiles (UserId) VALUES (?)', (user_id,))
            await db.commit()

async def addItem(user_id: int, item: str, quantity: int):
    async with aiosqlite.connect('quacky.db') as db:
        item_cursor = await db.execute('SELECT * FROM items WHERE ItemName=?', (item,))
        item_exists = await item_cursor.fetchone()
        if item_exists:
            inventory_cursor = await db.execute('SELECT Items FROM inventories WHERE UserId=?', (user_id,))
            inventory = await inventory_cursor.fetchone()

            if inventory:
                inventory_dict = await convert_json_to_dict(inventory[0])
            else:
                inventory_dict = {}
            
            if item in inventory_dict:
                inventory_dict[item] += quantity
            else:
                inventory_dict[item] = quantity

            inventory_json = json.dumps(inventory_dict)

            await db.execute("UPDATE inventories SET Items=? WHERE UserId=?", (inventory_json, user_id))
            await db.commit()
            
            return True
        else:
            return False

async def removeItem(user_id: int, item: str, quantity: int = None):
    async with aiosqlite.connect('quacky.db') as db:
        item_cursor = await db.execute('SELECT * FROM items WHERE ItemName=?', (item,))
        item_exists = await item_cursor.fetchone()
        if item_exists:
            async with db.execute("SELECT Items FROM inventories WHERE UserId=?", (user_id,)) as inventory_cursor:
                inventory = await inventory_cursor.fetchone()
                if inventory:
                    inventory_dict = await convert_json_to_dict(inventory[0])
                else:
                    inventory_dict = {}
                
                if item in inventory_dict:
                    if quantity is None:
                        del inventory_dict[item]
                    else:
                        inventory_dict[item] -= quantity
                        if inventory_dict[item] <= 0:
                            del inventory_dict[item]
                
                inventory_json = json.dumps(inventory_dict)

                await db.execute("UPDATE inventories SET Items=? WHERE UserId=?", (inventory_json, user_id))
                await db.commit()
                
                return True
        else:
                return False

async def hasItem(user_id: int, item: str):
    async with aiosqlite.connect('quacky.db') as db:
        item_cursor = await db.execute('SELECT * FROM items WHERE ItemName=?', (item,))
        item_exists = await item_cursor.fetchone()
        if item_exists:
            async with db.execute("SELECT Items FROM inventories WHERE UserId=?", (user_id,)) as inventory_cursor:
                inventory = await inventory_cursor.fetchone()
                if inventory:
                    inventory_dict = await convert_json_to_dict(inventory[0])
                else:
                    inventory_dict = {}
                
                if item in inventory_dict:
                    return True, inventory_dict[item]
                else:
                    return False, 0
        else:
            return False, 0

async def listInventory(user_id: int):
    async with aiosqlite.connect('quacky.db') as db:
        player_cursor = await db.execute('SELECT * FROM inventories WHERE UserId=?', (user_id,))
        player_inventory = await player_cursor.fetchone()
        
        inventory_dict = await convert_json_to_dict(player_inventory[2])

        return inventory_dict

async def logCommand(interaction: discord.Interaction, response: str = None):
    admin_guild = interaction.client.get_guild(admin_guild_id)
    log_channel = interaction.client.get_channel(log_channel_id)

    timestamp = int(datetime.now().timestamp())

    namespace_str = ' '.join([f"{key}:{value}" for key, value in vars(interaction.namespace).items()])

    if response:
        description = f"<t:{timestamp}:R> {interaction.user.mention} (`{interaction.user.id}` | `{interaction.user.name}`) used the command **{interaction.command.name} {namespace_str}** and the bot responded with `{response}`!"
    else:
        description = f"<t:{timestamp}:R> {interaction.user.mention} (`{interaction.user.id}` | `{interaction.user.name}`) used the command **{interaction.command.name} {namespace_str}**!"
    
    embed = discord.Embed(title=f"{logo_emoji} Command Logged", description=description, color=admin_color)
    embed.timestamp = datetime.now()
    embed.set_footer(text="Quacky-3000 Logs")
    embed.set_thumbnail(url=admin_guild.icon.url)

    embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
    
    await log_channel.send(embed=embed)

async def hasAdmin(interaction: discord.Interaction):
    if interaction.user.id in admins:
        return True
    else:
        return False