# cogs/help.py

import discord
from discord.ext import commands
from core.omega import omega

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, context):
        """
        List commands
        """
        prefix = context.prefix
        if not isinstance(prefix, str):
            prefix = prefix[0]
        embed = discord.Embed(title="Help", description="List of available commands and functionality:\n\n", color=discord.Color(int(omega.cfg.PRIMARYCOLOR, 16)))
        help_text_lines = []
        for cog_name, cog_obj in self.bot.cogs.items():
            cogname = cog_name.replace("cog", "")
            if cog_obj.__doc__:
                help_text_lines.append(f"**{cogname.capitalize()} - Description:** {cog_obj.__doc__.strip()}\n")
            commands = cog_obj.get_commands()
            commands_with_help = [(command.name, command.help, command.params) for command in commands if command.help]
            for name, help_text, params in commands_with_help:
                param_info = f"{' '.join(params.keys())}" if params else ""
                help_text_lines.append(f"**{name.capitalize()} - {help_text}**\n```{prefix}{name} {param_info}```")
        if help_text_lines:
            embed.description += '\n'.join(help_text_lines)
        embed.description += '\n\n'
        embed.add_field(name="", value="Powered by [Omega](https://github.com/Clobie/omega.git)", inline=False)
        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))