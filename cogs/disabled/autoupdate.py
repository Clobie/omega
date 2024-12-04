# cogs/autoupdate.py

import os
import subprocess
import discord
from discord.ext import commands, tasks
from utils.config import cfg
from utils.log import logger
from utils.status import status
from utils.common import common

class UpdateCheckerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 1256848459558817812  # Channel to post updates
        self.update_check.start()  # Start the task when the cog is loaded
        self.last_commit_message = None  # To store the last commit message

    @tasks.loop(seconds=15)  # Task runs every 15 seconds
    async def update_check(self):
        await self.check_for_updates()

    @update_check.before_loop
    async def before_update_check(self):
        await self.bot.wait_until_ready()  # Wait until the bot is ready

    async def check_for_updates(self):
        """Check for updates and run update script if available."""
        channel = self.bot.get_channel(self.channel_id)
        if channel is None:
            logger.error("Channel not found.")
            return
            
        try:
            logger.info("Checking for updates...")
            # Check for git updates
            result = subprocess.run(['git', 'fetch'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Error fetching updates: {result.stderr.strip()}")
                await channel.send("Error checking for updates.")
                return
            
            result = subprocess.run(['git', 'status', '-uno'], capture_output=True, text=True)
            if "up to date" in result.stdout:
                logger.info("No updates available.")
                return

            # Get the latest commit message
            commit_info = subprocess.run(['git', 'log', '-1', '--pretty=%B'], capture_output=True, text=True)
            self.last_commit_message = commit_info.stdout.strip()

            await channel.send(f"Starting update to: {self.last_commit_message}")
            logger.info(f"Starting update to: {self.last_commit_message}")
            
            # Run update script in the background
            subprocess.Popen(['./tools/update.sh'])
            
            await channel.send("Update initiated. The process will run in the background.")
            logger.info("Update initiated. The process will run in the background.")
            
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            await channel.send("An error occurred during the update check.")

async def setup(bot: commands.Bot):
    await bot.add_cog(UpdateCheckerCog(bot))