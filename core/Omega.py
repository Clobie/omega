# core/omega.py

import discord
from discord.ext import commands
from utils.logger import logger
from utils.config import config

class Omega:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=discord.Intents.all())
    
    async def run(self):
        logger.info('Starting bot...')
        self.bot.remove_command("help")

        @self.bot.event
        async def on_ready():
            logger.info(f'Logged in as {self.bot.user}!')

        @self.bot.event
        async def on_message(message):
            if message.author is self.bot.user:
                return
            await self.bot.process_commands(message)

        async with self.bot:
            await self.bot.start(config.DISCORD_BOT_TOKEN)