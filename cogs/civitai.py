# cogs/civitai.py

from discord.ext import commands
import civitai
import asyncio
from core.omega import omega

class CivitAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = "urn:air:flux1:checkpoint:civitai:618692@691639"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"

    @commands.command(name='civit')
    async def generate_image(self, ctx, *, prompt: str):
        reply_msg = await ctx.send(self.thinking_emoji)
        input_data = {
            "model": self.model,
            "params": {
                "prompt": prompt,
                "negativePrompt": "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime, mutated hands and fingers:1.4), (deformed, distorted, disfigured:1.3)",
                "scheduler": "EulerA",
                "steps": 20,
                "cfgScale": 7,
                "width": 512,
                "height": 512,
                "clipSkip": 2
            }
        }
        response = civitai.image.create(input_data)
        token = response['token']
        for attempt in range(10):
            job_response = await civitai.jobs.get(token=token)
            if job_response['jobs'][0]['result']['available']:
                blob_url = job_response['jobs'][0]['result']['blobUrl']
                await reply_msg.edit(content=f'{blob_url}', attachments=[])
                return
            await asyncio.sleep(6)
        await ctx.send('Image generation timed out after 10 attempts.')
        await reply_msg.edit(content='Image generation timed out after 10 attempts.', attachments=[])

async def setup(bot):
    await bot.add_cog(CivitAI(bot))