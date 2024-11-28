# utils/cog.py

import os
import ast
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    async def test_cog_experimental(self, bot, cog_name, cog_data):
        logger.debug(f"Testing experimental cog: {cog_name}")
        cog_path = f"./cogs/experimental/{cog_name}.py"
        cog_ext_name = f"cogs.experimental.{cog_name}"
        if os.path.exists(cog_path):
            if cog_ext_name in bot.extensions:
                await bot.unload_extension(cog_ext_name)
        try:
            ast.parse(cog_data)
        except SyntaxError as e:
            logger.error(f"Syntax error in cog {cog_ext_name}: {e}")
            return f"Syntax errors: {e}"

        with open(cog_path, 'w') as f:
            f.write(cog_data)
        try:
            await bot.load_extension(cog_ext_name)
        except Exception as e:
            with open(f'./cogs/experimental/failed/{cog_name}.py', 'w') as f:
                f.write(cog_data)
            logger.error(f"Failed loading experimental cog {cog_name}: {e}")
            return f"Loading failed: {e}"
        os.rename(cog_path, f'./cogs/experimental/success/{cog_name}.py')
        logger.info(f"Successfully loaded experimental cog: {cog_name}")
        return "Success"

def instantiate():
    return Cog()