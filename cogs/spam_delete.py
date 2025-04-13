# cogs/spam_delete.py

from discord.ext import commands
from core.omega import omega

class SpamDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        with open('./data/spam_phrases.txt', 'r') as f:
            spam_phrases = f.read().splitlines()
        for phrase in spam_phrases:
            if phrase.lower() in message.content.lower():
                await message.delete()
                break
    
    @commands.command(name='addspam')
    @commands.has_permissions(manage_messages=True)
    async def spamphrase(self, ctx, *, phrase):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You do not have the required permissions for that command.")
            return
        with open('./data/spam_phrases.txt', 'a') as f:
            f.write(phrase + '\n')
        await ctx.send(f"Added '{phrase}' to the spam phrases list.")
    
    @commands.command(name='removespam')
    @commands.has_permissions(manage_messages=True)
    async def removespam(self, ctx, *, phrase):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You do not have the required permissions for that command.")
            return
        with open('./data/spam_phrases.txt', 'r') as f:
            lines = f.readlines()
        with open('./data/spam_phrases.txt', 'w') as f:
            for line in lines:
                if line.strip() != phrase:
                    f.write(line)
        await ctx.send(f"Removed '{phrase}' from the spam phrases list.")
    
async def setup(bot):
    await bot.add_cog(SpamDelete(bot))