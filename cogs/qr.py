# cogs/qr.py

import os
import discord
import pyqrcode
from discord.ext import commands

class QR(commands.Cog, name="qr"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="qr")
    async def my_command(self, context, *, msg):
        """
        Generates a QR code from entered text.
        """
        qrobj = pyqrcode.create(msg)
        qrobj.png('qr.png', scale=8)
        await context.send(file=discord.File('qr.png'))
        os.remove("qr.png")

# Cog setup function
async def setup(bot: commands.Bot):
    await bot.add_cog(QR(bot))