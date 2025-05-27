# cogs/dalle.py

import io
import aiohttp
import discord
from discord.ext import commands
from core.omega import omega
import os

class Dalle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = "dall-e-3"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.dalle3_cost = 0.04
        self.gpt_image_1_cost = 0.25
        self.base_profit = 1
        self.percent_profit = 0.1

    @commands.command(name='getcredits')
    async def get_credits(self, ctx):
        # Let the user know that they can either ask clobie nicely (yay!) or buy credits at https://ko-fi.com/clobie
        await ctx.send(
            (
                f"Hey {ctx.author.mention}! You can get credits by:\n"
                f"1. Asking Clobie nicely (yay!)\n"
                f"2. Buying credits at https://ko-fi.com/s/fbec71b619\n"
                f"3. Earning credits by being active in the server!\n"
            )
        )

    @commands.command(name='generate')
    async def generate_image(self, ctx, *, prompt):
        """
        Generate an image using DALL-E 3.
        """
        if int(omega.credit.get_user_credits(ctx.author.id)) < 5:
            await ctx.send(
                (
                    f"You don't have enough credits for that :(\n"
                    f"Use `!credits` to check your balance, or `!getcredits` to see how to get more credits!\n"
                )
            )
            return
        reply_msg = await ctx.send(self.thinking_emoji)
        image_url = omega.ai.generate_image(self.model, prompt)
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    filename = omega.common.generate_random_string() + "_image.png"
                    file = discord.File(io.BytesIO(image_data), filename=filename)
                    cost = (self.dalle3_cost + self.base_profit) * (1 + self.percent_profit)
                    omega.ai.update_cost_static(cost)
                    credits = omega.credit.convert_cost_to_credits(cost)
                    omega.credit.user_spend(ctx.author.id, credits)
                    omega.ai.log_usage(ctx.author.id, 0, cost, 'dalle3')
                    credits_remaining = omega.credit.get_user_credits(ctx.author.id)
                    footer = omega.ai.get_footer('null', cost)
                    footer += omega.common.to_superscript(f"\n{credits_remaining} credits remaining")
                    await reply_msg.edit(content=footer, attachments=[file])
    
    @commands.command(name='edit')
    async def edit_image(self, ctx, *, prompt):
        """
        Edit an image using DALL-E 3.
        Reply to a message with an image attachment with this command, or use the command with an image attachment.
        """
        if int(omega.credit.get_user_credits(ctx.author.id)) < 30:
            await ctx.send(
                (
                    f"You don't have enough credits for that :(\n"
                    f"Use `!credits` to check your balance, or `!getcredits` to see how to get more credits!\n"
                )
            )
            return
        
        user = ctx.author

        attachment = None

        reply_msg = await ctx.send(self.thinking_emoji)

        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
        elif ctx.message.reference:
            ref_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if ref_message.attachments:
                attachment = ref_message.attachments[0]

        if not attachment:
            await reply_msg.edit(content="No image attachment found. Please attach an image or reply to a message with an image.")
            return

        file_path = f'download/{str(user.id)}/{attachment.filename}'
        if not os.path.exists(f'download/{str(user.id)}'):
            os.makedirs(f'download/{str(user.id)}')

        if attachment and attachment.filename.endswith(('.png', '.jpg', '.jpeg')):
            await attachment.save(file_path)

        edited_image_path = await omega.ai.edit_image(str(user.id), prompt, file_path)
        if not edited_image_path:
            await reply_msg.edit(content="Failed to edit the image.")
            return

        cost = round((self.gpt_image_1_cost + self.base_profit) * (1 + self.percent_profit), 0)
        omega.ai.update_cost_static(cost)
        credits = omega.credit.convert_cost_to_credits(cost)
        omega.credit.user_spend(ctx.author.id, credits)
        omega.ai.log_usage(ctx.author.id, 0, cost, 'gpt-image-1')

        credits_remaining = omega.credit.get_user_credits(ctx.author.id)
        #footer = omega.ai.get_footer('null', cost)
        footer = omega.common.to_superscript(f"{credits_remaining} credits remaining")

        await reply_msg.edit(content=footer, attachments=[discord.File(edited_image_path)])


async def setup(bot: commands.Bot):
    await bot.add_cog(Dalle(bot))