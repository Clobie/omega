# core/omega.py

import discord
from discord.ext import commands
from utils.cog import cog
from utils.config import cfg
from utils.log import logger
from utils.status import status
from utils.common import common
from utils.credit import credit
from utils.role import role
from utils.database import db
from utils.ai import ai
from utils.embed import embed
from utils.coingecko import cg

class Omega:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=cfg.COMMAND_PREFIX, intents=discord.Intents.all())
        self.cog = cog
        self.cfg = cfg
        self.logger = logger
        self.status = status
        self.common = common
        self.credit = credit
        self.role = role
        self.db = db
        self.ai = ai
        self.embed = embed
        self.cg = cg

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

omega = Omega()