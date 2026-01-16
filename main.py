import os
import certifi
# Force Python to use certifi CA certificates
os.environ['SSL_CERT_FILE'] = certifi.where()

import subprocess
import sys
import threading
import asyncio
import time
import datetime
import cfg
import re
import io

config = cfg.config()

packages = ["discord", "pytz", "mysql","re", "io"]

for package in packages:
    try:
        # Try importing the package
        __import__(package)
    except ImportError:
        # If the package is not installed, install it
        print(f"{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} installed successfully!")
    finally:
        # Import the package after installation
        globals()[package] = __import__(package)

# data base
import pytz
import mysql.connector

dbconfig = {
    "host": "",
    "user": "avnadmin",
    "password": "",
    "port": "23326",
    "database": "gamestat",
}


def getdatabase():
    try:
        mydb = mysql.connector.connect(**dbconfig)
        return mydb
    except mysql.connector.Error as err:
        current_time = datetime.datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%d/%m/%Y %I:%M %p")
        print("Reconnecting to Mysql --- ", current_time, "Error : ", err)
        time.sleep(45)
        return getdatabase()


import discord
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="z", intents=intents)

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="yappin")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print("online")
    guild = bot.get_guild(config.GUILD)
    # role = guild.get_role(config.ROLE_USER)
    t1 = threading.Thread(target=database_on, args=(guild,)).start()
    print("activity thread started")
    await gameStat()
    print("game stat thread started")

def database_on(guild):
    while True:
        time.sleep(60)
        t1 = threading.Thread(target=check_game, args=(guild,)).start()

def check_game(guild):
    for vc in guild.voice_channels:
        members = vc.members
        for member in members:
            for activity in member.activities:
                if activity.type == discord.ActivityType.playing:
                    # print(f"{member.name} is currently playing: {activity.name}")
                    updateGameDb(activity.name)
                    break
            updateUserDb(member.id)

def updateUserDb(id):
    db = getdatabase()
    cursor = db.cursor()
    try:
        cursor.execute("""
                INSERT INTO user(id, time)
                VALUES (%s, 1) 
                ON DUPLICATE KEY UPDATE time = time + 1;          
                       """, (id,))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Updte_Error: {err}")
        time.sleep(20)
        updateUserDb(id)
    db.close()



def updateGameDb(gamename):
    gamename = str(gamename)

    if gamename.startswith("PLAYERUNKNOWNS"):
        gamename = "Pubg Battlegrounds"

    gamename = re.sub(r"[\'\":]", "", gamename).strip()
    gamename = gamename.strip(" ")

    gamename = re.sub(r'game', '', gamename, flags=re.IGNORECASE).strip()
    gamename = re.sub(r'tracker', '', gamename, flags=re.IGNORECASE).strip()
    gamename = re.sub(r'app', '', gamename, flags=re.IGNORECASE).strip()
    gamename = re.sub(r'client', '', gamename, flags=re.IGNORECASE).strip()

    gamename = gamename.lower().title()

    db = getdatabase()
    cursor = db.cursor()
    try:
        cursor.execute("""
                INSERT INTO discord (gamename, gametime)
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE gametime = gametime + 1;
            """, (gamename,))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Updte_Error: {err}")
        time.sleep(20)
        updateGameDb(gamename)
    db.close()

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("pong")

@bot.command(name="check")
async def hello(ctx):
    user = ctx.author
    guild = ctx.guild
    role = guild.get_role(config.ROLE_USER)
    if role in user.roles:
        await ctx.reply("you have role")
    else:
        await ctx.reply("you don't have role")

@bot.command(name="ring")
async def ring(ctx):
    user = ctx.author
    guild = ctx.guild
    role = guild.get_role(config.ROLE_USER)
    if role in user.roles:
        await ctx.send("got you dude")
        message = ctx.message.content
        message = message.strip("zring")
        victim = message.split("@")
        newVictim = []
        for i in victim:
            i = i.strip("<> ")
            if i != "":
                newVictim.append(int(i))

        for i in newVictim:
            member = ctx.guild.get_member(i)
            sleep_channel = ctx.guild.afk_channel
            if member.voice is not None:
                voice_channel = member.voice.channel
                await member.move_to(sleep_channel)
                time.sleep(0.5)
                await member.move_to(voice_channel)
                time.sleep(0.5)
                await member.move_to(sleep_channel)
                time.sleep(0.5)
                await member.move_to(voice_channel)
            else:
                await ctx.reply(f"<@{member.id}> is not in vc")


    else:
        await ctx.author.send("you don't have role")

