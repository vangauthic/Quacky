import discord
import asyncio
import emoji
import yaml
import re
import aiomysql

from discord.ext import commands, tasks

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
admin_role_id = data["Roles"]["ADMIN_ROLE_ID"]
admin_color = discord.Color.from_str(data["Embeds"]["ADMIN_COLOR"])
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

class cache(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def cog_load(self):
        self.itemsCache.start()
        self.dimensionsCache.start()

    @tasks.loop(seconds=30)
    async def itemsCache(self):
        await asyncio.sleep(3)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                sql = 'SELECT * FROM items'
                await cursor.execute(sql)
                items = await cursor.fetchall()
                
                column_names = [column[0] for column in cursor.description]
                
                items_list = []
                for row in items:
                    item_dict = {column: row[column] for column in column_names}
                    items_list.append(item_dict)
                
                self.bot.items = items_list

    @itemsCache.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=30)
    async def dimensionsCache(self):
        await asyncio.sleep(3)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                dim_cursor = 'SELECT * FROM dimensions'
                await cursor.execute(dim_cursor)
                dimensions = await cursor.fetchall()
                
                dimensions_list = [{'DimId': dimension['DimId'], 'DimName': dimension['DimName']} for dimension in dimensions]
                
                self.bot.dimensions = dimensions_list

    @dimensionsCache.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(cache(bot), guilds=[discord.Object(id=admin_guild_id)])