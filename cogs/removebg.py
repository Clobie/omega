from discord.ext import commands
from discord import File
from core.omega import omega
from PIL import Image
import io
import re
from datetime import datetime

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

class RemoveBG(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="removebg")
    async def removebg(
        self, ctx, 
        color: str = "#FFFFFF", 
        weight: int = 30
    ):
        """
        Makes the background of an image transparent.
        Usage: !removebg [color] [weight]
        color: hex code or 'r,g,b' (default: white)
        weight: tolerance for color similarity (default: 30)
        Attach an image to your message.
        """
        if not ctx.message.attachments:
            await ctx.send("Please attach an image.")
            return

        attachment = None

        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
        elif ctx.message.reference:
            ref_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if ref_message.attachments:
                attachment = ref_message.attachments[0]
        
        if not attachment or not attachment.filename.endswith(('.png', '.jpg', '.jpeg')):
            await ctx.send("Please attach a valid image file or reply to a valid image file.")
            return
        
        img_bytes = await attachment.read()
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        except Exception:
            await ctx.send("Could not open the image.")
            return

        # Parse color
        if re.match(r"^\d{1,3},\d{1,3},\d{1,3}$", color):
            target_color = tuple(map(int, color.split(',')))
        else:
            try:
                target_color = hex_to_rgb(color)
            except Exception:
                await ctx.send("Invalid color format.")
                return

        datas = img.getdata()
        newData = []
        for item in datas:
            if color_distance(item[:3], target_color) <= weight:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)

        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            user = ctx.author
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{user.id}_{timestamp}_image.png"
            await ctx.send(file=File(fp=image_binary, filename=filename))

async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveBG(bot))