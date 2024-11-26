# cogs/reactor.py

from discord.ext import commands
import random
import logging
import requests
import utils.config
import utils.ai as ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Reactor(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai = ai.instantiate()
        self.cfg = utils.config.instantiate('./config/bot.conf')
        self.respond_chance = 10

    def chance(self, percent):
        return random.random() < (percent / 100)
    
    async def react_emoji(self, message):
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()
        sentiment_emoji = self.ai.get_emoji_sentiment(prompt)
        await message.add_reaction(sentiment_emoji)

    async def react_gif(self, message):
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()
        search_string = self.ai.generate_gif_search_string(prompt)
        url = "https://api.giphy.com/v1/gifs/search"
        params = {
            "api_key": self.cfg.GIPHY_API_KEY,
            "q": search_string,
            "limit": 25,
            "offset": random.randint(0, 24),
            "rating": "r",
            "lang": "en",
            "bundle": "messaging_non_clips"
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data['data']:
            react_gif_url = data['data'][0]['url']
            await message.channel.send(react_gif_url)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        if self.chance(self.respond_chance):
            functions = [self.react_gif]
            selected_function = random.choice(functions)
            await selected_function(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reactor(bot))