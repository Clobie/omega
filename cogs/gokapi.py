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
        base_url = omega.cfg.GOKAPI_BASE_URL
        api_url = base_url + "api/files/list"
        headers = {
            "accept": "application/json",
            "apikey": f"{omega.cfg.GOKAPI_API_KEY}"
        }
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            files = response.json()
            embed = discord.Embed(
                title="📂 File List",
                description="Here are the available files:",
                color=discord.Color(int(omega.cfg.PRIMARYCOLOR, 16))
            )
            for file in files:
                file_link = f"[{file['Name']}]({file['UrlDownload']})"
                embed.add_field(
                    name="",
                    value=file_link,
                    inline=False
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Failed to retrieve the file list. {response.status_code}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Gokapi(bot))
