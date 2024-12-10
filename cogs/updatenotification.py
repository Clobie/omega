# cogs/updatenotification.py

import os
import discord
from discord.ext import commands
from core.omega import omega

class UpdateNotification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        omega.logger.info(f'Logged in as {self.bot.user}')
        last_commit_file = './.last_commit'
        if os.path.exists(last_commit_file):
            try:
                with open(last_commit_file, 'r') as file:
                    last_commit_id = file.read().strip()
                omega.logger.info(f'Last commit ID: {last_commit_id}')
                channel = self.bot.get_channel(int(omega.cfg.UPDATE_CHANNEL))
                if channel:
                    embed = discord.Embed(title="Update Notification", description="", color=omega.cfg.PRIMARYCOLOR)
                    embed.add_field(name="Commit ID", value=last_commit_id, inline=False)
                    embed.add_field(name="Changes", value=f"[View changes here](https://github.com/Clobie/omega/commit/{last_commit_id})", inline=False)
                    await channel.send(embed=embed)
                else:
                    omega.logger.warning(f"Channel with ID {omega.cfg.UPDATE_CHANNEL} not found.")
                os.remove(last_commit_file)
                omega.logger.info(f"Deleted file {last_commit_file}")
            except Exception as e:
                omega.logger.error(f"Failed to process {last_commit_file}: {e}")

async def setup(bot):
    await bot.add_cog(UpdateNotification(bot))