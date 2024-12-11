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
    async def get_crypto_quote(self, ctx, api_id: str):
        """
        Get the price of a crypto coin or token
        """
        results = omega.cg.get_table_from_api_id(api_id)
        if not results:
            results
        results = omega.cg.get_price(api_id)
        results_json = results.json()

        omega.logger.debug(results_json)

        price = results_json[api_id]['usd']
        if price >= 1:
            price = "${:,.2f}".format(price)
        else:
            price = "${:,.10f}".format(price)
        market_cap = "${:,.2f}".format(results_json[api_id]['usd_market_cap'])
        vol_24h = "${:,.2f}".format(results_json[api_id]['usd_24h_vol'])
        change_24h_value = results_json[api_id]['usd_24h_change']
        change_24h = "{:+.2f}%".format(change_24h_value)
        embed = omega.embed.create_embed(f"Price quote for {api_id}", "")
        embed.add_field(name="", value=f"> API ID: **{api_id}**\n> Price: **{price}**\n> Market Cap: {market_cap}\n> 24h Volume: {vol_24h}\n\n24h Price Change\n```diff\n{change_24h}```", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name="search")
    async def search_crypto_id(self, ctx, symbol: str):
        """
        Search for the api id of a coin or token
        """
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
        chunked = False
        for item in results:
            api_id, sym, name = item
            desc += f"> API ID: **{api_id}**\n> Symbol: {sym}\n> Name: {name}\n\n"
            # field limit is 1024, stop before that and chunk.  this gets past field limit of 25 and size limit of 1024
            if len(desc) > 800:
                chunked = True
                embed.add_field(name="", value=desc, inline=False)
                desc = ""
        if not chunked:
            embed.add_field(name="", value=desc, inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name="tracker")
    async def tracked_coins(self, ctx):
        """
        List tracked coins or tokens
        """
        results = omega.cg.get_tracked_coin_api_ids()
        embed = omega.embed.create_embed("Tracked coins", "")

        quotes = ",".join(item for item in results)
        price_results = omega.cg.get_price(quotes)
        price_json = price_results.json()

        for item in price_json:
            price = price_json[item]['usd']
            if price >= 1:
                price = "${:,.2f}".format(price)
            else:
                price = "${:,.10f}".format(price)
            market_cap = "${:,.2f}".format(price_json[item]['usd_market_cap'])
            vol_24h = "${:,.2f}".format(price_json[item]['usd_24h_vol'])
            change_24h_value = price_json[item]['usd_24h_change']
            change_24h = "{:+.2f}%".format(change_24h_value)
            embed.add_field(
                name="", 
                value=f"> **{item}**\n> Price: **{price}**\n24h Price Change\n```diff\n{change_24h}```",
                inline=False
            )
        await ctx.send(embed=embed)
    
    @commands.command(name="track")
    async def track_coin(self, ctx, api_id):
        """
        Add a crypto api id to tracker
        """
        exists = omega.cg.api_id_exists(api_id)
        if exists:
            if omega.cg.set_coin_tracking(api_id, 'true'):
                embed = omega.embed.create_embed(f"Added {api_id} to tracker", "")
                await ctx.send(embed=embed)
                return
    
    @commands.command(name="untrack")
    async def untrack_coin(self, ctx, api_id):
        """
        Remove a crypto api id from the tracker
        """
        exists = omega.cg.api_id_exists(api_id)
        if exists:
            if omega.cg.set_coin_tracking(api_id, 'false'):
                embed = omega.embed.create_embed(f"Removed {api_id} from tracker", "")
                await ctx.send(embed=embed)
                return

async def setup(bot):
    await bot.add_cog(CryptoPriceCog(bot))