# cogs/template.py

import os
import discord
from discord.ext import commands
from core.omega import omega

class Asdf(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                query = f'INSERT INTO discord_users (id, name, credits, message_count) VALUES ({member.id}, {member.name}, 0, 0);'
                omega.logger.info(query)
                omega.db.run_script(query)

async def setup(bot: commands.Bot):
    await bot.add_cog(Asdf(bot))