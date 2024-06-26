import discord
import aiomysql
import yaml
import sys
from discord.ext import commands
from discord import app_commands
from checks import check_tables

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

token = data["General"]["TOKEN"]
activity = data["General"]["ACTIVITY"].lower()
doing_activity = data["General"]["DOING_ACTIVITY"]
status = data["General"]["STATUS"].lower()
admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
host = data["MySQL"]["HOST"]
user = data["MySQL"]["USERNAME"]
password = data["MySQL"]["PASSWORD"]
database = data["MySQL"]["DATABASE"]
guild_color = data["Embeds"]["GUILD_COLOR"]
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

initial_extensions = [
                      'cogs.minecraft.balance',
                      'cogs.minecraft.buy',
                      'cogs.minecraft.chop',
                      'cogs.minecraft.craft',
                      'cogs.minecraft.help',
                      'cogs.minecraft.hunt',
                      'cogs.minecraft.inventory',
                      'cogs.minecraft.mine',
                      'cogs.minecraft.networth',
                      'cogs.minecraft.refine',
                      'cogs.minecraft.sell',
                      'cogs.minecraft.shop',

                      'cogs.utility.additem',
                      'cogs.utility.clear',
                      'cogs.utility.deleteitem',
                      'cogs.utility.dimensions',
                      'cogs.utility.givecoins',
                      'cogs.utility.giveitem',
                      'cogs.utility.grabid',
                      'cogs.utility.info',
                      'cogs.utility.pfp',
                      'cogs.utility.takecoins',
                      'cogs.utility.takeitem',

                      'cogs.cache'
                      ]
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if status == "online":
    _status = getattr(discord.Status, status)
elif status == "idle":
    _status = getattr(discord.Status, status)
elif status == "dnd":
    _status = getattr(discord.Status, status)
elif status == "invisible":
    _status = getattr(discord.Status, status)
else:
    sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Status: {bcolors.ENDC}{bcolors.OKCYAN}{status}{bcolors.ENDC}
{bcolors.OKBLUE}Valid Options: {bcolors.ENDC}{bcolors.OKGREEN}{bcolors.UNDERLINE}online{bcolors.ENDC}{bcolors.OKGREEN}, {bcolors.UNDERLINE}idle{bcolors.ENDC}{bcolors.OKGREEN}, {bcolors.UNDERLINE}dnd{bcolors.ENDC}{bcolors.OKGREEN}, or {bcolors.UNDERLINE}invisible{bcolors.ENDC}
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 7
""")

if activity == "playing":
    if doing_activity == "":
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Doing Activity: {bcolors.OKBLUE}It Must Be Set!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 5
""")
    else:
        _activity = discord.Game(name=doing_activity)
elif activity == "watching":
    if doing_activity == "":
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Doing Activity: {bcolors.OKBLUE}It Must Be Set!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 5
""")
    else:
        _activity = discord.Activity(name=doing_activity, type=discord.ActivityType.watching)
elif activity == "listening":
    if doing_activity == "":
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Doing Activity: {bcolors.OKBLUE}It Must Be Set!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 5
""")
    else:
        _activity = discord.Activity(name=doing_activity, type=discord.ActivityType.listening)
elif activity == "competing":
    if doing_activity == "":
        sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Doing Activity: {bcolors.OKBLUE}It Must Be Set!
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 5
""")
    else:
        _activity = discord.Activity(name=doing_activity, type=discord.ActivityType.competing)
else:
    sys.exit(f"""
{bcolors.FAIL}{bcolors.BOLD}ERROR:{bcolors.ENDC}
{bcolors.FAIL}Invalid Activity: {bcolors.ENDC}{bcolors.OKCYAN}{activity}{bcolors.ENDC}
{bcolors.OKBLUE}Valid Options: {bcolors.ENDC}{bcolors.OKGREEN}{bcolors.UNDERLINE}playing{bcolors.ENDC}{bcolors.OKGREEN}, {bcolors.UNDERLINE}watching{bcolors.ENDC}{bcolors.OKGREEN}, {bcolors.UNDERLINE}competing{bcolors.ENDC}{bcolors.OKGREEN}, or {bcolors.UNDERLINE}listening{bcolors.ENDC}
{bcolors.OKGREEN}config.json {bcolors.OKCYAN}Line 4
""")

intents = discord.Intents.all()
class sirQuacky(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix = '.',
            intents = intents,
            token = token,
            activity = _activity,
            status = _status
        )
        self.pool = None

    async def on_ready(self):
        print(f'{client.user} is connected!')

        print('Attempting to create database pools...')
        print('Creating 1/1 pools...')
        self.pool = await aiomysql.create_pool(
            host=host,
            user=user,
            password=password,
            db=database,
        )
        print('Created 1/1 pools!')

        print("Attempting to check local tables...")
        await check_tables(self)
        print("Checked!")

        print('Attempting to sync slash commands...')
        await self.tree.sync()
        await self.tree.sync(guild=discord.Object(id=admin_guild_id))
        print('Synced')

    async def setup_hook(self):
        for extension in initial_extensions:
            await self.load_extension(extension)

client = sirQuacky()
client.items = [] # Required so the items can be cached
client.dimensions = [] # Required so the dimensions can be cached

#Tell cooldown
@client.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        time  = round(error.retry_after, 2)
        await interaction.response.send_message(f"This is on cooldown for the next {time}s.", ephemeral=True)
        return
    raise error

client.run(token)