# utils/cog.py

import os
import ast
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Cog:
    def __init__(self, config):
        self.config = config

    async def import_cogs(self, bot):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                cog_name = filename[:-3]
                if not hasattr(self.config, cog_name):
                    self.config.set_variable(cog_name, 'enabled')
                    logger.info(f"Imported cog {cog_name} to config.")

    async def enable_cog(self, bot, cog_name):
        await bot.load_extension(cog_name)
        logger.info(f"Enabled cog: {cog_name}")

    async def disable_cog(self, bot, cog_name):
        await bot.unload_extension(cog_name)
        logger.info(f"Disabled cog: {cog_name}")

    async def load_cogs(self, bot):
        enabled_cogs = []
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                cog_name = filename[:-3]
                #if hasattr(self.config, cog_name) and getattr(self.config, cog_name) == 'enabled':
                enabled_cogs.append(f'cogs.{cog_name}')
        for cog in enabled_cogs:
            await bot.load_extension(cog)
            logger.info(f"Loaded cog: {cog}")

    async def reload_cog(self, bot, cog_name):
        await bot.reload_extension(cog_name)
        logger.info(f"Reloaded cog: {cog_name}")

    async def test_cog_experimental(self, bot, cog_name, cog_data):
        logger.debug(f"Testing experimental cog: {cog_name}")
        cog_path = f"./cogs/experimental/{cog_name}.py"
        if os.path.exists(cog_path):
            if cog_name in bot.extensions:
                await bot.unload_extension(cog_name)
        try:
            ast.parse(cog_data)
        except SyntaxError as e:
            logger.error(f"Syntax error in cog {cog_name}: {e}")
            return f"Syntax errors: {e}"

        with open(cog_path, 'w') as f:
            f.write(cog_data)
        try:
            await bot.load_extension(cog_name)
        except Exception as e:
            with open(f'./cogs/experimental/failed/{cog_name}.py', 'w') as f:
                f.write(cog_data)
            logger.error(f"Failed loading experimental cog {cog_name}: {e}")
            return f"Loading failed: {e}"
        os.rename(cog_path, f'./cogs/experimental/success/{cog_name}.py')
        logger.info(f"Successfully loaded experimental cog: {cog_name}")
        return "Success"

def instantiate(config):
    return Cog(config)