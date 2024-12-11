# utils/coingecko.py

import os
import json
import requests
from datetime import datetime
from utils.log import logger
from utils.config import cfg
from utils.database import db

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
        query = f"UPDATE coingecko_list SET coin_tracking = %s WHERE app_id = %s"
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
        logger.debug(f"Exists: {results}")
        logger.debug(f"Exists: {results[0]}")
        if results[0] == api_id:
            return True
        return False

cg = CoinGecko()