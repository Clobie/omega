# cogs/zapier.py

import discord
from discord.ext import commands
import re
from core.omega import omega

class Zapier(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.zapier_user_id = 1256849004566675538

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.zapier_user_id:
            def dummy_function(amount_cents, user_id):
                print(f"Amount (cents): {amount_cents}, User ID: {user_id}")

            content = message.content

            amount_match = re.search(r'Amount:\s*([\d.]+)', content)
            if amount_match:
                amount_dollars = float(amount_match.group(1))
                amount_cents = int(amount_dollars * 100)
            else:
                amount_cents = None

            user_id_match = re.search(r'\b(\d{5,})\b', content)
            user_id = int(user_id_match.group(1)) if user_id_match else None

            if amount_cents is not None and user_id is not None:
                dummy_function(amount_cents, user_id)
            
            await message.channel.send(f"{amount_cents} cents and user ID {user_id} parsed from message.")
            if amount_cents is not None and user_id is not None:
                omega.credit.gift_user_credits(user_id, amount_cents)
            
            user = await self.bot.fetch_user(user_id)
            if user:
                embed = discord.Embed(
                    title="Omega Notification",
                    description=f"You have received {amount_cents} credits.",
                    color=omega.cfg.PRIMARYCOLOR
                )
                await user.send(embed=embed)
            else:
                await message.channel.send(f"User with ID {user_id} not found.")

async def setup(bot: commands.Bot):
    cog = Zapier(bot)
    await bot.add_cog(cog)