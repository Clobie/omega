# cogs/rag_test.py

import discord
from discord.ext import commands
from core.omega import omega

class RagTest(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="testadd")
    async def testadd(self, ctx):
        sample_text = "This is a test entry for the RAG database."
        omega.rag.add_info_to_local_rag(sample_text, metadata={"source": "testadd command"})
        await ctx.send("Added test entry to local RAG.")

    @commands.command(name="testretrieve")
    async def testretrieve(self, ctx, *, query: str = "test entry"):
        results = omega.rag.retrieve_context(query, top_k=4)
        if not results:
            await ctx.send("No documents found.")
            return
        msg = "\n\n".join(results)
        if len(msg) > 1900:
            msg = msg[:1900] + "\n...[truncated]"
        await ctx.send(f"Top results for '{query}':\n{msg}")

async def setup(bot: commands.Bot):
    cog = RagTest(bot)
    await bot.add_cog(cog)
