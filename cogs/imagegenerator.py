import discord
import os
from discord.ext import commands
from utils.config import cfg
from utils.log import logger
from utils.status import status
from utils.common import common
from utils.imagegenerator import imgen

class ImageGenerator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="postgenerator")
    async def postgenerator(self, context, *, msg):
        """
        Generates one of those fancy 'text over gradient' images for social media posts.
        """
        logger.info(f"User {context.author} requested image generation.")
        img = imgen.generate_facebook_text_post(msg)
        try:
            await context.send(file=discord.File(img, filename="post_image.png"))
            logger.info(f"Image sent to {context.author}.")
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            await context.send("Sorry, there was an error generating the image.")
        finally:
            if os.path.exists(img):
                os.remove(img)  # remove image from file system
                logger.info(f"Removed temporary image file: {img}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ImageGenerator(bot))