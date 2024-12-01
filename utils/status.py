# utils/status.py

import discord
from utils.config import cfg

class Status:
    def __init__(self):
        self.prefix = cfg.COMMAND_PREFIX

    async def update(self, bot, type, data, url=''):
        activity = None
        if type == "game":
            activity = discord.Game(name=data)
        elif type == "streaming":
            activity = discord.Streaming(name=data, url=url)
        elif type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=data)
        elif type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=data)
        else:
            activity = discord.Activity(type=discord.ActivityType.listening, name=f" to {cfg.COMMAND_PREFIX}help")
        await bot.change_presence(activity=activity)

status = Status()