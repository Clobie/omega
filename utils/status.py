# utils/status.py

import discord
import json
from utils.common import Common
from utils.config import cfg
from utils.log import logger

class Status:
    def __init__(self):
        pass

    async def update(self, bot, data):
        await bot.change_presence(activity=discord.Game(name=data))

status = Status()