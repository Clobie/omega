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
        
    @commands.command()
    async def save(self, ctx):
        """
        Saves the attachment of the replied-to message to Gokapi.
        """
        if not ctx.message.reference:
            await ctx.send("Please reply to a message containing an attachment.")
            return

        ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        if not ref_msg.attachments:
            await ctx.send("The referenced message has no attachments.")
            return

        attachment = ref_msg.attachments[0]
        file_name = attachment.filename

        try:
            response = await attachment.read()
            
            files = {
                "file": (file_name, response, "application/octet-stream"),
            }
            data = {
                "allowedDownloads": 0,
                "expiryDays": 0,
                "password": "",
            }
            headers = {
                "accept": "application/json",
                "apikey": omega.cfg.GOKAPI_API_KEY,
            }
            
            gokapi_response = requests.post(
                self.file_save_api_url, 
                headers=headers, 
                files=files, 
                data=data
            )
            
            if gokapi_response.status_code == 200:
                result = gokapi_response.json()
                download_url = result["FileInfo"]["UrlDownload"]
                await ctx.send(f"{download_url}")
            else:
                await ctx.send(f"Failed to upload the file. Error: {gokapi_response.text}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            
async def setup(bot: commands.Bot):
    await bot.add_cog(Gokapi(bot))
