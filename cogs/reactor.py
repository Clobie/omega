import discord
from discord.ext import commands
import random
import logging
import requests
import aiohttp
import io
import utils.config
import utils.ai as ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Reactor(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai = ai.instantiate()
        self.cfg = utils.config.instantiate('./config/bot.conf')
    
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
    
    async def react_conversate(self, message):
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()
        result = self.ai.conversate_no_context(prompt)
        await message.channel.send(result)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        functions = [self.react_gif, self.react_conversate]
        selected_function = random.choice(functions)
        await selected_function(message)
    
    @commands.command(name='generate')
    async def generate_image(self, ctx, *, prompt):
        image_url = self.ai.generate_image(prompt)
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    file = discord.File(io.BytesIO(image_data), filename="image.png")
                    await ctx.send(file=file)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reactor(bot))