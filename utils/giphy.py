# utils/giphy.py

import random
import requests
from utils.ai import ai
from utils.common import common
from utils.config import cfg
from utils.log import logger

class Giphy():
    def __init__(self):
        self.respond_chance = 10
        self.api_url = "https://api.giphy.com/v1/gifs/search"

    async def get_react_gif_url(self, message):
        search_string = ai.chat_completion(
            'gpt-4o-mini',
            'Analyze the text and suggest a concise search string for finding a relevant GIF. Your search string should be short and relevant.',
            message
        )
        params = {
            "api_key": cfg.GIPHY_API_KEY,
            "q": search_string,
            "limit": 25,
            "offset": random.randint(0, 24),
            "rating": "r",
            "lang": "en",
            "bundle": "messaging_non_clips"
        }
        response = requests.get(self.api_url, params=params)
        data = response.json()
        if data['data']:
            react_gif_url = data['data'][0]['url']
            return react_gif_url

gfy = Giphy()
