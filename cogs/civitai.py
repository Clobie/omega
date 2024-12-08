from discord.ext import commands, tasks
import civitai
import time

class CivitAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = "urn:air:flux1:checkpoint:civitai:618692@691639"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.active_jobs = {}  # Dictionary to track jobs
        self.poll_jobs.start()  # Start the background task

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

        # Start the image generation and track the job
        response = civitai.image.create(input_data)
        token = response['token']
        self.active_jobs[reply_msg.id] = {
            "ctx": ctx,
            "token": token,
            "start_time": time.time(),
            "message": reply_msg
        }

    @tasks.loop(seconds=5)
    async def poll_jobs(self):
        completed_jobs = []

        for message_id, job in self.active_jobs.items():
            try:
                job_response = civitai.jobs.get(token=job["token"])
                jobs = job_response.get('jobs', [])
                if jobs and jobs[0]['result']['available']:
                    blob_url = jobs[0]['result']['blobUrl']
                    await job["message"].edit(content=f'{blob_url}', attachments=[])
                    completed_jobs.append(message_id)
                elif time.time() - job["start_time"] > 60:  # Timeout after 60 seconds
                    await job["ctx"].send("Image generation timed out.")
                    await job["message"].edit(content="Image generation timed out.", attachments=[])
                    completed_jobs.append(message_id)
            except Exception as e:
                print(f"Error polling job: {e}")

        # Remove completed jobs
        for message_id in completed_jobs:
            del self.active_jobs[message_id]

    @poll_jobs.before_loop
    async def before_poll_jobs(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.poll_jobs.cancel()

async def setup(bot):
    await bot.add_cog(CivitAI(bot))
