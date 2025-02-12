import subprocess
import sys
import threading
import asyncio
import time
import datetime
import cfg
config = cfg.config()
import pytz
import mysql.connector
import discord
from discord.ext import commands


dbconfig = {
    "host": "",
    "user": "",
    "password": "",
    "port": "",
    "database": "",
}


def getdatabase():
    try:
        mydb = mysql.connector.connect(**dbconfig)
        return mydb
    except mysql.connector.Error as err:
        current_time = datetime.datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%d/%m/%Y %I:%M %p")
        print("Reconnecting to Mysql --- " + current_time)
        time.sleep(10)
        return getdatabase()



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
    t2 = threading.Thread(target=database_on, args=(guild,)).start()
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
                    update_database(activity.name)
                    break


def update_database(gamename):
    gamename = str(gamename)
    gamename = gamename.replace("'", "")
    gamename = gamename.replace("\"", "")
    gamename = gamename.replace(":", "")

    if gamename == "Delta Force Game":
        gamename == "Delta Force"

    gamename = gamename.strip(" ")
    gamename = gamename.replace("Game", "")
    gamename = gamename.replace("game", "")
    gamename = gamename.replace("GAME", "")

    if gamename.startswith("PLAYERUNKNOWNS"):
        gamename == "PUBG BATTLEGROUNDS"
    db = getdatabase()
    cursor = db.cursor()
    try:
        cursor.execute(f"SELECT * FROM discord where gamename = '{gamename}';")
        myresult = cursor.fetchall()
        if len(myresult) > 0:
            cursor.execute(f"UPDATE discord SET gametime = gametime+1 where gamename = '{gamename}';")
            db.commit()
        else:
            cursor.execute(f"INSERT INTO discord (gamename , gametime) VALUES('{gamename}' , 1);")
            db.commit()
    except mysql.connector.Error as err:
        print(f"Updte_Error: {err}")
        time.sleep(5)
        update_database(gamename)
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
                time.sleep(1)
                await member.move_to(voice_channel)
                time.sleep(1)
                await member.move_to(sleep_channel)
                time.sleep(1)
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
            time.sleep(1)
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
        msg = msg.strip("zmsg ")
        await ctx.message.delete()
        await ctx.send(msg)
    else:
        await ctx.message.delete()
        await ctx.author.send("you don't have role")


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
                        # await ctx.send(f"**{member.display_name}** is currently playing: **{activity.name}**")
                        str += f"**{member.display_name}** is currently playing: **{activity.name}**\n"
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
    authors = config.AUTHOR

    if not channel:
        for author in authors:
            user = bot.get_user(author)
            await user.send("Channel for games stat not found. Loop stopped")
        return

    if isinstance(channel, discord.TextChannel):
        print(f"Deleting old messages from {channel.name}to display  game stat")
        try:
            async for message in channel.history(limit=None):
                await message.delete()
            print(f"All messages in #{channel.name} have been deleted.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        return

    old_time = "Time could not found"
    db = getdatabase()
    cursor = db.cursor()
    try:
        myresult = cursor.execute(f"SELECT * FROM timestring;")
        myresult = cursor.fetchall()
        old_time = myresult[0][0]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    db.close()
    embed = discord.Embed(
        title=f"**TOP 5 GAMES | FROM {old_time} TO NOW**",
        description="*Calculated if in vc | Result resets every 7 days*",
        color=discord.Color.from_rgb(0, 100, 255)  # Set the color of the embed
    )
    result = getgames()

    # Add fields to the embed
    for i in range(5):
        embed.add_field(name=f"No {i + 1}", value=f"```{result[i][0]}```", inline=True)
        embed.add_field(name="Time", value=f"```{result[i][1] // 60} hr {result[i][1] % 60} min```", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        if i >= len(result):
            break

    # Add footer, author, and thumbnail
    embed.set_footer(text="Stat bot by kenji.xx | Hosting : silly.dev")
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1021136605710389259/1317397679252181033/main_bogs_2_AdobeExpress.gif?ex=675e89b2&is=675d3832&hm=65805578a0661c2d9a8f1f70cda13bcd3a3777f0abb2dfe24467232f306702aa&")
    # Send the embed
    message = await channel.send(embed=embed)

    await asyncio.sleep(300)

    while True:

        result = getgames()
        if len(result) < 1:
            continue
        if message is None:
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
        newembed.set_footer(text="Stat bot by kenji.xx | Hosting : silly.dev")
        newembed.set_image(
            url="https://cdn.discordapp.com/attachments/1021136605710389259/1317397679252181033/main_bogs_2_AdobeExpress.gif?ex=675e89b2&is=675d3832&hm=65805578a0661c2d9a8f1f70cda13bcd3a3777f0abb2dfe24467232f306702aa&")
        await message.edit(embed=newembed)
        await asyncio.sleep(300)


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


def getgames():
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


@bot.event
async def on_message_delete(message):
    if not message.guild:
        return
    guild = message.guild
    log_channel = guild.get_channel(config.DELETE_LOG)

    if not log_channel:
        print(f"Log channel '{log_channel}'-channel not found in guild '{message.guild.name}'")
        return

    if message.author.bot:
        return

    embed = discord.Embed(title="Message Deleted", color=discord.Color.from_rgb(255, 0, 0))
    embed.add_field(name="Author", value=f"{message.author} ({message.author.id})", inline=False)
    embed.add_field(name="Channel", value=f"#{message.channel.name}", inline=False)
    embed.add_field(name="Content", value=message.content or "Embed/Attachment", inline=False)
    embed.set_footer(text=f"Message ID: {message.id} • Author ID: {message.author.id}")

    await log_channel.send(embed=embed)


@bot.command(name="resetstat")
async def resetstat(ctx):
    current_time = datetime.datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%d/%m/%Y %I:%M %p")
    result = getgames()
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
        await ctx.reply("Done")
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


bot.run(config.BOT_TOKEN)
