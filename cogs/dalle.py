# cogs/dalle.py

import io
import aiohttp
import discord
from discord.ext import commands
from core.omega import omega

class Dalle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = "dall-e-3"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.base_cost = 0.04
        self.base_profit = 0.01
        self.total_cost = self.base_cost + self.base_profit

    @commands.command(name='generate')
    async def generate_image(self, ctx, *, prompt):
        """
        Generate an image using DALL-E 3.
        """
        if int(omega.credit.get_user_credits(ctx.author.id)) < 5:
            await ctx.send(f"You don't have enough credits for that :(")
            return
        reply_msg = await ctx.send(self.thinking_emoji)
        image_url = omega.ai.generate_image(self.model, prompt)
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    filename = omega.common.generate_random_string() + "_image.png"
                    file = discord.File(io.BytesIO(image_data), filename=filename)
                    omega.ai.update_cost_static(self.total_cost)
                    credits = omega.credit.convert_cost_to_credits(self.total_cost)
                    omega.credit.user_spend(ctx.author.id, credits)
                    omega.ai.log_usage(ctx.author.id, 0, self.total_cost, 'dalle3')
                    credits_remaining = omega.credit.get_user_credits(ctx.author.id)
                    footer = omega.ai.get_footer('null', self.total_cost)
                    footer += omega.common.to_superscript(f"\n{credits_remaining} credits remaining")
                    await reply_msg.edit(content=footer, attachments=[file])
    
    @commands.command(name='edit')
    async def edit_image(self, ctx, *, prompt):
        """
        Edit an image using DALL-E 3.
        Reply to a message with an image attachment with this command, or use the command with an image attachment.
        """
        image_attachment = None
        if ctx.message.reference:
            referenced_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            for attachment in referenced_msg.attachments:
                if attachment.content_type and attachment.filename.endswith(('.png', '.jpg', '.jpeg')):
                    image_attachment = attachment
                    break
        else:
            for attachment in ctx.message.attachments:
                if attachment.content_type and attachment.filename.endswith(('.png', '.jpg', '.jpeg')):
                    image_attachment = attachment
                    break

        if not image_attachment:
            await ctx.send("Please reply to a message with an image or attach an image to edit.")
            return
        
        if int(omega.credit.get_user_credits(ctx.author.id)) < 5:
            await ctx.send("You don't have enough credits for that :(")
            return

        reply_msg = await ctx.send(self.thinking_emoji)

        async with aiohttp.ClientSession() as session:
            async with session.get(image_attachment.url) as resp:
                if resp.status != 200:
                    await reply_msg.edit(content="Failed to download the image.")
                    return
                image_data = await resp.read()

        edited_image_url = omega.ai.edit_image(self.model, prompt, image_data)
        if not edited_image_url:
            await reply_msg.edit(content="Failed to edit the image.")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(edited_image_url) as resp:
                if resp.status != 200:
                    await reply_msg.edit(content="Failed to download the edited image.")
                    return
                edited_image_data = await resp.read()

        filename = omega.common.generate_random_string() + "_edited.png"
        file = discord.File(io.BytesIO(edited_image_data), filename=filename)

        omega.ai.update_cost_static(self.total_cost)
        credits = omega.credit.convert_cost_to_credits(self.total_cost)
        omega.credit.user_spend(ctx.author.id, credits)
        omega.ai.log_usage(ctx.author.id, 0, self.total_cost, 'dalle3_edit')

        credits_remaining = omega.credit.get_user_credits(ctx.author.id)
        footer = omega.ai.get_footer('null', self.total_cost)
        footer += omega.common.to_superscript(f"\n{credits_remaining} credits remaining")

        await reply_msg.edit(content=footer, attachments=[file])


async def setup(bot: commands.Bot):
    await bot.add_cog(Dalle(bot))