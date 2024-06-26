#imports
import discord
import aiosqlite
import yaml
import re

from discord.ext import commands
from discord import app_commands
from datetime import datetime
from utils import logCommand, checkPlayer

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

admin_guild_id = data["General"]["ADMIN_GUILD_ID"]
guild_color = data["Embeds"]["GUILD_COLOR"]
logo_emoji = data["Emojis"]["LOGO"]
shield_emoji = data["Emojis"]["SHIELD"]

#Accept Invite
class Accept(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiosqlite.connect('guilds.db') as db:
            msgid = interaction.message.id
            cursor = await db.execute('SELECT * FROM guild_invites WHERE MessageId=?', (msgid,))
            guild = await cursor.fetchone()
            guildID = guild[1]
            cursor2 = await db.execute('SELECT * FROM guilds WHERE GuildId=?', (guildID,))
            guild2 = await cursor2.fetchone()
            guildName = guild2[1]
            name = interaction.user.name
            memberid = interaction.user.id
            check = await db.execute('SELECT * from guild_members WHERE guildId=? AND memberId=?', (guildID, memberid))
            checked = await check.fetchone()

            if checked is None:
                await db.execute('INSERT INTO guild_members (GuildName, MemberID, GuildID) VALUES (?,?,?)', (guildName, memberid, guildID))
                await db.execute('UPDATE guilds SET GuildMembers=GuildMembers+? WHERE GuildId=?', (1, guildID))
                await db.commit()
                await interaction.response.send_message("Invite accepted!")
            else:
                await interaction.response.send_message("You are already in this guild!")

    @discord.ui.button(label='Decline', style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Invite declined!")

#Invite Member modal
class InviteMember(discord.ui.Modal, title='Invite a Member!'):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id
    
    name = discord.ui.TextInput(
        row = 1,
        label='Discord Username',
        placeholder='Type the username of the person you wish to invite',
        required = True,
    )
 
    #Search for user by name and send invite
    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect('guilds.db') as db:
            member = interaction.guild.get_member_named(self.name.value)
 
            if member:
                msg = await member.send('Click the button below to accept the invite!', view=Accept())
 
                await db.execute('INSERT INTO guild_invites (MessageId, GuildId) VALUES (?,?)', (msg.id, self.guild_id))
                await db.commit()
            else:
                await interaction.response.send_message("Failed to retrieve memnber object!", ephemeral=True)

#Kick Member modal
class KickMember(discord.ui.Modal, title='Remove a member from this guild'):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id
    
    name = discord.ui.TextInput(
        row = 1,
        label='Discord Username',
        placeholder='Type the username of the person you wish to remove',
        required = True,
    )
 
    #Search for user by name and kick
    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect('guilds.db') as db:
            member = interaction.guild.get_member_named(self.name.value)
            print (member.name)
            memberid = member.id
 
            if member:
                member_search = await db.execute('SELECT * FROM guild_members WHERE MemberId=? AND GuildId=?', (memberid, self.guild_id))
                owner_search = await db.execute('SELECT * FROM guilds WHERE OwnerId=? AND GuildId=?', (memberid, self.guild_id))
                memberCheck = await member_search.fetchone()
                ownerCheck = await owner_search.fetchone()
                if memberCheck:
                    if ownerCheck:
                        await interaction.response.send_message("You can't remove yourself from a guild you own.", ephemeral=True)
                    else:
                        await db.execute('DELETE FROM guild_members WHERE MemberId=? AND GuildId=?', (memberid, self.guild_id))
                        await db.execute('UPDATE guilds SET GuildMembers=GuildMembers-? WHERE GuildId=?', (1, self.guild_id))
                        await db.commit()
                else:
                    await interaction.response.send_message(f"<@{memberid}> is not in this guild.", ephemeral=True)
                    
            else:
                await interaction.response.send_message("Failed to retrieve memnber object!", ephemeral=True)

#Option list to edit selected guild from SettingsSearch.
class SettingsList(discord.ui.Select):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id

        options = [
            discord.SelectOption(label='Invite Member'),
            discord.SelectOption(label='Kick Member'),
            discord.SelectOption(label='Delete Guild'),
        ]

        super().__init__(placeholder='What do you wish to do?', min_values=1, max_values=1, options=options, custom_id='SettingsList:1')

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'Invite Member':
            await interaction.response.send_modal(InviteMember(self.guild_id))
        elif self.values[0] == 'Kick Member':
            await interaction.response.send_modal(KickMember(self.guild_id))
        elif self.values[0] == 'Delete Guild':
            async with aiosqlite.connect('guilds.db') as db:
                cursor = await db.execute('SELECT * FROM guilds WHERE OwnerId=? AND GuildId=?', (interaction.user.id, self.guild_id))
                if cursor:
                    await db.execute('DELETE FROM guilds WHERE OwnerId=? AND GuildId=?', (interaction.user.id, self.guild_id))
                    await db.execute('DELETE FROM guild_members WHERE MemberId=? AND GuildId=?', (interaction.user.id, self.guild_id))
                    await db.commit()

                    main = discord.Embed(title=f"{logo_emoji} Guilds", description=f"Guild successfully deleted.", color=discord.Color.from_str(guild_color))
                    await interaction.response.edit_message(content="", embed=main, view=None)
                else:
                    main = discord.Embed(title=f"{logo_emoji} Guilds", description=f"You are not the owner of this guild!", color=discord.Color.from_str(guild_color))
                    await interaction.response.edit_message(content="", embed=main, view=None)

#Add self to SettingsList
class SettingsListView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__()
        self.add_item(SettingsList(guild_id))

#Search user guilds, display option list to edit guild.
class SettingsSearch(discord.ui.Select):
    def __init__(self, guilds: list):
        self.guilds = guilds

        options = []
        for guild in guilds:
            options.append(discord.SelectOption(label=f"{guild[1]} (ID: {guild[0]})"))

        super().__init__(placeholder='Select a guild to edit...', min_values=1, max_values=1, options=options, custom_id='SettingsSearch:1')

    async def callback(self, interaction: discord.Interaction):
        async with aiosqlite.connect('guilds.db') as db:
            match = re.search(r'ID: (\d+)', self.values[0])
            guild_id = match.group(1)

            cursor = await db.execute('SELECT * FROM guilds WHERE GuildID=?', (guild_id,))
            guild = await cursor.fetchone()
            guild_name = guild[1]

            main = discord.Embed(title=f"{logo_emoji} {guild_name}", description=f"\n\n{shield_emoji} Guild Settings", color=discord.Color.from_str(guild_color))

            view = SettingsListView(guild_id)

            await interaction.response.edit_message(embed=main, view=view)

#Add self to SettingsSearch
class SettingsSearchView(discord.ui.View):
    def __init__(self, guilds: list):
        super().__init__()
        self.add_item(SettingsSearch(guilds))

#Search user guilds, display option list to view guild stats.
class GuildSearch(discord.ui.Select):
    def __init__(self, guilds: list):
        self.guilds = guilds

        options = []
        for guild in guilds:
            options.append(discord.SelectOption(label=f"{guild[1]} (ID: {guild[0]})"))

        super().__init__(placeholder='Select a guild to view...', min_values=1, max_values=1, options=options, custom_id='GuildSearch:1')

    async def callback(self, interaction: discord.Interaction):
        match = re.search(r'ID: (\d+)', self.values[0])
        guild_id = match.group(1)
        async with aiosqlite.connect('guilds.db') as db:
            cursor = await db.execute('SELECT * FROM guilds WHERE GuildID=?', (guild_id,))
            guild = await cursor.fetchone()
            guild_name = guild[1]
            guild_description = guild[2]
            guild_boosts = guild[4]

            cursor2 = await db.execute('SELECT * FROM guild_members WHERE GuildID=?', (guild_id,))
            guild2 = await cursor2.fetchall()
            guild_members = len(guild2)

            if guild_members >= 2:
                await db.execute('UPDATE guilds SET GuildLevel=2 WHERE GuildId=?', (guild_id,))
                await db.commit()
            elif guild_members >= 5:
                await db.execute('UPDATE guilds SET GuildLevel=3 WHERE GuildId=?', (guild_id,))
                await db.commit()
            else:
                ...

            guild_level = guild[3]

            main = discord.Embed(title=f"{logo_emoji} {guild_name}",
                            description=f"**{guild_description}**\n\n>>> 🧍 Members: **{guild_members}**\n\n🥇 Level: **{guild_level}**\n\n🚀 Boosts: **{guild_boosts}**",
                            color=discord.Color.from_str(guild_color))
            await interaction.response.edit_message(embed=main)

#Add self to GuildSearch
class GuildSearchView(discord.ui.View):
    def __init__(self, guilds: list):
        super().__init__()
        self.add_item(GuildSearch(guilds))

#Guild creation modal
class Create(discord.ui.Modal, title='Create a Guild!'):
    name = discord.ui.TextInput(
        row = 1,
        label='Guild Name',
        placeholder='Type your guild name here!',
        required = True,
    )

    description = discord.ui.TextInput(
        row = 2,
        label='Guild Description',
        placeholder='Describe your guild here!',
        required = True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect('guilds.db') as db:
            name = self.name.value
            description = self.description.value
            memberid = interaction.user.id
            
            #Add user values & base guild values to guilds.db and guild_members
            cursor = await db.execute('INSERT INTO guilds (GuildName, GuildDescription, GuildLevel, GuildBoosts, GuildMembers, OwnerId) VALUES (?,?,?,?,?,?)', (name, description, 1, 0, 1, memberid))
            await db.execute('INSERT INTO guild_members (GuildName, MemberID, GuildID) VALUES (?,?,?)', (name, memberid, cursor.lastrowid))
            await db.commit()
            
            await interaction.response.send_message('Guild Created!', ephemeral=True)

#Main Guild modal
class Guilds(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Profile', style=discord.ButtonStyle.blurple, emoji='<:profile1:1240486067292078100>')
    async def profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        main = discord.Embed(title=f"{logo_emoji} Profile", description=f"", color=discord.Color.from_str(guild_color))
        await interaction.response.send_message(embed=main, view=Profile(), ephemeral=True)

    #Guild settings button, displays SettingsSearch embed & modal.
    @discord.ui.button(label='Settings', style=discord.ButtonStyle.blurple, emoji='<:settings1:1240486074204033034>')
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        main = discord.Embed(title=f"{logo_emoji} Guilds", description=f"Select a Guild to edit.", color=discord.Color.from_str(guild_color))
        
        async with aiosqlite.connect('guilds.db') as db:
            cursor = await db.execute('SELECT * FROM guild_members WHERE MemberID=?', (str(interaction.user.id),))
            guilds = await cursor.fetchall()
            guilds = list(guilds)

            view = SettingsSearchView(guilds)
            await interaction.response.send_message(embed=main, view=view, ephemeral=True)

    #Guild stats button, displays GuildSearch embed & modal.
    @discord.ui.button(label='Guild Stats', style=discord.ButtonStyle.blurple, emoji=f'{shield_emoji}')
    async def stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        main = discord.Embed(title=f"{logo_emoji} Guilds", description=f"Select a Guild to view.", color=discord.Color.from_str(guild_color))
        
        async with aiosqlite.connect('guilds.db') as db:
            cursor = await db.execute('SELECT * FROM guild_members WHERE MemberID=?', (str(interaction.user.id),))
            guilds = await cursor.fetchall()
            guilds = list(guilds)
            view = GuildSearchView(guilds)
            
            await interaction.response.send_message(embed=main, view=view, ephemeral=True)

    #Create guild button, sends user to Create modal.
    @discord.ui.button(label='Create Guild', style=discord.ButtonStyle.blurple, emoji='<:smallquacky:1244850126124748851>')
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Create())

#Profile view
class Profile(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Primary Guild', style=discord.ButtonStyle.blurple, emoji=f'<:smallquacky:1244850126124748851>')
    async def primaryGuild(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(setPrimary())

#Primary guild modal
class setPrimary(discord.ui.Modal, title='Set your primary Guild!'):
    name = discord.ui.TextInput(
        row = 1,
        label='Guild Name',
        placeholder='Type the guild name here!',
        required = True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect('guilds.db') as db:
            name = self.name.value
            memberid = interaction.user.id
            
            cursor = await db.execute('SELECT * FROM guilds WHERE GuildName=?', (name,))
            if cursor:
                guild = await cursor.fetchone()
                guildName = guild[1]
                guildId = guild[0]
                await db.execute('UPDATE guild_members SET PrimaryID=? WHERE MemberId=?', (guildId, interaction.user.id))
                await db.commit()

                main = discord.Embed(title=f"{logo_emoji} Guilds", description=f"You have set **{guildName}** as your primary guild.", color=discord.Color.from_str(guild_color))
                await interaction.response.send_message(embed=main, ephemeral=True)
            else:
                await interaction.response.send_message(content="That is not a valid guild.", ephemeral=True)

class GuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #Main guild command
    @app_commands.command(name="guilds", description="Quacky Guilds")
    async def guild(self, interaction: discord.Interaction):
        async with aiosqlite.connect('guilds.db') as db:
            cursor = await db.execute('SELECT * FROM guilds')
            guilds = await cursor.fetchall()
            num_guilds = len(guilds)

            cursor2 = await db.execute('SELECT * FROM guild_members WHERE MemberID=?', (str(interaction.user.id),))
            uguilds = await cursor2.fetchall()
            user_guilds = len(uguilds)

            cursor3 = await db.execute('SELECT * FROM guild_members WHERE MemberID=?', (str(interaction.user.id),))
            pguild = await cursor3.fetchone()
            primaryGuild = pguild[4]

            cursor4 = await db.execute('SELECT * FROM guilds WHERE GuildID=?', (primaryGuild,))
            gpointer = await cursor4.fetchone()
            guildName = gpointer[1]

            main = discord.Embed(title=f"{logo_emoji} Guilds", description=f"""
There are **{num_guilds}** total guilds.

__{shield_emoji} Interact and manage your guilds!__
> You are in **{user_guilds}** guilds.
> Your primary guild is: **{guildName}**""",
    color=discord.Color.from_str(guild_color))

        await interaction.response.send_message(embed=main, view=Guilds(), ephemeral=True)

class ProfileCog(commands.GroupCog, name="profile"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="view", description="Views your profile")
    async def view(self, interaction: discord.Interaction) -> None:
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('guilds.db') as db:
            profile_cursor = await db.execute('SELECT * FROM profiles WHERE UserId=?', (interaction.user.id,))
            profile = await profile_cursor.fetchone()
            
            username = interaction.user.name
            displayName = profile[2]
            description = profile[3]
            status = profile[4]
            displayPicture = profile[5]
            thumbnail = profile[6]
            color = profile[7]
            
            embed = discord.Embed()

            if color:
                embed = discord.Embed(title=status, description=description, color=discord.Color.from_str(color))
            else:
                embed = discord.Embed(title=status, description=description, color=discord.Color.from_str(guild_color))
            
            if displayName and displayPicture:
                embed.set_author(name=displayName, icon_url=displayPicture)
            elif displayName:
                embed.set_author(name=displayName, icon_url=interaction.user.display_avatar.url)
            elif displayPicture:
                embed.set_author(name=username, icon_url=displayPicture)
            else:
                embed.set_author(name=username, icon_url=interaction.user.display_avatar.url)

            if thumbnail:
                embed.set_thumbnail(url=thumbnail)

            embed.set_footer(text=username, icon_url=interaction.user.display_avatar.url)
            embed.timestamp = datetime.now()

        await interaction.response.send_message(embed=embed)

        await logCommand(interaction)

    @app_commands.command(name="setname", description="Set your profile name!")
    @app_commands.describe(name="The name you want")
    async def setname(self, interaction: discord.Interaction, name: str) -> None:
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('guilds.db') as db:
            profile_cursor = await db.execute('SELECT * FROM profiles WHERE UserId=?', (interaction.user.id,))
            profile = await profile_cursor.fetchone()

            await db.execute('UPDATE profiles SET displayName=? WHERE UserId=?', (name, interaction.user.id))
            await db.commit()

            embed = discord.Embed(title="Profile Name Updated", description=f"\n\nSuccessfully changed your profile name to **{name}**", color=0xFFFFFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        await logCommand(interaction)

    @app_commands.command(name="setstatus", description="Set your profile status!")
    @app_commands.describe(status="The status you want to set")
    async def setstatus(self, interaction: discord.Interaction, status: str) -> None:
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('guilds.db') as db:
            profile_cursor = await db.execute('SELECT * FROM profiles WHERE UserId=?', (interaction.user.id,))
            profile = await profile_cursor.fetchone()

            await db.execute('UPDATE profiles SET status=? WHERE UserId=?', (status, interaction.user.id))
            await db.commit()

            embed = discord.Embed(title="Profile Status Updated", description=f"\n\nSuccessfully changed your status to **{status}**", color=0xFFFFFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        await logCommand(interaction)

    @app_commands.command(name="setdescription", description="Set your profile description!")
    @app_commands.describe(description="The description you want to set")
    async def setdescription(self, interaction: discord.Interaction, description: str) -> None:
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('guilds.db') as db:
            profile_cursor = await db.execute('SELECT * FROM profiles WHERE UserId=?', (interaction.user.id,))
            profile = await profile_cursor.fetchone()

            await db.execute('UPDATE profiles SET description=? WHERE UserId=?', (description, interaction.user.id))
            await db.commit()

            embed = discord.Embed(title="Profile Description Updated", description=f"\n\nSuccessfully changed your description to **{description}**", color=0xFFFFFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        await logCommand(interaction)

    @app_commands.command(name="setcolor", description="Set your profile color!")
    @app_commands.describe(color="The color you want to set [0x(HEXCODE)]")
    async def setcolor(self, interaction: discord.Interaction, color: str) -> None:
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('guilds.db') as db:
            profile_cursor = await db.execute('SELECT * FROM profiles WHERE UserId=?', (interaction.user.id,))
            profile = await profile_cursor.fetchone()

            await db.execute('UPDATE profiles SET embedColor=? WHERE UserId=?', (color, interaction.user.id))
            await db.commit()

            embed = discord.Embed(title="Profile Color Updated", description=f"\n\nSuccessfully changed your color to **{color}**", color=0xFFFFFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        await logCommand(interaction)

    @app_commands.command(name="setpicture", description="Set your profile picture!")
    @app_commands.describe(url="The link to the image you want to use")
    async def setpicture(self, interaction: discord.Interaction, url: str) -> None:
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('guilds.db') as db:
            profile_cursor = await db.execute('SELECT * FROM profiles WHERE UserId=?', (interaction.user.id,))
            profile = await profile_cursor.fetchone()

            await db.execute('UPDATE profiles SET displayPicture=? WHERE UserId=?', (url, interaction.user.id))
            await db.commit()

            embed = discord.Embed(title="Profile Picture Updated", description=f"\n\nSuccessfully changed your profile picture to\n {url}", color=0xFFFFFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        await logCommand(interaction)

    @app_commands.command(name="setthumbnail", description="Set your profile thumbnail!")
    @app_commands.describe(url="The link to the image you want to use")
    async def setthumbnail(self, interaction: discord.Interaction, url: str) -> None:
        await checkPlayer(interaction.user.id)
        async with aiosqlite.connect('guilds.db') as db:
            profile_cursor = await db.execute('SELECT * FROM profiles WHERE UserId=?', (interaction.user.id,))
            profile = await profile_cursor.fetchone()

            await db.execute('UPDATE profiles SET thumbnail=? WHERE UserId=?', (url, interaction.user.id))
            await db.commit()

            embed = discord.Embed(title="Profile Thumbnail Updated", description=f"\n\nSuccessfully changed your thumbnail picture to\n {url}", color=0xFFFFFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        await logCommand(interaction)

"""class MusicCog(commands.GroupCog, name="music"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.is_playing = False
        self.is_paused = False
        
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = FFMPEG_OPTIONS

        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False
        return {'source': info['formats'[0]['url']], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, interaction):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc == None:
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop[0]

            self.vc.play(discord.FFmpegAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

    @app_commands.command(name="play", description="Have Quacky play music!")
    async def play(self, ctx, interaction: discord.Interaction, *args) -> None:
        await checkPlayer(interaction.user.id)

        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Try a different keyword!")
            else:
                await ctx.send(f"**{song}** Added to the queue")
                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music(interaction)
            
        await logCommand(interaction)"""

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GuildCog(bot))
    await bot.add_cog(ProfileCog(bot))
    #await bot.add_cog(MusicCog(bot))