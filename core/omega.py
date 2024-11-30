# core/omega.py

import discord
from discord.ext import commands
from utils.cog import cog
from utils.config import cfg
from utils.log import logger

class Omega:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=cfg.COMMAND_PREFIX, intents=discord.Intents.all())

    async def run(self):
        logger.info('Starting bot...')

        self.bot.remove_command("help")

        @self.bot.event
        async def on_message(message):
            if message.author is self.bot.user:
                return
            await self.bot.process_commands(message)

        async with self.bot:
            await cog.load_cogs(self.bot)
            await self.bot.start(cfg.DISCORD_BOT_TOKEN)