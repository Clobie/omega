# utils/common.py

import discord
from datetime import datetime
from utils.config import cfg

class Embed:
    def __init__(self):
        self.url = "https://github.com/Clobie/omega"
        self.icon_url = "https://github.com/Clobie/omega/blob/main/assets/omega.png?raw=true"

    def create_embed_generic(self, title, description, color):
        embed = discord.Embed(
            title=title,
            description=description,
            colour=color,
            timestamp=datetime.now()
        )
        embed.set_author(name="Omega",url=self.url,icon_url=self.icon_url)
        embed.set_thumbnail(url=self.icon_url)
        embed.set_footer(text="Omega",icon_url=self.icon_url)
        return embed

    def create_embed_error(self, title, description):
        return self.create_embed_generic(f"Error: {title}", description, discord.Color(int(cfg.ERRORCOLOR, 16)))
    
    def create_embed_info(self, title, description):
        return self.create_embed_generic(f"Info: {title}", description, discord.Color(int(cfg.INFOCOLOR, 16)))

    def create_embed(self, title, description):
        return self.create_embed_generic(title, description, discord.Color(int(cfg.PRIMARYCOLOR, 16)))
    
embed = Embed()