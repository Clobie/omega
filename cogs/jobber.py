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
        self.user_directory = "./downloads"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        if not os.path.exists(self.user_directory):
            os.makedirs(self.user_directory)
        if not os.path.exists(f"{self.user_directory}/jobs"):
            os.makedirs(f"{self.user_directory}/jobs")
        self.db_init()

    def db_init(self):
        check_query = "SELECT * FROM information_schema.tables WHERE table_name = 'job_listings';"
        existing = omega.db.run_script(check_query)
        if not existing:
            create_query = """
            CREATE TABLE job_listings (
                id SERIAL PRIMARY KEY,
                company VARCHAR(255),
                title VARCHAR(255),
                link VARCHAR(255),
                pay VARCHAR(255),
                snapshot TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            omega.db.run_script(create_query)
            omega.logger.info("Created job_listings table in the database.")

    def add_job_to_db(self, job):
        check_query = "SELECT id FROM job_listings WHERE link = %s;"

        existing = omega.db.run_script(check_query, (job["link"],))

        if existing:
            omega.logger.info(f"Job with link {job['link']} already exists in the database.")
            return False

        insert_query = (
            "INSERT INTO job_listings (company, title, link, pay, snapshot) "
            "VALUES (%s, %s, %s, %s, %s);"
        )
        omega.db.run_script(insert_query, (job["company"], job["title"], job["link"], job["pay"], job["snapshot"],))
        omega.logger.info(f"Inserted job with link {job['link']} into the database.")
        return True

    def extract_jobs_from_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        job_entries = []
        p_tags = soup.find_all("p")
        for i, p in enumerate(p_tags):
            text = p.get_text(strip=True)
            if "Company" in text and "Job/Gig" in text:
                # Initialize fields
                company = None
                title = None
                link = None
                pay = None
                snapshot = None
                if "Company" in text:
                    company_line = next((line for line in text.splitlines() if "Company" in line), "")
                    company = company_line.split(":", 1)[-1].split("Job/Gig")[0].strip()
                a_tag = p.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    link = a_tag.get("href", None)
                if "Pay" in text:
                    pay_line = next((line for line in text.splitlines() if "Pay" in line), "")
                    pay = pay_line.split("Pay:", 1)[-1].strip()
                if i + 1 < len(p_tags):
                    snapshot_text = p_tags[i + 1].get_text(strip=True)
                    if "Snapshot" in snapshot_text or not snapshot_text.startswith("Company:"):
                        snapshot = snapshot_text
                job_entries.append({
                    "company": company,
                    "title": title,
                    "link": link,
                    "pay": pay,
                    "snapshot": snapshot
                })
        return job_entries

    @commands.command(name='addresume')
    async def add_resume(self, ctx, *, data=None):
        reply_msg = await ctx.send(f"{self.thinking_emoji}")
        if ctx.message.attachments:
            if not ctx.message.attachments[0].filename.endswith('.txt'):
                await reply_msg.edit(content="Please upload a .txt file or paste the text of your resume directly.")
                return
            if not os.path.exists(f"{self.user_directory}/{ctx.author.id}"):
                os.makedirs(f"{self.user_directory}/{ctx.author.id}")
            await ctx.message.attachments[0].save(f"{self.user_directory}/{ctx.author.id}/resume.txt")
            data = open(f"{self.user_directory}/{ctx.author.id}/resume.txt", "r").read()
        elif data is None:
            await reply_msg.edit(content="Please upload a .txt file or paste the text of your resume directly.")
            return
        redacted_text = omega.ai.chat_completion(
            model="gpt-4",
            system_prompt="You are a helpful assistant. Redact any sensitive information in the text.",
            user_prompt=data
        )
        redacted_text = re.sub(r'\r\n|\n+', '\n', redacted_text.strip())
        file_text_path = f"{self.user_directory}/{ctx.author.id}/resume.txt"
        with open(f"{file_text_path}", "w") as f:
            f.write(redacted_text)
        omega.logger.info(f"Saved resume for user {ctx.author.id} at {file_text_path}")
        await reply_msg.edit(content=f"Resume saved for user {ctx.author.id} at {file_text_path}")
    
    @commands.command(name='resume')
    async def get_resume(self, ctx):
        reply_msg = await ctx.send(f"{self.thinking_emoji}")
        if not os.path.exists(f"{self.user_directory}/{ctx.author.id}/resume.txt"):
            await reply_msg.edit(content="You don't have a resume saved. Please upload one using the `addresume` command.")
            return
        with open(f"{self.user_directory}/{ctx.author.id}/resume.txt", "r") as f:
            data = f.read()
        await reply_msg.edit(content=f"Your resume:\n\n{data}")
    

    @commands.command(name='addjob')
    async def add_job(self, ctx):
        url = f"https://ratracerebellion.com/job-postings/"
        reply_msg = await ctx.send(self.thinking_emoji)
        if not url:
            await reply_msg.edit(content="Please provide a URL to a job listing.")
            return
        if not omega.common.is_valid_url(url):
            await reply_msg.edit(content="Please provide a valid URL.")
            return
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            await reply_msg.edit(content=f"Failed to fetch the job listing: {e}")
            return
        html = response.text
        job_entries = self.extract_jobs_from_html(html)
        if not job_entries:
            await reply_msg.edit(content="No job entries found.")
            return
        total_jobs = len(job_entries)
        omega.logger.info(f"Found {total_jobs} job entries.")

        
        jobs_added = 0
        for job in job_entries:
            if self.add_job_to_db(job):
                jobs_added += 1
        if jobs_added > 0:
            await reply_msg.edit(content=f"Added {jobs_added} new job entries to the database out of {total_jobs}.")
        else:
            await reply_msg.edit(content=f"No new job entries were added to the database out of {total_jobs}.")
        #    company = job.get("company")
        #    title = job.get("title")
        #    link = job.get("link")
        #    pay = job.get("pay")
        #    snapshot = job.get("snapshot")

        # Save the job entry to the database
        # Turn this into a task loop

async def setup(bot: commands.Bot):
    cog = Jobber(bot)
    await bot.add_cog(cog)












    # Create a jobber_tables_init.sql file that can be used to create the necessary tables in the database
    # (separate file, this is just a comment for the task)

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
