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
        self.color_message_list = self.load_color_message_list()
        omega.logger.info(f"NameColor Cog initialized with {len(self.color_message_list)} stored message IDs.")

    def load_color_message_list(self):
        try:
            with open('./data/color_role_messages.txt', 'r', encoding='utf-8') as f:
                message_ids = [int(line.strip()) for line in f if line.strip()]
                omega.logger.info(f"Loaded color message IDs: {message_ids}")
                return message_ids
        except FileNotFoundError:
            omega.logger.info("color_role_messages.txt not found. Starting with empty message list.")
            return []

    def get_color_data(self, emoji):
        return COLOR_MAP.get(str(emoji))

    @commands.command(name='namecolorsetup')
    async def namecolorsetup(self, ctx):
        await ctx.message.delete()
        omega.logger.info(f"'namecolorsetup' command invoked by {ctx.author}.")
        
        embed = omega.embed.create_embed_info(
            "Set your name color!", 
            "React to this message to get a color role!"
        )
        message = await ctx.send(embed=embed)
        
        
        for emoji in COLOR_MAP.keys():
            await message.add_reaction(emoji)
            omega.logger.info(f"Added reaction {emoji} to setup message (ID: {message.id}).")
        await message.pin()
        omega.logger.info(f"Pinned setup message with ID: {message.id}.")
        
        
        with open('./data/color_role_messages.txt', 'a', encoding='utf-8') as f:
            f.write(f"{message.id}\n")
        self.color_message_list.append(message.id)
        omega.logger.info(f"Stored message ID {message.id} for future reaction processing.")

        guild = ctx.guild
        
        
        for emoji, data in COLOR_MAP.items():
            role_name = f"cr_{data['name']}"
            role = discord.utils.get(guild.roles, name=role_name)
            if not role:
                role = await guild.create_role(
                    name=role_name,
                    color=discord.Color.from_rgb(*data['rgb'])
                )
                omega.logger.info(f"Created role {role_name} with color {data['rgb']}.")
        
        # Reorder the color roles to be just below the bot's top role.
        # IMPORTANT: The bot's role must be higher in the role hierarchy than the color roles.
        bot_top_role = ctx.me.top_role
        color_roles = []
        
        for data in COLOR_MAP.values():
            role = discord.utils.get(guild.roles, name=f"cr_{data['name']}")
            if role:
                color_roles.append(role)
        
        new_positions = {}
        new_position = bot_top_role.position - 1
        for role in sorted(color_roles, key=lambda r: r.name):
            new_positions[role] = new_position
            omega.logger.info(f"Setting role {role.name} position to {new_position}.")
            new_position -= 1

        await guild.edit_role_positions(positions=new_positions)
        omega.logger.info("Successfully updated color role positions.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if str(reaction.message.id) not in self.color_message_list:
            omega.logger.info(f"Reaction msg not matched {reaction.message.id} using emoji {reaction.emoji}")
            return

        guild = reaction.message.guild
        omega.logger.info(f"Reaction added by {user} on message {reaction.message.id} using emoji {reaction.emoji}.")

        await reaction.message.remove_reaction(reaction.emoji, user)

        color_roles = [role for role in guild.roles if role.name.startswith('cr_')]
        if color_roles:
            await user.remove_roles(*color_roles)
            omega.logger.info(f"Removed existing color roles from {user}.")

        color_data = self.get_color_data(reaction.emoji)
        if color_data:
            role = discord.utils.get(guild.roles, name=f"cr_{color_data['name']}")
            if role:
                await user.add_roles(role)
                omega.logger.info(f"Assigned role {role.name} to {user}.")
        else:
            omega.logger.info(f"No color data found for emoji {reaction.emoji}.")

async def setup(bot: commands.Bot):
    await bot.add_cog(NameColor(bot))
    omega.logger.info("NameColor Cog loaded successfully.")
