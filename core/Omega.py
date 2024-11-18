from discord.ext import commands
from core.CogManager import CogManager
from utils.Logger import Logger
import utils.Config

class Omega:
    def __init__(self, bot_token):
        self.logger = Logger()
        self.config = utils.Config.load_config()
        self.bot = commands.Bot(command_prefix=self.config['prefix'])
        self.cogmanager = CogManager(self.bot, self, self.config, self.logger)

    def run(self):
        @self.bot.event
        async def on_ready():
            self.logger.info(f'Logged in as {self.bot.user}!')
        self.logger.info('Starting bot...')
        self.bot.run(self.bot_token)