# cogs/jobber.py

import discord
from discord.ext import commands, tasks
from core.omega import omega
import os
import sys
import re
import aiohttp
from bs4 import BeautifulSoup
import requests

class Jobber(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.purge_after_days = 30
        self.user_directory = "./downloads/"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"


    # Create a jobber_tables_init.sql file that can be used to create the necessary tables in the database
    # (separate file, this is just a comment for the task)

    @commands.command(name='addresume')
    async def add_resume(self, ctx, *, data=None):
        reply_msg = await ctx.send(f"{self.thinking_emoji}")
        if ctx.message.attachments:
            if not ctx.message.attachments[0].filename.endswith('.txt'):
                await reply_msg.edit("Please upload a .txt file or paste the text of your resume directly.")
                return
            if not os.path.exists(f"{self.user_directory}{ctx.author.id}"):
                os.makedirs(f"{self.user_directory}{ctx.author.id}")
            await ctx.message.attachments[0].save(f"{self.user_directory}{ctx.author.id}/resume.txt")
            data = open(f"{self.user_directory}{ctx.author.id}/resume.txt", "r").read()
        elif data is None:
            await reply_msg.edit("Please upload a .txt file or paste the text of your resume directly.")
            return
        redacted_text = omega.ai.chat_completion(
            model="gpt-4",
            system_prompt="You are a helpful assistant. Redact any sensitive information in the text.",
            user_prompt=data
        )
        redacted_text = re.sub(r'\r\n|\n+', '\n', redacted_text.strip())
        file_text_path = f"{self.user_directory}{ctx.author.id}/resume.txt"
        with open(f"{file_text_path}", "w") as f:
            f.write(redacted_text)
        omega.logger.info(f"Saved resume for user {ctx.author.id} at {file_text_path}")
        await reply_msg.edit(f"Resume saved for user {ctx.author.id} at {file_text_path}")
    
    @commands.command(name='resume')
    async def get_resume(self, ctx):
        reply_msg = await ctx.send(f"{self.thinking_emoji}")
        if not os.path.exists(f"{self.user_directory}{ctx.author.id}/resume.txt"):
            await reply_msg.edit("You don't have a resume saved. Please upload one using the `addresume` command.")
            return
        with open(f"{self.user_directory}{ctx.author.id}/resume.txt", "r") as f:
            data = f.read()
        await reply_msg.edit(f"Your resume:\n\n{data}")
    
    @commands.command(name='addjob')
    async def add_job(self, ctx, *, url=None):
        reply_msg = await ctx.send(f"{self.thinking_emoji}")
        if url is None:
            await reply_msg.edit("Please provide a URL to a job listing.")
            return
        if not omega.common.is_valid_url(url):
            await reply_msg.edit("Please provide a valid URL.")
            return
        response = requests.get(url)
        if response.status_code != 200:
            await reply_msg.edit("Failed to fetch the job listing. Please check the URL.")
            return
        soup = BeautifulSoup(response.text, 'html.parser')

        body = soup.find('body')

        #embed = omega.embed.create_embed_info(
        #    "debug",
        #    body
        #)

        #sanitize url
        sanitized_url = re.sub(r'[^a-zA-Z0-9/:._-]', '', url)

        file_path = f"{self.user_directory}{ctx.author.id}/{sanitized_url}.html"

        with open(file_path, "w") as f:
            f.write(str(body))
        omega.logger.info(f"Saved job listing for user {ctx.author.id} at {file_path}")

        await reply_msg.edit(f"Job listing fetched successfully.")


    # Task loop to do the following once per hour:
    # 1. Parse a website URL for any potential job listings
    # 2. Use AI to parse the job listing and extract the complete job summary, URL, job title, requirements, etc. Then save it to the database
    # Make sure to think about speed and efficiency, and make sure to not spam the website with requests
    # Make sure to consider speed for the db, use multiple tables if necessary

    # Task loop to do the following once per day:
    # 1. Check if any job listings have been updated in the last self.purge_after_days
    # 2. Purge any job listings that are older than self.purge_after_days and have not been updated in the last self.purge_after_days

    # Task loop to match job listings with users based on resume and job title
    # 1. DB query a list of all job listing titles
    # 2. DB query a list of all user resumes
    # 3. Use AI to match the job listing titles with the user resumes
    # 4. Set the job as processed in the database, only for that specific user
    # 5. Send a DM to the user with the job listing title and a link to the job listing
    # 6. Use AI to generate a cover letter for the user based on the job listing title and the resume
    # 7. Save the cover letter in the database and send it to the user as a DM
    # 8. Use AI to generate a resume for the user based on the job listing title and the resume.  Try to change as little as possible, but make it more appealing to the job listing

    # Command to do the following:
    # 1. Take in a URL parameter and check if it's a valid URL
    # 2. Use AI to parse the URL and extract the complete job summary, URL, job title, requirements, etc.
    # 3. If the URL is a valid job listing, create a custom cover letter for the user based on the job listing title and the resume
    # 4. Reply to the user with the cover letter

    # Command to manually add a job listing to the database (URL)
    # 1. Verify that the URL is a valid job listing
    # Follow the same steps as the task loop that scrapes the website for job listings

    # 




async def setup(bot: commands.Bot):
    cog = Jobber(bot)
    await bot.add_cog(cog)