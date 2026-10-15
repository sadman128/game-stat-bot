import random
import asyncio
import discord
from discord.ext import commands

from config import config

class RPSView(discord.ui.View):
    def __init__(self, author: discord.Member, opponent: discord.Member):
        super().__init__(timeout=300)
        self.author = author
        self.opponent = opponent
        self.choices = {}

    @discord.ui.select(
        placeholder="Choose Rock, Paper, or Scissors",
        options=[
            discord.SelectOption(label="Rock", emoji="✊"),
            discord.SelectOption(label="Paper", emoji="✋"),
            discord.SelectOption(label="Scissors", emoji="✌️"),
        ],
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user not in (self.author, self.opponent):
            await interaction.response.send_message(
                "❌ You are not part of this game!",
                ephemeral=True
            )
            return

        if interaction.user.id in self.choices:
            await interaction.response.send_message(
                "❌ You have already made your choice!",
                ephemeral=True
            )
            return

        self.choices[interaction.user.id] = select.values[0].lower()
        await interaction.response.send_message(f"✅ You selected **{select.values[0]}**", ephemeral=True)

        if len(self.choices) < 2:
            return

        p1 = self.author
        p2 = self.opponent
        c1 = self.choices[p1.id]
        c2 = self.choices[p2.id]

        def get_result():
            if c1 == c2:
                return f"🤝 **It's a draw!** Both chose **{c1.capitalize()}**"
            if (
                (c1 == "rock" and c2 == "scissors") or
                (c1 == "paper" and c2 == "rock") or
                (c1 == "scissors" and c2 == "paper")
            ):
                return f"🎉 **{p1.mention} wins!** ({c1.capitalize()} beats {c2.capitalize()})"
            return f"🎉 **{p2.mention} wins!** ({c2.capitalize()} beats {c1.capitalize()})"

        # Dramatic reveal countdown
        await interaction.message.edit(content="✊ ✋ ✌️ **Rock...**", view=None)
        await asyncio.sleep(1)
        await interaction.message.edit(content="✊ ✋ ✌️ **Rock... Paper...**", view=None)
        await asyncio.sleep(1)
        await interaction.message.edit(content="✊ ✋ ✌️ **Rock... Paper... Scissors...**", view=None)
        await asyncio.sleep(2)

        await interaction.message.edit(
            content=(
                f"🎮 **Rock Paper Scissors**\n\n"
                f"{p1.mention} chose **{c1.capitalize()}**\n"
                f"{p2.mention} chose **{c2.capitalize()}**\n\n"
                f"{get_result()}"
            )
        )
        self.stop()

class General(commands.Cog):
    """General utility and fun commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Simple ping command."""
        await ctx.send("pong")

    @commands.command(name="check")
    async def check(self, ctx: commands.Context):
        """Check if user has the configured member role."""
        user = ctx.author
        guild = ctx.guild
        role = guild.get_role(config.ROLE_USER)
        if role in user.roles:
            await ctx.reply("you have role")
        else:
            await ctx.reply("you don't have role")

    @commands.command(name="help")
    async def help(self, ctx: commands.Context):
        """Custom help message."""
        msg = "All commands for **gugu gaga** brains 🌻. Most of these works with <bot-cum> role \n\n"
        msg += "> Use ``zring`` <mention a user | use ``@``> to ring them\n"
        msg += "> Use ``zmoveall`` <mention a voice channel | use ``#!``> to move all users to another channel\n"
        msg += "> Use ``zact`` to get the **activity** of current VC members\n"
        msg += "> Use ``zflip`` to flip a **coin** (it's totally random — believe me or fuck off)\n"
        msg += "> Use ``zrps`` to play **Rock, Paper, Scissors**\n"
        msg += "> Use ``zping`` to get a **pong**\n"
        msg += "> Use ``zcheck`` to check if you have the config **role**\n"
        msg += "> Use ``zmsg`` <your message> to resend your message using the **bot**\n"
        msg += "> Use ``znodc`` to turn off **no-disconnect** mode\n"
        msg += "> Use ``zresetstat`` to reset all **stat data** (admin only)\n"
        await ctx.reply(msg)

    @commands.command(name="flip")
    async def flip(self, ctx: commands.Context):
        """Flip a coin."""
        msg = await ctx.send("Flipping a coin...")
        result = random.choice(["It's **Heads**!", "It's **Tails**!"])
        await asyncio.sleep(3)
        await msg.edit(content=result)

    @commands.command(name="rps")
    async def rps(self, ctx: commands.Context, opponent: discord.Member = None):
        """Play Rock Paper Scissors with another member."""
        if opponent is None:
            await ctx.reply("❌ Please mention an opponent to play with.")
            return

        if opponent.bot:
            await ctx.reply("❌ You can't play with a bot.")
            return

        if opponent == ctx.author:
            await ctx.reply("❌ You can't play against yourself.")
            return

        await ctx.reply(
            f"🎮 **Rock Paper Scissors**\n"
            f"{ctx.author.mention} vs {opponent.mention}\n\n"
            f"Both players, make your move:",
            view=RPSView(ctx.author, opponent)
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
