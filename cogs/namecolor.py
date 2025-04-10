# cogs/namecolor.py
import discord
from discord.ext import commands
from core.omega import omega

# Consolidated color mapping with both names and RGB values.
COLOR_MAP = {
    "🔴": {"name": "Red", "rgb": (255, 0, 0)},
    "🟠": {"name": "Orange", "rgb": (255, 165, 0)},
    "🟡": {"name": "Yellow", "rgb": (255, 255, 0)},
    "🟢": {"name": "Green", "rgb": (0, 255, 0)},
    "🔵": {"name": "Blue", "rgb": (0, 0, 255)},
    "🟣": {"name": "Purple", "rgb": (128, 0, 128)},
    "⚪": {"name": "White", "rgb": (255, 255, 255)},
    "⚫": {"name": "Black", "rgb": (0, 0, 0)},
    "🟤": {"name": "Brown", "rgb": (139, 69, 19)},
}

class NameColor(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Load stored message IDs as integers for accurate comparisons.
        self.color_message_list = self.load_color_message_list()
    
    def load_color_message_list(self):
        try:
            with open('./data/color_role_messages.txt', 'r', encoding='utf-8') as f:
                return [int(line.strip()) for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def get_color_data(self, emoji):
        # Return the color data (name and rgb) for the provided emoji.
        return COLOR_MAP.get(str(emoji))

    @commands.command(name='namecolorsetup')
    async def namecolorsetup(self, ctx):
        # Delete the original command message.
        await ctx.message.delete()
        embed = omega.embed.create_embed_info(
            "Set your name color!", 
            "React to this message to get a color role!"
        )
        message = await ctx.send(embed=embed)
        
        # Add each reaction from our color map.
        for emoji in COLOR_MAP.keys():
            await message.add_reaction(emoji)
        await message.pin()
        
        # Store the message ID in the file and our local list.
        with open('./data/color_role_messages.txt', 'a', encoding='utf-8') as f:
            f.write(f"{message.id}\n")
        self.color_message_list.append(message.id)

        guild = ctx.guild
        total_roles = len(guild.roles)
        # Create color roles if they do not already exist.
        # Roles are named with a "cr_" prefix, e.g., "cr_Red".
        for emoji, data in COLOR_MAP.items():
            role_name = f"cr_{data['name']}"
            role = discord.utils.get(guild.roles, name=role_name)
            if not role:
                # Create the role with the specified color.
                role = await guild.create_role(
                    name=role_name,
                    color=discord.Color.from_rgb(*data['rgb'])
                )
                # Adjust the role's position.
                await role.edit(position=total_roles - 3)
                total_roles += 1

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignore bot reactions.
        if user.bot:
            return

        # Process only if the message is a valid color setup message.
        if reaction.message.id not in self.color_message_list:
            return

        guild = reaction.message.guild

        # Remove any existing color roles from the user.
        color_roles = [role for role in guild.roles if role.name.startswith('cr_')]
        await user.remove_roles(*color_roles)

        # Retrieve color data using the emoji and assign the role.
        color_data = self.get_color_data(reaction.emoji)
        if color_data:
            role = discord.utils.get(guild.roles, name=f"cr_{color_data['name']}")
            if role:
                await user.add_roles(role)
        # Remove the reaction so the user can reuse it if needed.
        await reaction.message.remove_reaction(reaction.emoji, user)

async def setup(bot: commands.Bot):
    await bot.add_cog(NameColor(bot))
