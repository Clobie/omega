# cogs/reactor.py

from discord.ext import commands
import random
import requests
from utils.ai import ai
from utils.common import common
from utils.config import cfg
from utils.log import logger

class Reactor(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.respond_chance = 10

    async def react_gif(self, message):
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()
        search_string = ai.chat_completion(
            'gpt-4o-mini', 
            'Analyze the text and suggest a concise search string for finding a relevant GIF. Your search string should be short and relevant.',
            prompt
        )
        url = "https://api.giphy.com/v1/gifs/search"
        params = {
            "api_key": cfg.GIPHY_API_KEY,
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
        if common.chance(self.respond_chance):
            functions = [self.react_gif]
            selected_function = random.choice(functions)
            await selected_function(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reactor(bot))