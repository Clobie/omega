# cogs/template.py

import discord
from discord.ext import commands, tasks
import logging
from typing import Optional

class TemplateCog(commands.Cog):
    """A template cog for Discord bot development."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{self.__class__.__name__} initialized.")
        self.repeating_task.start()

    # A task loop that runs every 10 minutes
    @tasks.loop(minutes=10.0)
    async def repeating_task(self):
        """A repeating task that runs every 10 minutes."""
        self.logger.info("Running repeating task...")
        # Example task action: You can add code here to execute regularly

    # Run this before the repeating task starts
    @repeating_task.before_loop
    async def before_repeating_task(self):
        await self.bot.wait_until_ready()
        self.logger.info("Repeating task about to start...")

    # Listen for the bot being ready
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready."""
        self.logger.info(f"{self.__class__.__name__} is ready.")

    # A command example
    @commands.command(name='example')
    async def example_command(self, ctx: commands.Context, arg: Optional[str] = None):
        """An example command."""
        await ctx.send(f"Example command received with argument: {arg}")
        self.logger.debug(f"example_command triggered with arg={arg}")

async def setup(bot: commands.Bot):
    cog = TemplateCog(bot)
    await bot.add_cog(cog)
    cog.logger.info(f"{cog.__class__.__name__} added to bot.")