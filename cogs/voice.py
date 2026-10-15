import asyncio
import datetime
import pytz
import logging
import discord
from discord.ext import commands

from config import config

logger = logging.getLogger(__name__)

class Voice(commands.Cog):
    """Voice channel utilities, logging, and protections."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.beast: int = 0
        self.no_disconnect: int = 1
        self.timeout_checker: dict[int, datetime.datetime] = {}

    async def log_vc_event(self, member: discord.Member, channel: discord.VoiceChannel, action: str):
        """Log voice join/leave events to the designated log channel."""
        if not member.guild:
            return
        log_channel = member.guild.get_channel(config.JOIN_LOG)
        if not log_channel:
            return

        color = discord.Color.from_rgb(0, 255, 0) if action == "join" else discord.Color.from_rgb(255, 0, 0)
        title = f"🔊 {member} joined {channel.name}" if action == "join" else f"🔇 {member} left {channel.name}"

        embed = discord.Embed(
            title=title,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.command(name="ring")
    async def ring(self, ctx: commands.Context, member: discord.Member):
        """Ring a user by toggling them to AFK channel and back twice."""
        role = ctx.guild.get_role(config.ROLE_USER)
        if role not in ctx.author.roles:
            await ctx.author.send("you don't have role")
            return

        sleep_channel = ctx.guild.afk_channel
        if sleep_channel is None:
            await ctx.send("⚠️ This server has no AFK channel set.")
            return

        if not member.voice or not member.voice.channel:
            await ctx.send(f"{member.mention} is not in vc")
            return

        voice_channel = member.voice.channel
        await ctx.send("got you dude")
        for _ in range(2):
            await member.move_to(sleep_channel)
            await asyncio.sleep(0.5)
            await member.move_to(voice_channel)
            await asyncio.sleep(0.5)

    @commands.command(name="moveall")
    async def moveall(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """Move all users in the author's voice channel to another channel."""
        role = ctx.guild.get_role(config.ROLE_USER)
        if role not in ctx.author.roles:
            await ctx.reply("you don't have role")
            return

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("you must be connected in a voice channel")
            return

        current_channel = ctx.author.voice.channel
        if current_channel == channel:
            await ctx.reply("you are already in that channel")
            return

        moved = 0
        for member in current_channel.members:
            try:
                await member.move_to(channel)
                moved += 1
            except discord.Forbidden:
                pass

        await ctx.send(f"🔊 moving all — {moved} members moved")

    @commands.command(name="act")
    async def act(self, ctx: commands.Context):
        """Check playing and streaming activities of voice members."""
        role = ctx.guild.get_role(config.ROLE_USER)
        if role not in ctx.author.roles:
            try:
                await ctx.message.delete()
            except Exception:
                pass
            await ctx.author.send("you don't have role")
            return

        check = True
        status_text = ""
        for vc in ctx.guild.voice_channels:
            for member in vc.members:
                for activity in member.activities:
                    if activity.type == discord.ActivityType.playing:
                        check = False
                        name = activity.name
                        if name.startswith("Valorant"):
                            name = "VALORANT"
                        status_text += f"**{member.display_name}** is currently playing: **{name}**\n"
                        break
                    elif activity.type == discord.ActivityType.streaming:
                        check = False
                        status_text += f"**{member.display_name}** is currently streaming: **{activity.name}**\n"
                        break

        if check:
            await ctx.send("Everyone is sleepin'")
        else:
            await ctx.send(status_text)

    @commands.command(name="beast")
    async def beast_mode(self, ctx: commands.Context):
        """Toggle anti-server-mute/deafen protection for target author."""
        if ctx.author.id != config.TARGET_ID:
            await ctx.reply("fuck you")
            return

        self.beast = 1 if self.beast == 0 else 0
        state_str = "ON" if self.beast == 1 else "OFF"
        await ctx.reply(f"Beast mode is {state_str}")

    @commands.command(name="nodc")
    async def nodc_mode(self, ctx: commands.Context):
        """Toggle anti-mass-disconnect timeout protection."""
        if ctx.author.id not in config.AUTHOR:
            await ctx.reply("fuck you")
            return

        self.no_disconnect = 1 if self.no_disconnect == 0 else 0
        state_str = "ON" if self.no_disconnect == 1 else "OFF"
        await ctx.reply(f"No Disconnect mode is {state_str}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice channel logging, disconnect moderation, and beast protection."""
        # ---------- LEAVE ----------
        if before.channel is not None and after.channel != before.channel:
            await self.log_vc_event(member, before.channel, "leave")

        # ---------- JOIN ----------
        if after.channel is not None and before.channel != after.channel:
            await self.log_vc_event(member, after.channel, "join")

        # ---------- NO DISCONNECT PROTECTION ----------
        if self.no_disconnect == 1 and member.guild:
            guild = member.guild
            try:
                async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.member_disconnect):
                    if (
                        (datetime.datetime.now(pytz.UTC) - entry.created_at).total_seconds() < 60
                        and getattr(entry.extra, "count", 0) > 4
                    ):
                        culprit = entry.user
                        text_channel = guild.get_channel(config.YAP_CHAT)
                        now_utc = datetime.datetime.now(pytz.UTC)

                        if self.timeout_checker.get(culprit.id, datetime.datetime.min.replace(tzinfo=pytz.UTC)) > now_utc:
                            logger.info(f"{culprit} is already timed-out")
                            continue

                        try:
                            await culprit.timeout(
                                datetime.timedelta(minutes=1),
                                reason="timed-out for frequently disconnecting member(s)"
                            )
                            logger.info(f"{culprit} timed out for mass disconnecting.")
                            self.timeout_checker[culprit.id] = now_utc + datetime.timedelta(minutes=1)
                        except Exception as e:
                            logger.error(f"Failed to timeout {culprit.mention}: {e}")

                        if text_channel:
                            await text_channel.send(
                                f"{culprit.mention} has been (or tried to) timed-out for frequently disconnecting member(s) in 2 minutes."
                                f"\n If it's not working properly then use `znodc` to turn it off"
                            )
            except discord.Forbidden:
                pass
            except Exception as e:
                logger.error(f"Audit log check failed: {e}")

        # ---------- BEAST MODE PROTECTION ----------
        if member.id == config.TARGET_ID and self.beast == 1:
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
                        logger.error(f"Failed to unmute/undeafen {member}: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))
