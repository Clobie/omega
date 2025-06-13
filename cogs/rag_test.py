# cogs/rag_test.py

import discord
from discord.ext import commands
from core.omega import omega

class RagTest(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="testadd")
    async def testadd(self, ctx,  *, data: str):
        omega.rag.add_info_to_local_rag(data, metadata={"source": "testadd command"})
        await ctx.send("Added test entry to local RAG.")

    @commands.command(name="testretrieve")
    async def testretrieve(self, ctx, *, query: str):
        results = omega.rag.retrieve_context(query, top_k=4)
        if not results:
            await ctx.send("No documents found.")
            return

        # Convert all entries to strings (even if they are already strings, this is safe)
        texts = [str(entry) for entry in results]

        msg = "\n\n".join(texts)
        if len(msg) > 1900:
            msg = msg[:1900] + "\n...[truncated]"
        await ctx.send(f"Top results for '{query}':\n{msg}")
    
    @commands.command(name="nukedb")
    async def nukedb(self, ctx):
        pass



async def setup(bot: commands.Bot):
    cog = RagTest(bot)
    await bot.add_cog(cog)
