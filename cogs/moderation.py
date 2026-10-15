import io
import logging
import discord
from discord.ext import commands

from config import config

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    """Moderation tools, audit logging for deleted messages and role updates."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="msg")
    async def msg(self, ctx: commands.Context, *, message_content: str = None):
        """Admin command to re-send a message and attachments via the bot."""
        user = ctx.author
        role = ctx.guild.get_role(config.ROLE_ADMIN)
        if role not in user.roles:
            try:
                await ctx.message.delete()
            except Exception:
                pass
            await user.send("You don't have the required role to use this command.")
            return

        files = []
        for attachment in ctx.message.attachments:
            try:
                files.append(await attachment.to_file())
            except Exception as e:
                logger.error(f"Failed to get attachment: {e}")

        if not message_content and not files:
            await user.send("⚠️ You must provide a message or an attachment.")
            return

        try:
            await ctx.message.delete()
        except Exception as e:
            logger.error(f"Failed to delete original message: {e}")
            return

        await ctx.send(content=message_content, files=files if files else None)

    @commands.command(name="dm")
    async def dm(self, ctx: commands.Context, member: discord.Member, *, dm_message: str):
        """Author command to send a direct message to a member through the bot."""
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
                embed.set_footer(text="Logged by bot")
                await log_channel.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I cannot DM this user.")
        except Exception as e:
            await ctx.send("⚠️ An error occurred.")
            logger.error(f"Error sending DM: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log deleted messages and re-upload deleted attachments."""
        if not message.guild or message.author.bot:
            return

        log_channel = message.guild.get_channel(config.DELETE_LOG)
        if not log_channel:
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
                    file_data = await attachment.read()
                    file = discord.File(
                        io.BytesIO(file_data),
                        filename=attachment.filename
                    )
                    files.append(file)
                    attachment_names.append(attachment.filename)

                    if i == 0 and attachment.content_type and attachment.content_type.startswith("image/"):
                        embed.set_image(url=f"attachment://{attachment.filename}")
                except Exception as e:
                    logger.error(f"Failed to download attachment {attachment.filename}: {e}")

            embed.add_field(
                name="Attachments",
                value="\n".join(attachment_names),
                inline=False
            )

        embed.set_footer(text=f"Message ID: {message.id} • Author ID: {message.author.id}")
        await log_channel.send(embed=embed, files=files)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log role changes to the audit channel."""
        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles

        if not added_roles and not removed_roles:
            return

        log_channel = self.bot.get_channel(config.DELETE_LOG)
        if not log_channel:
            return

        executor = None
        try:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
                if entry.target.id == after.id:
                    executor = entry.user
                    break
        except Exception as e:
            logger.error(f"Failed to fetch audit logs for role update: {e}")

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

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