@bot.command(name="moveall")
async def moveall(ctx):
    user = ctx.author
    guild = ctx.guild
    role = guild.get_role(config.ROLE_USER)

    if role in user.roles:

        message = ctx.message.content
        message = message.strip("zmoveall")
        message = message.strip("<#> ")
        if message == "":
            await ctx.reply("specify a channel nigger | type \"#![channel_name] \" ")
            return
        if ctx.author.voice is None:
            await ctx.reply("you must be connected in a voice channel")
            return
        new_channel = ctx.guild.get_channel(int(message))
        current_channel = ctx.author.voice.channel
        victim = current_channel.members
        for member in victim:
            await member.move_to(new_channel)
        await ctx.send("moving all")
    else:
        await ctx.reply("you don't have role")


@bot.command(name="cmd")
async def cmd(ctx):
    str = "Help text gugu gaga brains \n\nuse ``zring``<space><mention a user | use ``@``> to ring him \n\nuse ``zmoveall``<space><mention a voice channel | ``use #!``> to move all user to another channel\n\nend for now suggest more feature"
    await ctx.reply(str)

@bot.command(name="msg")
async def cmd(ctx):
    user = ctx.author
    guild = ctx.guild
    role = guild.get_role(config.ROLE_ADMIN)

    if role in user.roles:
        msg = ctx.message.content
        msg = msg.removeprefix("zmsg ").strip()
        files = []
        for attachment in ctx.message.attachments:
            try:
                fp = await attachment.to_file()
                files.append(fp)
            except Exception as e:
                print(f"Failed to get attachment: {e}")
        await ctx.message.delete()
        if files:
            await ctx.send(content=msg if msg else None, files=files)
        else:
            await ctx.send(msg)
    else:
        await ctx.message.delete()
        await ctx.author.send("You don't have the required role to use this command.")

@bot.command(name="act")
async def act(ctx):
    user = ctx.author
    guild = ctx.guild
    role = guild.get_role(config.ROLE_USER)
    if role in user.roles:
        check = True
        str = ""
        for vc in guild.voice_channels:
            members = vc.members
            for member in members:
                for activity in member.activities:
                    if activity.type == discord.ActivityType.playing:
                        check = False
                        name = activity.name
                        if name.startswith("Valorant"):
                            name = "VALORANT"
                        str += f"**{member.display_name}** is currently playing: **{name}**\n"
                        break
                    elif activity.type == discord.ActivityType.streaming:
                        check = False
                        str += f"**{member.display_name}** is currently streaming: **{activity.name}**\n"
                        break

        if check:
            await ctx.send("Everyone is sleepin'")
        else:
            await ctx.send(str)
    else:
        await ctx.message.delete()
        await ctx.author.send("you don't have role")

