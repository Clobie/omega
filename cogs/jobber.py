# cogs/jobber.py

import discord
from discord.ext import commands, tasks
from core.omega import omega
import os
import sys
import fitz

class Jobber(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.purge_after_days = 30
        self.user_directory = "./downloads/"


    # Example of how to use the AI class and the logger class (Remove this)
    async def get_ai_response(self, model, system_prompt, user_prompt):
        response = omega.ai.chat_completion(model, system_prompt, user_prompt)
        omega.logger.info(f"AI response: {response}")
        return response

    # Example of how to use the database class (Remove this)
    async def insert_data_to_db(self, web_url):
        omega.db.run_script(
            "INSERT INTO job_listings (url) VALUES (?)",
            (web_url,)
        )
        omega.logger.info(f"Inserted URL into database: {web_url}")

    # Create a jobber_tables_init.sql file that can be used to create the necessary tables in the database
    # (separate file, this is just a comment for the task)

    @commands.command(name='addresume')
    async def add_resume(self, ctx, *, url: str):
        if not omega.common.is_valid_url(url):
            await ctx.send("Invalid URL. Please provide a valid URL.")
            return
        
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith('.pdf'):
            await ctx.send("Please provide a PDF file.")
            return
        
        file_path = f"{self.user_directory}{ctx.author.id}/{attachment.filename}"
        if not os.path.exists(f"{self.user_directory}{ctx.author.id}"):
            os.makedirs(f"{self.user_directory}{ctx.author.id}")
        await attachment.save(file_path)

        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        redacted_text = omega.ai.chat_completion(
            model="gpt-4",
            system_prompt="You are a helpful assistant. Redact any sensitive information in the text and format it to be more readable if possible. Do not change any critical information.",
            user_prompt=text
        )

        file_text_path = f"{self.user_directory}{ctx.author.id}/resume.txt"
        with open(f"{file_text_path}", "w") as f:
            f.write(redacted_text)
        omega.logger.info(f"Saved resume for user {ctx.author.id} at {file_text_path}")

        embed = omega.create_embed_info(
            "debug",
            redacted_text
        )

        await ctx.send(embed=embed)

    



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