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
            "apikey": f"{omega.cfg.GOKAPI_API_KEY}"
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
        elif response.status_code == 400:
            await ctx.send("Invalid input.")
        elif response.status_code == 401:
            await ctx.send("Invalid API key provided or not logged in as admin.")
        else:
            await ctx.send(f"Failed to retrieve the file list. {response.status_code}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Gokapi(bot))