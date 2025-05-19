# cogs/qr.py

import os
import time
import qrcode
import discord
from discord.ext import commands
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import GappedSquareModuleDrawer
from PIL import Image

class QR(commands.Cog, name="qr"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="qr")
    async def create_stylized_qr(self, context, *msg):
        """
        Generates a stylized QR code with a centered logo
        """
        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=1
        )
        qr.add_data(' '.join(msg))
        qr.make(fit=True)
        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            ill_color="black", 
            back_color="white",
            module_drawer=GappedSquareModuleDrawer()
        ).convert('RGB')
        
        user_id = context.author.id
        logo_path = f'logos/{user_id}_logo.png'
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
        else:
            logo_path = f'logos/default_logo.png'
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)

        if logo:
            logo_size = int(qr_img.size[0] * 0.2)
            logo = logo.resize((logo_size, logo_size), Image.ANTIALIAS)
            logo_position = (
                (qr_img.size[0] - logo_size) // 2,
                (qr_img.size[1] - logo_size) // 2
            )
            qr_img.paste(logo, logo_position, mask=logo)

        unique_filename = f'qr_{int(time.time())}.png'
        qr_img.save(unique_filename)
        await context.send(file=discord.File(unique_filename))
        os.remove(unique_filename)

    @commands.command(name="setlogo")
    async def set_logo(self, context, user: discord.User = None):
        """
        Set your logo for bot functions.
        """
        if not user:
            user = context.author

        attachment = None

        if context.message.attachments:
            attachment = context.message.attachments[0]
        elif context.message.reference:
            ref_message = await context.channel.fetch_message(context.message.reference.message_id)
            if ref_message.attachments:
                attachment = ref_message.attachments[0]

        if attachment and attachment.filename.endswith(('.png', '.jpg', '.jpeg')):
            await attachment.save(f'logos/{user.id}_logo.png')
            await context.send(f"Logo saved for {user.name}.")
        else:
            await context.send("Please upload a valid image file, or ensure the reply has an image.")

async def setup(bot: commands.Bot):
    await bot.add_cog(QR(bot))