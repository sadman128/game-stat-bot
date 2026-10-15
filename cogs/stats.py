import asyncio
import datetime
import pytz
import logging
import discord
from discord.ext import commands, tasks

from config import config
from database import (
    update_user_db,
    update_game_db,
    get_games,
    get_users,
    get_timestring,
    reset_game_stat,
    reset_user_stat,
)

logger = logging.getLogger(__name__)

class Stats(commands.Cog):
    """Game and voice activity tracking, live leaderboards, and stat resets."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gamestat_task = None
        self.activity_tracker.start()

    def cog_unload(self):
        self.activity_tracker.cancel()
        if self.gamestat_task and not self.gamestat_task.done():
            self.gamestat_task.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        # Start leaderboard task when bot is ready
        if self.gamestat_task is None or self.gamestat_task.done():
            self.gamestat_task = asyncio.create_task(self.game_stat_loop())

    @tasks.loop(seconds=60)
    async def activity_tracker(self):
        """Scans voice channels every 60s and updates user & game playtimes."""
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(config.GUILD_ID)
        if not guild:
            return

        for vc in guild.voice_channels:
            for member in vc.members:
                for activity in member.activities:
                    if activity.type == discord.ActivityType.playing:
                        await asyncio.to_thread(update_game_db, activity.name)
                        break
                await asyncio.to_thread(update_user_db, member.id)

    async def game_stat_loop(self):
        """Maintains the top 5 games and top 5 lifeless users embeds."""
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(config.GUILD_ID)
        if not guild:
            logger.error(f"Guild {config.GUILD_ID} not found for gameStat.")
            return

        channel = guild.get_channel(config.CHANNEL_INFO)
        channel2 = guild.get_channel(config.CHANNEL_LIFELESS)

        if not channel or not channel2:
            for author_id in config.AUTHOR:
                user = self.bot.get_user(author_id)
                if user:
                    if not channel:
                        await user.send("Channel for games stat not found. Loop stopped")
                    if not channel2:
                        await user.send("Channel for Lifeless counter not found. Loop stopped")
            return

        # Clear old messages in both channels
        for ch in (channel, channel2):
            if isinstance(ch, discord.TextChannel):
                try:
                    async for message in ch.history(limit=None):
                        await message.delete()
                    logger.info(f"Cleared previous messages in #{ch.name}")
                except Exception as e:
                    logger.error(f"Error clearing #{ch.name}: {e}")

        init_embed = discord.Embed(
            title="stat is starting",
            color=discord.Color.from_rgb(0, 100, 255)
        )

        message = await channel.send(embed=init_embed)
        message2 = await channel2.send(embed=init_embed)

        tz = pytz.timezone(config.TIMEZONE)

        while True:
            try:
                result = await asyncio.to_thread(get_games)
                result2 = await asyncio.to_thread(get_users)

                if len(result) < 1 or message is None or len(result2) < 1 or message2 is None:
                    await asyncio.sleep(10)
                    continue

                old_time = await asyncio.to_thread(get_timestring)
                current_time = datetime.datetime.now(tz).strftime("%m/%d/%Y %I:%M %p")

                # --- TOP 5 GAMES EMBED ---
                game_embed = discord.Embed(
                    title=f"**TOP 5 GAMES | FROM {old_time} TO NOW**",
                    description=f"*Calculated if in vc | Result resets every 7 days | Last update : {current_time}*",
                    color=discord.Color.from_rgb(0, 100, 255)
                )

                for i in range(min(5, len(result))):
                    game_embed.add_field(name=f"No {i + 1}", value=f"```{result[i][0]}```", inline=True)
                    game_embed.add_field(name="Time", value=f"```{result[i][1] // 60} hr {result[i][1] % 60} min```", inline=True)
                    game_embed.add_field(name="\u200b", value="\u200b", inline=True)

                game_embed.set_footer(text="Stat bot by kenji.xx")
                game_embed.set_image(
                    url="https://cdn.discordapp.com/attachments/1021136605710389259/1317397679252181033/main_bogs_2_AdobeExpress.gif?ex=675e89b2&is=675d3832&hm=65805578a0661c2d9a8f1f70cda13bcd3a3777f0abb2dfe24467232f306702aa&"
                )
                await message.edit(embed=game_embed)

                # --- TOP 5 LIFELESS USERS EMBED ---
                user_embed = discord.Embed(
                    title=f"**TOP 5 LIFELESS USERS | FROM {old_time} TO NOW**",
                    description=f"*Calculated from lifeless data | Last update: {current_time}*",
                    color=discord.Color.from_rgb(255, 50, 50)
                )

                for i in range(min(5, len(result2))):
                    user_id, time_minutes = result2[i]
                    member = guild.get_member(int(user_id))
                    name = member.display_name if member else f"Unknown ({user_id})"

                    hr = time_minutes // 60
                    mn = time_minutes % 60

                    user_embed.add_field(name=f"No {i + 1}", value=f"```{name}```", inline=True)
                    user_embed.add_field(name="Time", value=f"```{hr} hr {mn} min```", inline=True)
                    user_embed.add_field(name="\u200b", value="\u200b", inline=True)

                user_embed.set_footer(text="Stat bot by kenji.xx")
                await message2.edit(embed=user_embed)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in gameStat loop: {e}")

            await asyncio.sleep(300)

    @commands.command(name="zgamestat")
    async def zgamestat(self, ctx: commands.Context):
        """Admin command to re-initialize gameStat leaderboard."""
        role = ctx.guild.get_role(config.ROLE_ADMIN)
        if role not in ctx.author.roles:
            await ctx.author.reply("You are not authorized to use this command")
            return

        await ctx.author.reply("Working on it")
        if self.gamestat_task and not self.gamestat_task.done():
            self.gamestat_task.cancel()
        self.gamestat_task = asyncio.create_task(self.game_stat_loop())

    @commands.command(name="resetstat")
    async def resetstat(self, ctx: commands.Context):
        """Reset stats and post summary to the log channel (Author only)."""
        if ctx.author.id not in config.AUTHOR:
            await ctx.reply("You are not authorized to use this command")
            return

        tz = pytz.timezone(config.TIMEZONE)
        current_time = datetime.datetime.now(tz).strftime("%d/%m/%Y %I:%M %p")

        result = await asyncio.to_thread(get_games)
        result2 = await asyncio.to_thread(get_users)
        old_time = await asyncio.to_thread(get_timestring)

        log_channel = ctx.guild.get_channel(config.RESET_INFO)
        if not log_channel:
            await ctx.send("Log channel not found in guild")

        # --- GAME STATS LOG EMBED ---
        game_embed = discord.Embed(
            title=f"Game Statistics from {old_time} to {current_time}:",
            color=discord.Color.from_rgb(0, 64, 255)
        )
        cnt = 0
        for game, playtime in result:
            if cnt >= 25:
                break
            if playtime >= 30:
                game_embed.add_field(
                    name=f"{game} | Time: {playtime // 60} hours {playtime % 60} minutes",
                    value="",
                    inline=False
                )
                cnt += 1

        game_embed.set_footer(text=f"Requested by {ctx.author.name} time- {current_time}")

        # Reset games in DB
        await asyncio.to_thread(reset_game_stat, current_time)
        if log_channel:
            await log_channel.send(embed=game_embed)

        # --- USER STATS LOG EMBED ---
        user_embed = discord.Embed(
            title=f"User Statistics from {old_time} to {current_time}:",
            color=discord.Color.from_rgb(0, 64, 255)
        )
        cnt2 = 0
        for uid, user_time in result2:
            if cnt2 >= 25:
                break
            if user_time < 30:
                continue

            member = ctx.guild.get_member(int(uid))
            name = member.display_name if member else f"Unknown ({uid})"
            hr = user_time // 60
            mn = user_time % 60

            user_embed.add_field(
                name=f"{name} | Time: {hr} hours {mn} minutes",
                value="",
                inline=False
            )
            cnt2 += 1

        user_embed.set_footer(text=f"Requested by {ctx.author.name} • {current_time}")

        # Reset users in DB
        await asyncio.to_thread(reset_user_stat)
        if log_channel:
            await log_channel.send(embed=user_embed)

        await ctx.reply("Done")
        logger.info("Stat reset complete")

async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