async def gameStat():
    guild = bot.get_guild(config.GUILD)
    channel = guild.get_channel(config.CHANNEL_INFO)
    channel2 = guild.get_channel(config.CHANNEL_LIFELESS)
    authors = config.AUTHOR

    if not channel:
        for author in authors:
            user = bot.get_user(author)
            await user.send("Channel for games stat not found. Loop stopped")
        return

    if not channel2:
        for author in authors:
            user = bot.get_user(author)
            await user.send("Channel for Lifeless counter not found. Loop stopped")
        return

    if isinstance(channel, discord.TextChannel):
        print(f"Deleting old messages from {channel.name}to display  game stat")
        try:
            async for message in channel.history(limit=None):
                await message.delete()
            print(f"All messages in #{channel.name} have been deleted.")
        except Exception as e:
            print(f"An error occurred: {e}")

    if isinstance(channel2, discord.TextChannel):
        print(f"Deleting old messages from {channel2.name}to display  game stat")
        try:
            async for message in channel2.history(limit=None):
                await message.delete()
            print(f"All messages in #{channel2.name} have been deleted.")
        except Exception as e:
            print(f"An error occurred: {e}")

    iniEmbed = discord.Embed(
        title="stat is starting",
        color=discord.Color.from_rgb(0, 100, 255)  # Set the color of the embed
    )

    message = await channel.send(embed=iniEmbed)
    message2 = await channel2.send(embed=iniEmbed)

    while True:
        result = getGames()
        result2 = getUser()
        if len(result) < 1:
            continue
        if message is None:
            break
        if len(result2) < 1:
            continue
        if message2 is None:
            break
        db = getdatabase()
        cursor = db.cursor()
        try:
            myresult = cursor.execute(f"SELECT * FROM timestring;")
            myresult = cursor.fetchall()
            old_time = myresult[0][0]
        except mysql.connector.Error as err:
            print(f"Loop_Error: {err}")
            continue
        db.close()
        current_time = datetime.datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%m/%d/%Y %I:%M %p")

        # ------------------------------------------------------------
        newembed = discord.Embed(
            title=f"**TOP 5 GAMES | FROM {old_time} TO NOW**",
            description=f"*Calculated if in vc | Result resets every 7 days | Last update : {current_time}*",
            color=discord.Color.from_rgb(0, 100, 255)  # Set the color of the embed
        )

        # Add fields to the embed
        for i in range(5):
            newembed.add_field(name=f"No {i + 1}", value=f"```{result[i][0]}```", inline=True)
            newembed.add_field(name="Time", value=f"```{result[i][1] // 60} hr {result[i][1] % 60} min```", inline=True)
            newembed.add_field(name="\u200b", value="\u200b", inline=True)
            if i >= len(result):
                break

        # Add footer, author, and thumbnail
        newembed.set_footer(text="Stat bot by kenji.xx")
        newembed.set_image(
            url="https://cdn.discordapp.com/attachments/1021136605710389259/1317397679252181033/main_bogs_2_AdobeExpress.gif?ex=675e89b2&is=675d3832&hm=65805578a0661c2d9a8f1f70cda13bcd3a3777f0abb2dfe24467232f306702aa&")
        await message.edit(embed=newembed)

        #--------------------------------------------------------------

        embed = discord.Embed(
            title=f"**TOP 5 LIFELESS USERS | FROM {old_time} TO NOW**",
            description=f"*Calculated from lifeless data | Last update: {current_time}*",
            color=discord.Color.from_rgb(255, 50, 50)
        )

        for i in range(min(5, len(result2))):
            user_id, time_minutes = result2[i]
            member = guild.get_member(int(user_id))

            if member:
                name = member.display_name
            else:
                name = f"Unknown ({user_id})"

            hr = time_minutes // 60
            mn = time_minutes % 60

            embed.add_field(name=f"No {i + 1}", value=f"```{name}```", inline=True)
            embed.add_field(name="Time", value=f"```{hr} hr {mn} min```", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.set_footer(text="Stat bot by kenji.xx")
        await message2.edit(embed=embed)

        # --------------------------------------------------------------

        await asyncio.sleep(300)

def getGames():
    myresult = []
    while True:
        db = getdatabase()
        cursor = db.cursor()
        try:
            cursor.execute(f"SELECT * FROM discord ;")
            myresult = cursor.fetchall()
            myresult = sorted(myresult, key=lambda l: l[1], reverse=True)
            break
        except mysql.connector.Error as err:
            print(f"Getgame_Error: {err}")
            continue

    db.close()
    return myresult

def getUser():
    myresult = []
    while True:
        db = getdatabase()
        cursor = db.cursor()
        try:
            cursor.execute(f"SELECT id, time FROM user ;")
            myresult = cursor.fetchall()
            myresult = sorted(myresult, key=lambda l: l[1], reverse=True)
            break
        except mysql.connector.Error as err:
            print(f"Getgame_Error: {err}")
            continue

    db.close()
    return myresult

@bot.command(name="zgamestat")
async def zgamestat(ctx):
    user = ctx.author
    guild = ctx.guild
    role = guild.get_role(config.ROLE_ADMIN)
    if role in user.roles:
        await ctx.author.reply("Working on it")
        await gameStat()
    else:
        await ctx.author.reply("You are not authorized to use this command")


@bot.command(name="resetstat")
async def resetstat(ctx):
    current_time = datetime.datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%d/%m/%Y %I:%M %p")
    result = getGames()
    result2 = getUser()
    guild = ctx.guild
    log_channel = ctx.guild.get_channel(config.RESET_INFO)
    if not log_channel:
        await ctx.send("Log channel not found in guild '{message.guild.name}'")
    old_time = "Time could not found"
    db = getdatabase()
    cursor = db.cursor()
    try:
        myresult = cursor.execute(f"SELECT * FROM timestring;")
        myresult = cursor.fetchall()
        old_time = myresult[0][0]
    except mysql.connector.Error as err:
        print(f"ResetStat_Error: {err}")
        await ctx.reply("Something went wrong please try again later")
        db.close()
        return
    db.close()

    user = ctx.author
    authors = config.AUTHOR


    cnt = 0
    cnt2 = 0
    if user.id in authors:
        embed = discord.Embed(title=f"Game Statistics from {old_time} to {current_time}:",
                              color=discord.Color.from_rgb(0, 64, 255))
        for i in range(len(result)):
            if cnt > 24:
                break

            if result[i][1] >= 30:
                embed.add_field(name=f"{result[i][0]} | Time: {result[i][1] // 60} hours {result[i][1] % 60} minutes ",
                                value="", inline=False)
                cnt += 1

        embed.set_footer(text=f"Requested by {user.name} time- {current_time}")

        await resetGameStat(current_time, ctx)
        await log_channel.send(embed=embed)

        # ---------------------------------------------------------

        embed = discord.Embed(title=f"User Statistics from {old_time} to {current_time}:",
                              color=discord.Color.from_rgb(0, 64, 255))

        for i in range(len(result2)):
            if cnt2 >= 25:
                break

            user_id = result2[i][0]
            time_minutes = result2[i][1]

            if time_minutes < 30:  # ignore very small values
                continue

            member = guild.get_member(int(user_id))
            name = member.display_name if member else f"Unknown ({user_id})"

            hr = time_minutes // 60
            mn = time_minutes % 60

            embed.add_field(
                name=f"{name} | Time: {hr} hours {mn} minutes",
                value="",
                inline=False
            )
            cnt2 += 1
        embed.set_footer(text=f"Requested by {ctx.author.name} • {current_time}")

        await resetUserStat(ctx)
        await log_channel.send(embed=embed)
        await ctx.reply("Done")

        print("Stat reset complete")
    else:
        await ctx.reply("you dont have permission")

async def resetGameStat(current_time, ctx):
    while True:
        db = getdatabase()
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE discord SET gametime = 0")
            db.commit()
            cursor.execute("DELETE FROM timestring")
            db.commit()
            cursor.execute(f"INSERT INTO timestring (oldtime) VALUES('{current_time}');")
            db.commit()

            break
        except mysql.connector.Error as err:
            print(f"ResetStat2_Error: {err}")
            ctx.reply("Something went wrong please try again later")
        db.close()

async def resetUserStat(ctx):
    while True:
        db = getdatabase()
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE user SET time = 0")
            db.commit()
            break
        except mysql.connector.Error as err:
            print(f"ResetStat2_Error: {err}")
            ctx.reply("Something went wrong please try again later")
        db.close()

@bot.event
async def on_message_delete(message):
    if not message.guild:
        return

    guild = message.guild
    log_channel = guild.get_channel(config.DELETE_LOG)

    if not log_channel:
        print(f"Log channel '{log_channel}' not found in guild '{message.guild.name}'")
        return

    if message.author.bot:
        return

    embed = discord.Embed(
        title="Message Deleted",
        color=discord.Color.from_rgb(255, 0, 0),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Author", value=f"{message.author} ({message.author.id})", inline=False)
    embed.add_field(name="Channel", value=f"#{message.channel.name}", inline=False)

    if message.content:
        embed.add_field(name="Content", value=message.content, inline=False)

    files = []
    if message.attachments:
        attachment_names = []
        for i, attachment in enumerate(message.attachments):
            try:
                # Read file into memory
                file_data = await attachment.read()
                file = discord.File(
                    io.BytesIO(file_data),
                    filename=attachment.filename
                )
                files.append(file)
                attachment_names.append(attachment.filename)

                # Use first image/gif as embed preview
                if i == 0 and attachment.content_type and attachment.content_type.startswith("image/"):
                    embed.set_image(url=f"attachment://{attachment.filename}")

            except Exception as e:
                print(f"Failed to download {attachment.filename}: {e}")

        embed.add_field(
            name="Attachments",
            value="\n".join(attachment_names),
            inline=False
        )

    embed.set_footer(text=f"Message ID: {message.id} • Author ID: {message.author.id}")
    await log_channel.send(embed=embed, files=files)

TARGET_ID = 634826720293290004  # protected user
beast = 0
noDisconnect = 1
timeoutChecker = {}

@bot.command(name="beast")
async def beast_mode(ctx):
    if ctx.author.id != TARGET_ID:
        await ctx.reply("fuck you")
        return

    global beast
    if beast == 0:
        beast = 1
        await ctx.reply("Beast mode is ON")
    else:
        beast = 0
        await ctx.reply("Beast mode is OFF")

@bot.command(name="nodc")
async def beast_mode(ctx):
    if ctx.author.id not in config.AUTHOR:
        await ctx.reply("fuck you")
        return

    global noDisconnect
    if noDisconnect == 0:
        noDisconnect = 1
        await ctx.reply("No Disconnect mode is ON")
    else:
        noDisconnect = 0
        await ctx.reply("No Disconnect mode is OFF")

@bot.event
async def on_voice_state_update(member, before, after):


    # ---------- LEAVE ----------
    if before.channel is not None and after.channel != before.channel:
        await log_vc_event(member, before.channel, "leave")
    # ---------- JOIN ----------
    if after.channel is not None and before.channel != after.channel:
        await log_vc_event(member, after.channel, "join")


    global noDisconnect
    if noDisconnect == 1:
        guild = member.guild
        async for entry in guild.audit_logs(limit=10 ,action=discord.AuditLogAction.member_disconnect):
            if (datetime.datetime.now(pytz.UTC) - entry.created_at).total_seconds() < 60 and getattr(entry.extra, "count", 0) > 4:
                culprit = entry.user
                textChannel = guild.get_channel(config.YAP_CHAT)
                global timeoutChecker
                if timeoutChecker.get(culprit.id, datetime.datetime.min.replace(tzinfo=pytz.UTC)) > datetime.datetime.now(pytz.UTC):
                    print(f"{culprit} is already timed-out")
                    continue
                try:
                    await culprit.timeout(datetime.timedelta(minutes=1), reason="timed-out for frequently disconnecting member(s)")
                    print(f"{culprit} has been timed-out for frequently disconnecting member(s) in 2 minutes.")
                    timeoutChecker[culprit.id] = datetime.datetime.now(pytz.UTC) + datetime.timedelta(minutes=1)
                except Exception as e:
                    print(f"Failed to get timed out for {culprit.mention}: {e}")

                await textChannel.send(f"{culprit.mention} has been (or tried to) timed-out for frequently disconnecting member(s) in 2 minutes."
                                       f"\n If it's not working properly then use `znodc` to turn it off")


    global beast
    if member.id == TARGET_ID and beast == 1:
        if after.channel:
            server_muted = after.mute and not after.self_mute
            server_deafened = after.deaf and not after.self_deaf

            if server_muted or server_deafened:
                try:
                    if server_muted:
                        await member.edit(mute=False)
                    if server_deafened:
                        await member.edit(deafen=False)
                except Exception as e:
                    print(f"Failed to unmute/undeafen {member}: {e}")


async def log_vc_event(member, channel, action):
    log_channel = member.guild.get_channel(config.JOIN_LOG)
    if not log_channel:
        return

    color = discord.Color.from_rgb(0,255,0) if action == "join" else discord.Color.from_rgb(255,0,0)
    title = f"🔊 {member} joined {channel.name}" if action == "join" else f"🔇 {member} left {channel.name}"

    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=discord.utils.utcnow()
    )

    #embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    #embed.add_field(name="Channel", value=f"{channel.name}" if channel else "Unknown", inline=False)

    await log_channel.send(embed=embed)


@bot.command(name="dm")
async def dm_mode(ctx, member: discord.Member, *, dm_message: str):

    if ctx.author.id not in config.AUTHOR:
        await ctx.send("❌ You are not authorized to use this command.")
        return
    try:
        await member.send(dm_message)
        log_channel = ctx.guild.get_channel(config.DELETE_LOG)
        if log_channel:
            embed = discord.Embed(
                title="💬 DM Sent",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Sender", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            embed.add_field(name="Receiver", value=f"{member} ({member.id})", inline=False)
            embed.add_field(name="Message", value=dm_message, inline=False)
            embed.set_footer(text=f"Logged by bot")

            await log_channel.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ I cannot DM this user.")
    except Exception as e:
        await ctx.send("⚠️ An error occurred.")
        print(e)

import discord

@bot.event
async def on_member_update(before, after):

    before_roles = set(before.roles)
    after_roles = set(after.roles)

    added_roles = after_roles - before_roles
    removed_roles = before_roles - after_roles

    if not added_roles and not removed_roles:
        return  # No role change

    log_channel = bot.get_channel(config.DELETE_LOG)
    if log_channel is None:
        print("Log channel not found!")
        return

    executor = None
    try:
        async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id:
                executor = entry.user
                break
    except Exception as e:
        print("Failed to fetch audit logs:", e)

    embed = discord.Embed(
        title="Member Role Updated",
        description=f"Roles changed for **{after}** ({after.id})",
        color=discord.Color.green()
    )

    if added_roles:
        embed.add_field(name="✅ Roles Added", value=", ".join([r.name for r in added_roles]), inline=False)
    if removed_roles:
        embed.add_field(name="❌ Roles Removed", value=", ".join([r.name for r in removed_roles]), inline=False)

    if executor:
        embed.set_footer(text=f"Updated by: {executor} ({executor.id})")
    else:
        embed.set_footer(text="Updated by: Unknown")

    await log_channel.send(embed=embed)


bot.run(config.BOT_TOKEN)
