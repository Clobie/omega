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
            # Call the blocking function and debug its return
            try:
                job_response = civitai.jobs.get(token=token)
                print(f"Debug: job_response type: {type(job_response)}, content: {job_response}")

                # Access the data correctly (modify this as needed based on debug output)
                jobs = job_response.get('jobs', [])
                if jobs and jobs[0]['result']['available']:
                    blob_url = jobs[0]['result']['blobUrl']
                    await reply_msg.edit(content=f'{blob_url}', attachments=[])
                    return
            except Exception as e:
                print(f"Error fetching job response: {e}")
            
            await asyncio.sleep(6)

        await ctx.send('Image generation timed out after 10 attempts.')
        await reply_msg.edit(content='Image generation timed out after 10 attempts.', attachments=[])

async def setup(bot):
    await bot.add_cog(CivitAI(bot))
