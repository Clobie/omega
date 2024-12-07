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
            query = f"INSERT IGNORE INTO discord_servers (servername, server_id, credits) VALUES ('{guild.name}', {guild.id}, 0)"
            result = omega.db.run_script(query)
            print(result)
            for member in guild.members:
                query = f"INSERT IGNORE INTO discord_users (username, user_id, credits) VALUES ('{member.name}', {member.id}, 0)"
                omega.logger.info(query)
                result = omega.db.run_script(query)
                print(result)

async def setup(bot: commands.Bot):
    await bot.add_cog(Asdf(bot))