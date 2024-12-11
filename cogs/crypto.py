# cogs/crypto.py

import discord
from discord.ext import commands
import requests
from datetime import datetime
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

        results = omega.cg.get_table_from_api_id(app_id)
        if not results:
            results

        results = omega.cg.get_price(app_id)
        results_json = results.json()

        omega.logger.debug("\n\n")
        omega.logger.debug(results)
        omega.logger.debug("\n\n")
        omega.logger.debug(results_json)
        omega.logger.debug("\n\n")

        price = results_json[app_id]['usd']
        if price >= 1:
            price = "${:,.2f}".format(price)
        else:
            price = "${}".format(price)
        market_cap = "${:,.2f}".format(results_json[app_id]['usd_market_cap'])
        vol_24h = "${:,.2f}".format(results_json[app_id]['usd_24h_vol'])
        change_24h_value = results_json[app_id]['usd_24h_change']
        change_24h = "{:+.2f}%".format(change_24h_value)
        embed = omega.embed.create_embed(f"Price quote for {app_id}", "")
        embed.add_field(name="", value=f"> API ID: **{app_id}**\n> Price: {price}\n> Market Cap: {market_cap}\n> 24h Volume: {vol_24h}\n> 24h Change: {change_24h}", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name="search")
    async def search_crypto_id(self, ctx, symbol: str):
        results = omega.cg.get_table_from_symbol(symbol)
        if not results:
            results = omega.cg.get_table_from_api_id(symbol)
        if not results:
            results = omega.cg.get_table_from_name(symbol)
        if not results:
            await ctx.send("No results")
            return
        embed = omega.embed.create_embed("Search results", f"Search: {symbol}\n\n")
        desc = ""
        for item in results:
            api_id, sym, name = item
            desc += f"> API ID: **{api_id}**\n> Symbol: {sym}\n> Name: {name}\n\n"
        embed.add_field(name="", value=desc, inline=False)
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