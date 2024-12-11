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
    async def get_crypto_quote(self, ctx, ticker: str):
        """
        Get the price of crypto
        """
        ticker = ticker.upper()
        ticker_key = f"{ticker}/USD"
        url = f"{self.base_url_quotes}?symbols={ticker_key}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            trade_info = data.get('quotes', {}).get(ticker_key, None)
            if trade_info:
                spread = trade_info['ap'] - trade_info['bp']
                embed = discord.Embed(title=f"{ticker} Latest Information", color=omega.cfg.PRIMARYCOLOR)
                embed.add_field(name="Bid Price", value=f"${trade_info['bp']}", inline=True)
                #embed.add_field(name="Bid Size", value=f"{trade_info['bs']}", inline=False)
                embed.add_field(name="Ask Price", value=f"${trade_info['ap']}", inline=True)
                #embed.add_field(name="Ask Size", value=f"{trade_info['as']}", inline=False)
                embed.add_field(name="Spread", value=f"${spread:.2f}", inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("No trade information found for this ticker.")
        else:
            await ctx.send("Error retrieving data.")
    
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
    async def search_crypto_id(self, ctx):
        results = omega.cg.get_tracked_coin_app_ids()
        embed = omega.embed.create_embed("Tracked coins", "")
        for item in results:
            embed.add_field(name="", value=f"> API ID: **{item}**\n\n", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CryptoPriceCog(bot))