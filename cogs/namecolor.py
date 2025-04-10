# cogs/namecolor.py

import discord
from discord.ext import commands
from core.omega import omega

class NameColor(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color_message_list = self.load_color_message_list()
    
    def load_color_message_list(self):
        with open('./data/color_messages.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    def get_color_from_emoji(self, emoji):
        color_map = {
            "🔴": (255, 0, 0),
            "🟠": (255, 165, 0),
            "🟡": (255, 255, 0),
            "🟢": (0, 255, 0),
            "🔵": (0, 0, 255),
            "🟣": (128, 0, 128),
            "⚪": (255, 255, 255),
            "⚫": (0, 0, 0),
        }
        return color_map.get(str(emoji), (255, 255, 255))

    def get_color_name_from_emoji(self, emoji):
        color_map = {
            "🔴": "Red",
            "🟠": "Orange",
            "🟡": "Yellow",
            "🟢": "Green",
            "🔵": "Blue",
            "🟣": "Purple",
            "⚪": "White",
            "⚫": "Black",
        }
        return color_map.get(str(emoji), "Unknown")

    @commands.command(name='namecolorsetup')
    async def namecolorsetup(self, ctx):
        embed = omega.embed.create_embed_info("Name Color Setup", "React to this message to get a color role!")
        message = await ctx.send(embed=embed)
        await message.add_reaction("🔴")
        await message.add_reaction("🟠")
        await message.add_reaction("🟡")
        await message.add_reaction("🟢")
        await message.add_reaction("🔵")
        await message.add_reaction("🟣")
        await message.add_reaction("⚪")
        await message.add_reaction("⚫")
        await message.pin()
        with open('./data/color_message_list.txt', 'a', encoding='utf-8') as f:
            f.write(f"{message.id}\n")
        self.color_message_list.append(message.id)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if reaction.message.id in self.color_message_list:
            guild = reaction.message.guild
            role_name = self.get_color_name_from_emoji(reaction.emoji)
            role = discord.utils.get(guild.roles, name=role_name)
            if not role:
                role = await guild.create_role(name=role_name, color=discord.Color.from_rgb(*self.get_color_from_emoji(reaction.emoji)))

            await user.add_roles(role)


async def setup(bot: commands.Bot):
    await bot.add_cog(NameColor(bot))