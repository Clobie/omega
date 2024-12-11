import requests
import psycopg2

API_KEY=""

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

base_api_url = "https://api.coingecko.com/api/v3"
headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": f"{API_KEY}"
}

url = f"{base_api_url}/coins/list"
result = requests.get(url, headers).json()

inserted_count = 0
skipped_count = 0

for coin in result:
    coin_id = coin["id"]
    symbol = coin["symbol"]
    name = coin["name"]
    script = (
        "INSERT INTO coingecko_list (api_id, symbol, name) "
        "VALUES (%s, %s, %s) "
        "ON CONFLICT (name) DO NOTHING;"
    )
    affected_rows = run_script(script, (coin_id, symbol, name))
    print(f"{affected_rows} rows affected.  Total: {inserted_count}")
    if affected_rows > 0:
        inserted_count += affected_rows
    else:
        skipped_count += 1

cursor.close()
connection.close()