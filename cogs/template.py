# cogs/template.py

import os
import discord
from discord.ext import commands
from utils.config import cfg
from utils.log import logger
from utils.status import status
from utils.common import common
from utils.credit import credit
from utils.role import role

class TemplateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(TemplateCog(bot))