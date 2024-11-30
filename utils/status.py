# utils/status.py

import discord

class Status:
    def __init__(self):
        pass

    async def update(self, bot, data):
        await bot.change_presence(activity=discord.Game(name=data))

status = Status()