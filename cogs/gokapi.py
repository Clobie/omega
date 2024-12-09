# cogs/gokapi.py

import discord
from discord.ext import commands
import requests
from core.omega import omega

class Gokapi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='files')
    async def list_files(self, ctx):
        api_url = "http://files.clobie.net/api/files/list"
        headers = {
            "accept": "application/json",
            "apikey": omega.cfg.GOKAPI_API_KEY
        }

        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            files = response.json()
            embed = discord.Embed(title="File List", color=discord.Color(int(omega.cfg.PRIMARYCOLOR, 16)))
            
            for file in files:
                embed.add_field(
                    name=file['Name'],
                    value=f"[Download]({file['UrlDownload']})",
                    inline=False
                )

            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to retrieve the file list.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Gokapi(bot))