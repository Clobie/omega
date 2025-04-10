# cogs/spam_delete.py

from discord.ext import commands
from core.omega import omega

class SpamDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content == "The world has been saved.":
            await message.delete()
    
async def setup(bot):
    await bot.add_cog(SpamDelete(bot))