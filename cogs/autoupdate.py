# cogs/update_checker.py

import subprocess
import logging
from discord.ext import commands
from utils.log import logger

class UpdateCheckerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 1256848459558817812  # Channel to post updates

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
            
            # Check for local changes
            result = subprocess.run(['git', 'status', '-uno'], capture_output=True, text=True)
            if "up to date" in result.stdout:
                logger.info("No updates available.")
                await channel.send("No updates available.")
                return

            # Notify starting update
            await channel.send("Starting update...")
            logger.info("Starting update...")
            
            # Run the update script
            result = subprocess.run(['/tools/update.sh'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Error running update script: {result.stderr.strip()}")
                await channel.send("Update failed.")
                return
            
            # Notify update complete
            await channel.send("Update completed successfully.")
            logger.info("Update completed successfully.")

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            await channel.send("An error occurred during the update check.")

async def setup(bot: commands.Bot):
    await bot.add_cog(UpdateCheckerCog(bot))