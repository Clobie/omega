# utils/coingecko.py

import os
import json
import requests
from datetime import datetime
from utils.log import logger
from utils.config import cfg
from utils.database import db
from utils.common import common

class CoinGecko:
    def __init__(self):
        self.base_api_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": f"{cfg.COINCECKO_API_KEY}"
        }

    def get_price(self, coins):
        url = f"{self.base_api_url}/simple/price?ids={coins}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true&precision=full"
        return requests.get(url, self.headers)
    
    def get_supported_currencies_list(self):
        url = f"{self.base_api_url}/simple/supported_vs_currencies"
        return requests.get(url, self.headers)

    def get_list_with_market_data(self, coins):
        url = f"{self.base_api_url}/coins/markets?vs_currency=usd&ids={coins}"
        return requests.get(url, self.headers)
    
    def get_historical_chart_data_within_time_range(self, coin, time_start, time_end):
        url = f"{self.base_api_url}/coins/{coin}/market_chart/range?vs_currency=usd&from={time_start}&to={time_end}&precision=full"
        return requests.get(url, self.headers)

    def get_table_from_name(self, name):
        query = f"SELECT coin_api_id, coin_symbol, coin_name FROM coingecko_list WHERE coin_name = %s;"
        results = db.run_script(query, (name,))
        return results

    def get_table_from_symbol(self, name):
        query = f"SELECT coin_api_id, coin_symbol, coin_name FROM coingecko_list WHERE coin_symbol = %s;"
        results = db.run_script(query, (name,))
        return results
    
    def get_table_from_api_id(self, name):
        query = f"SELECT coin_api_id, coin_symbol, coin_name FROM coingecko_list WHERE coin_api_id = %s;"
        results = db.run_script(query, (name,))
        return results
    
    def set_coin_tracking(self, app_id, track):
        query = f"UPDATE coingecko_list SET coin_tracking = %s WHERE coin_api_id = %s"
        if track != 'true' and track != 'false':
            return None
        results = db.run_script(query, (track, app_id,))
        return results
    
    def get_tracked_coin_api_ids(self):
        query = f"SELECT coin_api_id FROM coingecko_list WHERE coin_tracking = true"
        results = db.run_script(query)
        return results

    def api_id_exists(self, api_id):
        query = f"SELECT coin_api_id FROM coingecko_list WHERE coin_api_id = %s"
        results = db.run_script(query, (api_id,))
        if results[0][0] == api_id:
            return True
        return False

    def query_and_insert_historical_data(self, api_id, time_from, time_to):
        logger.debug(f"Querying historical data for {api_id}")
        url = f"{self.base_api_url}/coins/{api_id}/market_chart/range?vs_currency=usd&from={time_from}&to={time_to}&precision=10"
        results = requests.get(url, self.headers)
        
        if results.status_code != 200:
            logger.error(f"Request failed with status code {results.status_code}: {results.text}")
            return 0

        try:
            data = results.json()
            logger.debug(f"Response data: {data}")
        except ValueError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return 0

        if 'prices' not in data or 'market_caps' not in data or 'total_volumes' not in data:
            logger.error(f"Unexpected response structure: {data}")
            return 0

        timestamps = [item[0] for item in data['prices']]
        logger.debug(f"timestamps data: {timestamps}")

        prices = [item[1] for item in data['prices']]
        logger.debug(f"prices data: {prices}")

        market_caps = [item[1] for item in data['market_caps']]
        logger.debug(f"market_caps data: {market_caps}")

        total_volumes = [item[1] for item in data['total_volumes']]
        logger.debug(f"total_volumes data: {total_volumes}")

        interval = ""#common.get_unix_interval(timestamps[0], timestamps[1])
        logger.debug(f"interval data: {interval}")
        total_rows_affected = 0
        for i in range(len(timestamps)):
            script = (
                "INSERT INTO coingecko_historical_data (api_id, timestamp, price, market_cap, total_volume, interval) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            rows_affected = db.run_script(
                script,
                (api_id, timestamps[i], prices[i], market_caps[i], total_volumes[i], interval),
            )
            total_rows_affected += rows_affected

        logger.debug(f"{total_rows_affected} rows affected.")
        return total_rows_affected


cg = CoinGecko()