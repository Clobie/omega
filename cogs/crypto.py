# cogs/crypto.py

import discord
from discord.ext import commands
import requests
from core.omega import omega

class CryptoPriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url_quotes = "https://data.alpaca.markets/v1beta3/crypto/us/latest/quotes"
        self.headers = {"accept": "application/json"}

    @commands.command(name='quote')
    async def get_crypto_quote(self, ctx, app_id: str):
        """
        Get the price of a crypto coin
        """

        # Add a check for a valid app_id

        results = omega.cg.get_price(app_id)
        price = results['bitcoin']['usd']
        market_cap = results['bitcoin']['usd_market_cap']
        vol_24h = results['bitcoin']['usd_24h_vol']
        change_24h = results['bitcoin']['usd_24h_change']
        embed = omega.embed.create_embed(f"Price quote for {app_id}", "")
        embed.add_field(name="", value=f"> API ID: **{app_id}**\n> Price: {price}\n> Market Cap: {market_cap}\n> 24h Volume: {vol_24h}\n> 24h Change: {change_24h}", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name="search")
    async def search_crypto_id(self, ctx, symbol: str):
        results = omega.cg.get_table_from_name(symbol)
        if not results:
            results = omega.cg.get_table_from_symbol(symbol)
        if not results:
            await ctx.send("No results")
            return
        embed = omega.embed.create_embed("Search results", f"Search: {symbol}\n\n")
        for item in results:
            api_id, sym, name = item
            embed.add_field(name="", value=f"> API ID: **{api_id}**\n> Symbol: {sym}\n> Name: {name}\n\n", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name="tracked")
    async def tracked_coins(self, ctx):
        results = omega.cg.get_tracked_coin_app_ids()
        embed = omega.embed.create_embed("Tracked coins", "")
        for item in results:
            embed.add_field(name="", value=f"> **{item[0]}**\n", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CryptoPriceCog(bot))