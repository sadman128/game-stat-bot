import os
import sys
import asyncio
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
        """Restart the bot process in-place (Author only)."""
        if ctx.author.id not in config.AUTHOR:
            await ctx.reply("You are not authorized to do that.")
            return

        await ctx.reply("🔄 Restarting bot...")
        logger.info(f"Restart initiated by {ctx.author} ({ctx.author.id})")

        # Allow message to send and flush Discord gateway
        await asyncio.sleep(1)

        # Close Discord bot connection gracefully
        try:
            await self.bot.close()
        except Exception as e:
            logger.error(f"Error closing bot session: {e}")

        # In-place process restart using current python executable and args (/home/container/main.py)
        os.execv(sys.executable, [sys.executable] + sys.argv)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
