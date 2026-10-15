import subprocess
import logging
from discord.ext import commands

from config import config

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    """Administrative commands for bot maintenance."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="restart")
    async def restart(self, ctx: commands.Context):
        """Restart bot via PM2 (Author only)."""
        if ctx.author.id not in config.AUTHOR:
            await ctx.reply("You are not authorized to do that.")
            return

        await ctx.reply("Restarting bot...")
        logger.info(f"Restart initiated by {ctx.author} ({ctx.author.id})")

        try:
            subprocess.Popen(
                ["pm2", "restart", "discord-bot"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            logger.error(f"Failed to execute PM2 restart: {e}")
            await ctx.send(f"⚠️ Failed to trigger restart command: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
