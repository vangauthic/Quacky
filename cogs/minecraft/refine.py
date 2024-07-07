import discord
import aiomysql
import asyncio
import yaml
import math

from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils import addItem, removeItem, convert_json_to_dict, checkPlayer, hasItem, logCommand, checkServer

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

class refine(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Refine command
    @app_commands.command(name="refine", description="Refine your resources!")
    @app_commands.describe(item="The name of the item", amount="The amount to refine")
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    async def refine(self, interaction: discord.Interaction, item: str, amount: int):
       if await checkServer(self.bot, interaction.guild.id):
            await checkPlayer(self.bot, interaction.user.id)
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                        furnaceCheck = await hasItem(self.bot, interaction.user.id, "Furnace")
                        if furnaceCheck[0]:
                            inventory_cursor = 'SELECT * FROM inventories WHERE UserID=%s'
                            await cursor.execute(inventory_cursor, (interaction.user.id,))
                            inventory = await cursor.fetchone()

                            ecurs1 = 'SELECT * FROM items WHERE ItemName=%s'
                            await cursor.execute(ecurs1, ('Coal',))
                            emoji1 = await cursor.fetchone()
                            emoji1 = emoji1['Emoji']

                            ecurs2 = 'SELECT * FROM items WHERE ItemName=%s'
                            await cursor.execute(ecurs2, (item,))
                            emojiRaw = await cursor.fetchone()
                            emojiRaw = emojiRaw['Emoji']

                            inv = await convert_json_to_dict(inventory['Items'])

                            if "Coal" in inv:
                                userCoal = inv["Coal"]
                            else:
                                embed = discord.Embed(title=f"LOW NETWORTH INDIVIDUAL", description=f"\n\nYou have **NO** {emoji1} Coal!", color=discord.Color.from_str(minecraft_color))
                                embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                                await interaction.response.send_message(embed=embed, ephemeral=True)
                                return 

                            if item in inv:
                                userItems = inv[item]
                            else:
                                embed = discord.Embed(title=f"LOW NETWORTH INDIVIDUAL", description=f"\n\nYou have **NO** {emojiRaw} {item}!", color=discord.Color.from_str(minecraft_color))
                                embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                                await interaction.response.send_message(embed=embed, ephemeral=True)
                                return 

                            item_select = 'SELECT * FROM items WHERE CanSmelt=True'
                            await cursor.execute(item_select)
                            items = await cursor.fetchall()
                            refinable_items = str(items)

                            if item in refinable_items:
                                if userItems:
                                    wantSmelt = amount
                                    if userItems >= wantSmelt:
                                        reqCoal = math.ceil(wantSmelt / 8)
                                        if reqCoal < 1:
                                            reqCoal = 1
                                        if userCoal >= reqCoal:
                                            await removeItem(self.bot, interaction.user.id, "Coal", reqCoal)
                                            await removeItem(self.bot, interaction.user.id, item, wantSmelt)

                                            ref_select = 'SELECT * FROM items WHERE ItemName=%s'
                                            await cursor.execute(ref_select, (item,))
                                            ref_item = await cursor.fetchone()
                                            refinedItem = ref_item['SmeltedItem']

                                            ecurs3 = 'SELECT * FROM items WHERE ItemName=%s'
                                            await cursor.execute(ecurs3, (refinedItem,))
                                            emojiRefine = await cursor.fetchone()
                                            emojiRefine = emojiRefine['Emoji']
                                            
                                            ts = datetime.now() + timedelta(seconds=10)
                                            timestamp = int(ts.timestamp())

                                            for x in range(1, 11):
                                                percentage = x * 10

                                                progress_bar = generate_progress_bar(percentage)

                                                embed = discord.Embed(title=f"Items Smelted", description=f"\n\nYou are smelting {wantSmelt} {emojiRaw} **{item}** into {wantSmelt} {emojiRefine} **{refinedItem}** in {10 - x} seconds!\n{progress_bar}", color=discord.Color.from_str(minecraft_color))
                                                embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                                                
                                                if x == 1:
                                                    await interaction.response.send_message(embed=embed, ephemeral=True)
                                                else:
                                                    await interaction.edit_original_response(embed=embed)
                                                await asyncio.sleep(1)

                                            await addItem(self.bot, interaction.user.id, refinedItem, wantSmelt)
                                            
                                            embed = discord.Embed(title=f"Items Smelted", description=f"\n\nYou have turned {wantSmelt} {emojiRaw} **{item}** into {wantSmelt} {emojiRefine} **{refinedItem}**!", color=discord.Color.from_str(minecraft_color))
                                            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                                            await interaction.edit_original_response(embed=embed)
                                        else:
                                            embed = discord.Embed(title=f"LOW NETWORTH INDIVIDUAL", description=f"\n\nYou do not have enough {emoji1} Coal!", color=discord.Color.from_str(minecraft_color))
                                            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                                            await interaction.response.send_message(embed=embed, ephemeral=True)
                                    else:
                                        embed = discord.Embed(title=f"LOW NETWORTH INDIVIDUAL", description=f"\n\nYou do not have enough {emojiRaw} **{item}**!", color=discord.Color.from_str(minecraft_color))
                                        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                                        await interaction.response.send_message(embed=embed, ephemeral=True)
                                else:
                                    embed = discord.Embed(title=f"Invalid Item", description=f"\n\n{emojiRaw} {item} is not in your inventory or does not exist!", color=discord.Color.from_str(minecraft_color))
                                    embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                                    await interaction.response.send_message(embed=embed, ephemeral=True)
                            else:
                                embed = discord.Embed(title=f"Invalid Item", description=f"\n\n{emojiRaw} {item} can not be smelted!", color=discord.Color.from_str(minecraft_color))
                                embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                                await interaction.response.send_message(embed=embed, ephemeral=True)
                        else:
                            embed = discord.Embed(title=f"LOW NETWORTH INDIVIDUAL", description=f"\n\nYou don't have a furnace! Type **/recipe** to craft one!", color=discord.Color.from_str(minecraft_color))
                            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                            await interaction.response.send_message(embed=embed, ephemeral=True)

            await logCommand(interaction)
       else:
            embed = discord.Embed(title=f"Game Disabled",
                                  description="This server currently has the Quacky-3000 Minigame disabled.",
                                  color=discord.Color.red())
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
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

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(refine(bot))