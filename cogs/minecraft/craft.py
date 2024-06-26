import discord
import aiomysql
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

#Crafting Table View
class Craft(discord.ui.View):
    def __init__(self, item):
        super().__init__()
        self.item = item

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
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
                        await removeItem(self.bot, interaction.user.id, item, count) #let's test
                    
                    await addItem(self.bot, self.bot, interaction.user.id, self.item, 1)

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

class craft(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Craft command
    @app_commands.command(name="craft", description="Craft a new item!")
    @app_commands.describe(item="The item you want to craft")
    async def craft(self, interaction: discord.Interaction, item: str):
        await checkPlayer(self.bot, interaction.user.id)

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
    
    @craft.autocomplete("item")
    async def craft_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
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
    await bot.add_cog(craft(bot))