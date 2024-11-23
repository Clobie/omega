# core/omega.py

import discord
from discord.ext import commands
import utils.config
import utils.cog
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Omega:
    def __init__(self):
        self.cfg = utils.config.instantiate('./config/bot.conf')
        self.cog = utils.cog.instantiate(self.cfg)
        self.bot = commands.Bot(command_prefix=self.cfg.COMMAND_PREFIX, intents=discord.Intents.all())

    async def run(self):
        logger.info('Starting bot...')

        self.bot.remove_command("help")

        @self.bot.event
        async def on_message(message):
            if message.author is self.bot.user:
                return
            await self.bot.process_commands(message)

        async with self.bot:
            await self.cog.load_cogs(self.bot)
            await self.bot.start(self.cfg.DISCORD_BOT_TOKEN)