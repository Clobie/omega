

import requests
import psycopg2
import json
from datetime import datetime

connection = psycopg2.connect(
    dbname="omega",
    user="omega",
    password="omega",
    host="127.0.0.1",
    port=5432
)

cursor = connection.cursor()

def run_script(query, params=None):
    """
    Execute a SQL query with optional parameters and return the number of affected rows.
    """
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Error executing query: {e}")
        connection.rollback()
        return 0

def get_unix_timestamp(date_str, date_format="%Y-%m-%d %H:%M:%S"):
    dt = datetime.strptime(date_str, date_format)
    return int(dt.timestamp())

API_KEY=''
api_id = 'bitcoin'
from_time = get_unix_timestamp('2024-11-01 00:00:00')
to_time = get_unix_timestamp('2024-11-10 00:00:00')

base_api_url = "https://api.coingecko.com/api/v3"
headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": f"{API_KEY}"
}

url = f"{base_api_url}/coins/{api_id}/market_chart/range?vs_currency=usd&from={from_time}&to={to_time}&interval=5m&precision=10"
result = requests.get(url, headers).json()


with open('output.json', 'w') as json_file:
    json.dump(result, json_file, indent=4)

cursor.close()
connection.close()



sample_data = {
    "prices": [
        [
            1733936465421,
            100646.8428649161
        ]
    ],
    "market_caps": [
        [
            1733936465421,
            1992225859049.791
        ]
    ],
    "total_volumes": [
        [
            1733936465421,
            125396600001.84285
        ]
    ]
}