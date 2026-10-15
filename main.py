import asyncio
import logging
import sys
from pathlib import Path

import discord
from discord.ext import commands

from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("FinalBot")

class FinalBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Asynchronously load all cogs in the cogs directory."""
        cogs_dir = Path(__file__).parent / "cogs"
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("__"):
                continue
            cog_name = f"cogs.{cog_file.stem}"
            try:
                await self.load_extension(cog_name)
                logger.info(f"Loaded extension: {cog_name}")
            except Exception as e:
                logger.error(f"Failed to load extension {cog_name}: {e}", exc_info=True)

    async def on_ready(self):
        activity = discord.Activity(type=discord.ActivityType.listening, name="yappin")
        await self.change_presence(status=discord.Status.idle, activity=activity)
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("Bot is ready and online.")

async def main():
    if not config.BOT_TOKEN:
        logger.critical("BOT_TOKEN is not configured! Please set it in .env or cfg.py.")
        sys.exit(1)

    bot = FinalBot()
    async with bot:
        await bot.start(config.BOT_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user.")
