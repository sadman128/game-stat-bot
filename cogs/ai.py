import queue
import threading
import logging
from collections import deque
import asyncio
import json
import requests
import discord
from discord.ext import commands

from config import config

logger = logging.getLogger(__name__)

class AI(commands.Cog):
    """AI Assistant cog for server interactions via OpenRouter API."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.conversation_memory = deque(maxlen=6)
        self.message_queue = queue.Queue(maxsize=50)
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._ai_worker, daemon=True)
        self.worker_thread.start()

    def cog_unload(self):
        self.stop_event.set()

    def _get_ai_reply_sync(self, user_message: str) -> str:
        """Synchronously query the OpenRouter endpoint using requests."""
        url = config.AI_BASE_URL.rstrip("/")
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {config.AI_TOKEN}",
            "Content-Type": "application/json"
        }
        if getattr(config, "AI_SITE_URL", ""):
            headers["HTTP-Referer"] = config.AI_SITE_URL
        if getattr(config, "AI_SITE_NAME", ""):
            headers["X-OpenRouter-Title"] = config.AI_SITE_NAME

        payload = {
            "model": config.AI_MODEL,
            "messages": [
                {"role": "system", "content": config.AI_SYSTEM_PROMPT},
                {"role": "system", "content": "Recent chat history:\n" + "\n".join(self.conversation_memory)},
                {"role": "user", "content": user_message}
            ],
            "top_p": 0.8,
            "temperature": 0.7,
            "max_tokens": 500,
            "presence_penalty": 0,
            "frequency_penalty": 0.2
        }

        try:
            response = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(payload),
                timeout=45
            )
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            return reply[:1800] if reply else ":zipper_mouth:"
        except Exception as e:
            logger.error(f"OpenRouter request error: {e}")
            raise e

    def _ai_worker(self):
        """Background worker consuming messages from the queue."""
        while not self.stop_event.is_set():
            try:
                item = self.message_queue.get(timeout=1)
            except queue.Empty:
                continue

            message, content = item
            try:
                formatted_user_msg = (
                    f"@{message.author.name}(nickname : '{message.author.display_name}' , "
                    f"usercode : '{message.author.id}') : {' '.join(content.split())}"
                )
                reply = self._get_ai_reply_sync(formatted_user_msg)

                self.conversation_memory.append(formatted_user_msg)
                self.conversation_memory.append(f"ai reply : {' '.join(reply.split())}")

                asyncio.run_coroutine_threadsafe(
                    self._send_reply(message, reply),
                    self.bot.loop
                )
            except Exception as e:
                logger.error(f"Error processing AI message: {e}")
                asyncio.run_coroutine_threadsafe(
                    self._send_reply(message, "❌ AI error occurred."),
                    self.bot.loop
                )
            finally:
                self.message_queue.task_done()

    async def _send_reply(self, message: discord.Message, reply: str):
        """Send message reply with a typing indicator."""
        try:
            async with message.channel.typing():
                await message.reply(reply)
        except Exception as e:
            logger.error(f"Failed to send AI reply: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Intercept messages directed to the dedicated AI channel."""
        if message.author.bot:
            return

        if message.channel.id != config.AI_CHANNEL:
            return

        if not any(role.id == config.ROLE_USER for role in message.author.roles):
            await message.reply("❌ You need the **[bot-cum]** role to use this channel.")
            return

        if self.message_queue.full():
            await message.reply("⏳ AI is busy, try again later.")
            return

        content = str(message.content)
        for user in message.mentions:
            content = content.replace(
                user.mention,
                f"@{user.name}(nickname : '{user.display_name}' , usercode : '{user.id}')",
            )

        self.message_queue.put((message, content))

async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
