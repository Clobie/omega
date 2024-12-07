# cogs/template.py

import os
import discord
from discord.ext import commands
from core.omega import omega

class TemplateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                omega.db.run_script(('INSERT INTO discord_users (id, name, credits, message_count) VALUES (1, "User1", 100, 50)')(member.id, member.name, 100, 0))
                omega.logger.info(f'Inserted user into discord_users table - Name: {member.name}, ID: {member.id}')

async def setup(bot: commands.Bot):
    await bot.add_cog(TemplateCog(bot))