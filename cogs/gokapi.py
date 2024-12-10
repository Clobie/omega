# cogs/gokapi.py

import discord
from discord.ext import commands
import requests
import mimetypes
from core.omega import omega

class Gokapi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = omega.cfg.GOKAPI_BASE_URL
        self.file_list_api_url = self.base_url + "api/files/list"
        self.file_save_api_url = self.base_url + "api/files/add"
        

    @commands.command(name='files')
    async def list_files(self, ctx):
        """
        List available files to download
        """
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
                color=omega.cfg.PRIMARYCOLOR
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
        
    @commands.command(name='save')
    async def save_file(self, ctx):
        """Reply to a message to save it"""
        allowed_downloads: int = 0
        expiry_days: int = 0
        password: str = None
        if ctx.message.reference is None:
            await ctx.send("Please reply to a message with attachments.")
            return
        replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if len(replied_message.attachments) == 0:
            await ctx.send("The replied message does not contain any attachments.")
            return
        for file_attachment in replied_message.attachments:
            file_content = await file_attachment.read()
            headers = {
                "accept": "application/json",
                "apikey": f"{omega.cfg.GOKAPI_API_KEY}",
                "Content-Type": "application/octet-stream"
            }
            data = {
                "allowedDownloads": allowed_downloads,
                "expiryDays": expiry_days,
                "password": password
            }
            file_type, _ = mimetypes.guess_type(file_attachment.filename)
            files = {
                "file": (file_attachment.filename, file_content, file_type or "application/octet-stream")
            }

            response = requests.post(self.file_save_api_url, headers=headers, files=files, data=data)
            if response.status_code == 201:
                data = response.json()
                if data["Result"] == "OK":
                    url_download = data["FileInfo"]["UrlDownload"]
                    await ctx.send(f"File uploaded successfully! You can download it here: {url_download}")
                else:
                    await ctx.send("Failed to retrieve download URL.")
            else:
                await ctx.send(f"Failed to upload file [{response.status_code}]")
            
async def setup(bot: commands.Bot):
    await bot.add_cog(Gokapi(bot))
