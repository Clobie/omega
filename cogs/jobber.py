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
from datetime import datetime

class Jobber(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.purge_after_days = 30
        self.user_directory = "./downloads"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.update_channel_id = 1376922139239645204

        if not os.path.exists(self.user_directory):
            os.makedirs(self.user_directory)
        if not os.path.exists(f"{self.user_directory}/jobs"):
            os.makedirs(f"{self.user_directory}/jobs")
        self.db_init()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.ratracerebellion_scraper_loop.is_running():
            self.ratracerebellion_scraper_loop.start()

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

            CREATE TABLE job_notifications (
                user_id VARCHAR(255) PRIMARY KEY,
                notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    def is_job_similar(self, job, keywords):
        title = job.get("title", "").lower()
        company = job.get("company", "").lower()
        for keyword in keywords:
            if keyword.lower() in title or keyword.lower() in company:
                return True
        return False

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

        proccessing_msg = await ctx.send(self.thinking_emoji + " Processing your resume...")

        keywords = omega.ai.chat_completion(
            model="gpt-4",
            system_prompt="You are a helpful assistant. Using the provided resume text, generate a list of potential job titles that can be used for job matching.  Be as thorough as possible.  Do not use a numbered list.  ONLY job titles separated by new lines.",
            user_prompt=redacted_text
        )

        keywords = re.sub(r'\r\n|\n+', '\n', keywords.strip())
        keywords = [
            re.sub(r'^[\s]*[0-9]+[.)][\s]*', '', line).strip()
            for line in keywords.split('\n') if line.strip()
        ]

        if not keywords:
            await proccessing_msg.edit(content="Issue :(")
            return
        
        keywords_text_path = f"{self.user_directory}/{ctx.author.id}/keywords.txt"
        with open(keywords_text_path, "w") as f:
            f.write(keywords)

        omega.logger.info(f"Saved keywords for user {ctx.author.id} at {keywords_text_path}")
        await proccessing_msg.edit(content=f"Resume processed for {ctx.author.id}.\n")
    

    @commands.command(name='notifyme', aliases=['notifyjobs'])
    async def notify_me(self, ctx):
        if not os.path.exists(f"{self.user_directory}/{ctx.author.id}/resume.txt"):
            await ctx.send("You don't have a resume saved. Please upload one using the `addresume` command first.")
            return
        if not os.path.exists(f"{self.user_directory}/{ctx.author.id}/keywords.txt"):
            await ctx.send("You don't have keywords saved. Please run the `addresume` command to generate keywords, or add them manually with the `addkw` and `removekw` commands.")
            return
        query = "SELECT * FROM job_notifications WHERE user_id = %s;"
        existing = omega.db.run_script(query, (str(ctx.author.id),))
        if existing:
            query = "DELETE FROM job_notifications WHERE user_id = %s;"
            omega.db.run_script(query, (str(ctx.author.id),))
            omega.logger.info(f"User {ctx.author.id} has been removed from the job notification list.")
            await ctx.send("You have been removed from the job notification list. You will no longer receive notifications when new jobs are posted that match your resume keywords.")
            return
        else:
            query = "INSERT INTO job_notifications (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING;"
            omega.db.run_script(query, (str(ctx.author.id),))
            omega.logger.info(f"User {ctx.author.id} has been added to the job notification list.")
            await ctx.send(f"You have been added to the job notification list. You will receive notifications when new jobs are posted that match your resume keywords.")




    @commands.command(name='jobmatch', aliases=['matchjobs'])
    async def job_match(self, ctx):
        reply_msg = await ctx.send(self.thinking_emoji)

        user_id = str(ctx.author.id)
        resume_path = f"{self.user_directory}/{user_id}/resume.txt"
        keywords_path = f"{self.user_directory}/{user_id}/keywords.txt"

        if not os.path.exists(resume_path):
            await reply_msg.edit(content="You don't have a resume saved. Please upload one using the `addresume` command.")
            return
        if not os.path.exists(keywords_path):
            await reply_msg.edit(content="You don't have keywords saved. Please run the `addresume` command to generate keywords.")
            return

        with open(resume_path, "r") as f:
            resume_text = f.read().strip()
        with open(keywords_path, "r") as f:
            keywords = [line.strip() for line in f if line.strip()]

        if not resume_text or not keywords:
            await reply_msg.edit(content="Your resume or keywords are empty. Please ensure you have uploaded a resume and generated keywords.")
            return

        query = "SELECT * FROM job_listings WHERE title ILIKE %s;"
        seen = set()
        results = []

        for keyword in keywords:
            search_term = f"%{keyword}%"
            jobs = omega.db.run_script(query, (search_term,))
            for job in jobs:
                if job[0] not in seen:
                    seen.add(job[0])
                    results.append(job)

        if not results:
            await reply_msg.edit(content="No job listings found matching your resume keywords.")
            return

        embeds = []
        body = ""
        for job in results:
            title = job[2]
            company = job[1]
            link = job[3]
            pay = job[4]
            created_at = job[6]

            try:
                days_ago = (datetime.now() - created_at).days
            except Exception:
                days_ago = "?"
            days_ago_string = omega.common.to_superscript(f"added {days_ago} days ago")

            entry = f"**{title}** at {company} - Pay: {pay} - {days_ago_string}\n<{link}>\n\n"

            if len(body) + len(entry) > 4000:
                embed = omega.embed.create_embed_info("Job Matches", body)
                embeds.append(embed)
                body = ""

            body += entry

        if body:
            embed = omega.embed.create_embed_info("Job Matches", body)
            embeds.append(embed)

        await reply_msg.delete()
        for embed in embeds:
            await ctx.send(embed=embed)






    @commands.command(name='resume')
    async def get_resume(self, ctx):
        reply_msg = await ctx.send(f"{self.thinking_emoji}")
        if not os.path.exists(f"{self.user_directory}/{ctx.author.id}/resume.txt"):
            await reply_msg.edit(content="You don't have a resume saved. Please upload one using the `addresume` command.")
            return
        with open(f"{self.user_directory}/{ctx.author.id}/resume.txt", "r") as f:
            data = f.read()
        await reply_msg.edit(content=f"Your resume:\n\n{data}")

    @commands.command(name='findjobs', aliases=['searchjobs', 'jobsearch'])
    async def find_jobs(self, ctx, *, search):
        query = (
            "SELECT * FROM job_listings WHERE title ILIKE %s OR company ILIKE %s OR snapshot ILIKE %s;"
        )
        search_term = f"%{search}%"
        results = omega.db.run_script(query, (search_term, search_term, search_term,))
        if not results:
            await ctx.send("No job listings found matching your search.")
            return
        body = ""
        embeds = []
        for job in results:
            created_at = job[6]
            days_ago = (datetime.now() - created_at).days
            days_ago_string = omega.common.to_superscript(f"added {days_ago} days ago")
            entry = (
                f"**{job[2]}** at {job[1]} - Pay: {job[4]} - {days_ago_string}\n"
                f"<{job[3]}>\n\n"
            )
            if len(body) + len(entry) > 4000:
                embed = omega.embed.create_embed_info("Job Listings", body)
                embeds.append(embed)
                body = ""
            body += entry
        if body:
            embed = omega.embed.create_embed_info("Job Listings", body)
            embeds.append(embed)
        for embed in embeds:
            await ctx.send(embed=embed)

    @tasks.loop(hours=1)
    async def ratracerebellion_scraper_loop(self):
        current_hour = discord.utils.utcnow().hour
        if current_hour >= 22 or current_hour < 6:
            omega.logger.info("Skipping ratracerebellion scraper loop due to time restriction.")
            return
        def extract_jobs_from_html(html):
            soup = BeautifulSoup(html, "html.parser")
            job_entries = []
            p_tags = soup.find_all("p")
            for i, p in enumerate(p_tags):
                text = p.get_text(strip=True)
                if "Company" in text and "Job/Gig" in text:
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
        url = "https://ratracerebellion.com/job-postings/"
        channel = self.bot.get_channel(self.update_channel_id)
        if not channel:
            omega.logger.warning(f"Channel with ID {self.update_channel_id} not found.")
            return
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            await channel.send(f"Failed to fetch job board: {e}\n\nURL: {url}")
            return
        html = response.text
        job_entries = extract_jobs_from_html(html)
        if not job_entries:
            await channel.send(f"No job entries found.")
            return
        total_jobs = len(job_entries)
        omega.logger.info(f"Found {total_jobs} job entries.")
        new_jobs = []
        jobs_added = 0
        for job in job_entries:
            if self.add_job_to_db(job):
                jobs_added += 1
                new_jobs.append(job)
        if jobs_added > 0:
            await channel.send(
                f"Added {jobs_added} new job entries to the database out of {total_jobs} found."
            )
            job_summaries = ""
            for job in new_jobs:
                entry = f"**{job['title']}** at {job['company']} - Pay: {job['pay']}\n"
                if (len(job_summaries) + len(entry)) > 2000:
                    await channel.send(entry)
                    job_summaries = ""
                else:
                    job_summaries += entry
            if job_summaries:
                await channel.send(job_summaries)
            


        query = "SELECT user_id FROM job_notifications;"
        rows = omega.db.run_script(query)

        if rows:
            for row in rows:
                user_id = int(row[0])
                keywords_file = f"./downloads/{user_id}/keywords.txt"
                
                if not os.path.isfile(keywords_file):
                    omega.logger.warning(f"Keywords file not found for user {user_id}")
                    continue
                
                with open(keywords_file, "r", encoding="utf-8") as f:
                    keywords = [line.strip() for line in f if line.strip()]
                
                matches = [job for job in new_jobs if self.is_job_similar(job, keywords)]
                
                if matches:
                    user_obj = self.bot.get_user(user_id)
                    if user_obj:
                        try:
                            await user_obj.send(
                                "New job listings have been added that match your resume keywords. Check the job board for details."
                            )
                        except discord.Forbidden:
                            omega.logger.warning(f"Could not send DM to user {user_id}. They may have DMs disabled.")

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
