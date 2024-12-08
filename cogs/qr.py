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
        Generates a stylized QR code
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
        unique_filename = f'qr_{int(time.time())}.png'
        qr_img.save(unique_filename)
        await context.send(file=discord.File(unique_filename))
        os.remove(unique_filename)

async def setup(bot: commands.Bot):
    await bot.add_cog(QR(bot))