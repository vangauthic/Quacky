import discord
import yaml
import json
import aiomysql
from discord.ext import commands
from datetime import datetime

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

async def checkPlayer(bot: commands.Bot, user_id: int):
    async with bot.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            sql = 'SELECT * FROM inventories WHERE UserId=%s'
            await cursor.execute(sql, (user_id,))
            player_inventory = await cursor.fetchone()

            if player_inventory is None:
                sql = 'INSERT INTO inventories (UserId) VALUES (%s)'
                await cursor.execute(sql, (user_id,))
            
            sql = 'SELECT * FROM wallets WHERE UserId=%s'
            await cursor.execute(sql, (user_id,))
            player_wallet = await cursor.fetchone()
            
            if player_wallet is None:
                sql = 'INSERT INTO wallets (UserId) VALUES (%s)'
                await cursor.execute(sql, (user_id,))

            sql = 'SELECT * FROM profiles WHERE UserId=%s'
            await cursor.execute(sql, (user_id,))
            player_profile = await cursor.fetchone()
            if player_profile is None:
                sql = 'INSERT INTO profiles (UserId) VALUES (%s)'
                await cursor.execute(sql, (user_id,))

            await conn.commit()

async def addItem(bot: commands.Bot, user_id: int, item: str, quantity: int):
    async with bot.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            item_cursor = 'SELECT * FROM items WHERE ItemName=%s'
            await cursor.execute(item_cursor, (item,))
            if await cursor.fetchone():
                sql = 'SELECT Items FROM inventories WHERE UserId=%s'
                await cursor.execute(sql, (user_id,))
                inventory = await cursor.fetchone()

                if inventory:
                    inventory_dict = await convert_json_to_dict(inventory['Items'])
                else:
                    inventory_dict = {}
                
                if item in inventory_dict:
                    inventory_dict[item] += quantity
                else:
                    inventory_dict[item] = quantity

                inventory_json = json.dumps(inventory_dict)

                sql = 'UPDATE inventories SET Items=%s WHERE UserId=%s'
                await cursor.execute(sql, (inventory_json, user_id))
                await conn.commit()
                
                return True
            else:
                return False

async def removeItem(bot: commands.Bot, user_id: int, item: str, quantity: int = None):
    async with bot.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            item_cursor = 'SELECT * FROM items WHERE ItemName=%s'
            await cursor.execute(item_cursor, (item,))
            if await cursor.fetchone():
                inventory_cursor = 'SELECT Items FROM inventories WHERE UserId=%s'
                await cursor.execute(inventory_cursor, (user_id,))
                inventory = await cursor.fetchone()
                if inventory:
                    inventory_dict = await convert_json_to_dict(inventory['Items'])
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

                sql = 'UPDATE inventories SET Items=%s WHERE UserId=%s'
                await cursor.execute(sql, (inventory_json, user_id))
                await conn.commit()
                
                return True
            else:
                return False

async def hasItem(bot: commands.Bot, user_id: int, item: str):
    async with bot.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            item_cursor = 'SELECT * FROM items WHERE ItemName=%s'
            await cursor.execute(item_cursor, (item,))
            item_exists = await cursor.fetchone()
            if item_exists:
                inventory_cursor = 'SELECT Items FROM inventories WHERE UserId=%s'
                await cursor.execute(inventory_cursor, (user_id,))
                inventory = await cursor.fetchone()
                if inventory:
                    inventory_dict = await convert_json_to_dict(inventory['Items'])
                else:
                    inventory_dict = {}
                
                if item in inventory_dict:
                    return True, inventory_dict[item]
                else:
                    return False, 0
            else:
                return False, 0

async def listInventory(bot: commands.Bot, user_id: int):
    async with bot.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = "SELECT * FROM inventories WHERE UserId = %s"
            await cursor.execute(sql, (user_id,))
            player_inventory = await cursor.fetchone()
            
            print(player_inventory)
            
            inventory_dict = await convert_json_to_dict(player_inventory['Items'])

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