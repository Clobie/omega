# utils/cog.py

import os
import json
from utils.log import logger

CONFIG_PATH = './config/cogs.json'

class Cog:
    def __init__(self):
        self.config = self.load_config()
        self.import_cogs()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as file:
                return json.load(file)
        return {}

    def save_config(self):
        with open(CONFIG_PATH, 'w') as file:
            json.dump(self.config, file, indent=4)

    def import_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                cog_name = filename[:-3]
                if cog_name not in self.config:
                    self.config[cog_name] = 'enabled'
                    logger.info(f"Imported cog {cog_name} to config.")
        self.save_config()

    async def enable_cog(self, bot, cog_name):
        await bot.load_extension(cog_name)
        logger.info(f"Enabled cog: {cog_name}")

    async def disable_cog(self, bot, cog_name):
        await bot.unload_extension(cog_name)
        logger.info(f"Disabled cog: {cog_name}")

    async def load_cogs(self, bot):
        enabled_cogs = [cog for cog, status in self.config.items() if status == 'enabled']
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                cog_name = filename[:-3]
                if cog_name in enabled_cogs:
                    full_name = f'cogs.{cog_name}'
                    await bot.load_extension(full_name)
                    logger.info(f"Loaded cog: {full_name}")

    async def reload_cog(self, bot, cog_name):
        await bot.reload_extension(cog_name)
        logger.info(f"Reloaded cog: {cog_name}")

cog = Cog()