import discord
from discord.ext import commands
import os
import json

class CogManager:
    def __init__(self, bot, omega, config, logger, cogs_folder='./cogs'):
        self.bot = bot
        self.omega = omega
        self.cogs_folder = cogs_folder
        self.config = config
        self.logger = logger
        self.config_file = './config/cogs.conf'
        self.enabled_cogs = self._load_enabled_cogs()

    def load_cog(self, cog_name):
        """Load a specific cog."""
        try:
            path = f'{self.cogs_folder.replace("/", ".")}.{cog_name}'
            cog_module = __import__(path, fromlist=[cog_name])
            cog_class = getattr(cog_module, cog_name)
            self.bot.add_cog(cog_class(self.bot, self.omega))
            self.logger.info(f"Cog '{cog_name}' loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load cog '{cog_name}': {e}")

    def _load_enabled_cogs(self):
        """Load the list of enabled cogs from the config file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                return json.load(file).get('enabled', [])
        return []

    def _save_enabled_cogs(self):
        """Save the list of enabled cogs to the config file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as file:
            json.dump({'enabled': self.enabled_cogs}, file)

    def list_cogs(self):
        """List all available cogs in the cogs folder."""
        return [f[:-3] for f in os.listdir(self.cogs_folder) if f.endswith('.py')]

    def unload_cog(self, cog_name):
        """Unload a specific cog."""
        try:
            self.bot.unload_extension(f'{self.cogs_folder.replace("/", ".")}.{cog_name}')
            self.logger.info(f"Cog '{cog_name}' unloaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to unload cog '{cog_name}': {e}")

    def reload_cog(self, cog_name):
        """Reload a specific cog."""
        try:
            self.unload_cog(cog_name)
            self.load_cog(cog_name)
            self.logger.info(f"Cog '{cog_name}' reloaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to reload cog '{cog_name}': {e}")

    def enable_cog(self, cog_name):
        """Enable a cog to auto-load on initialization."""
        if cog_name not in self.enabled_cogs:
            self.enabled_cogs.append(cog_name)
            self._save_enabled_cogs()
            self.logger.info(f"Cog '{cog_name}' enabled.")

    def disable_cog(self, cog_name):
        """Disable a cog from auto-loading."""
        if cog_name in self.enabled_cogs:
            self.enabled_cogs.remove(cog_name)
            self._save_enabled_cogs()
            self.logger.info(f"Cog '{cog_name}' disabled.")

    def load_enabled_cogs(self):
        """Load all enabled cogs."""
        for cog in self.enabled_cogs:
            self.load_cog(cog)