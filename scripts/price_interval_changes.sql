WITH latest_price AS (
	select
		api_id,
		timestamp,
		price,
		ROW_NUMBER() OVER (PARTITION BY api_id ORDER BY timestamp DESC) AS recency_rank
	from coingecko_historical_data
	where api_id = %s
	order by timestamp desc
	limit 1
),
recent_price_list as (
	select
		api_id,
		timestamp,
		price,
		ROW_NUMBER() OVER (PARTITION BY api_id ORDER BY timestamp DESC) AS recencyrank
	from coingecko_historical_data
	where api_id = %s
	and timestamp < (SELECT timestamp FROM latest_price)
	order by timestamp desc
	limit 100
),
change_list AS (
	select
		api_id
		,(SELECT timestamp FROM latest_price) as latesttimestamp
		,(SELECT price FROM latest_price) AS latestprice
		,timestamp AS historicaltimestamp
		,price as historicalprice
		,recencyrank
		,(SELECT price FROM latest_price) - price AS difference
		,ROUND((((SELECT price FROM latest_price) - price) / price) * 100, 2) AS percentchange
	from
		recent_price_list
	order by historicaltimestamp desc
)

select * from change_list
limit 10