WITH latest_data AS (
    SELECT 
        api_id,
        MAX(timestamp) AS latest_timestamp
    FROM 
        coingecko_historical_data
    GROUP BY 
        api_id
),
price_comparison AS (
    SELECT 
        d.api_id,
        d.timestamp,
        d.price,
        ld.latest_timestamp,
        ld.latest_timestamp - (5 * 60) AS five_minutes_ago,
        ld.latest_timestamp - (15 * 60) AS fifteen_minutes_ago,
        ld.latest_timestamp - (30 * 60) AS thirty_minutes_ago,
        ld.latest_timestamp - (60 * 60) AS one_hour_ago,
        ld.latest_timestamp - (24 * 60 * 60) AS twenty_four_hours_ago,
        ld.latest_timestamp - (30 * 24 * 60 * 60) AS one_month_ago,
        ld.latest_timestamp - (6 * 30 * 24 * 60 * 60) AS six_months_ago,
        ld.latest_timestamp - (365 * 24 * 60 * 60) AS one_year_ago
    FROM 
        coingecko_historical_data d
    JOIN 
        latest_data ld
    ON 
        d.api_id = ld.api_id
),
price_increase AS (
    SELECT 
        pc.api_id,
        MAX(CASE WHEN pc.timestamp = pc.latest_timestamp THEN pc.price END) AS latest_price,
        MAX(CASE WHEN pc.timestamp <= pc.five_minutes_ago THEN pc.price END) AS price_five_minutes_ago,
        MAX(CASE WHEN pc.timestamp <= pc.fifteen_minutes_ago THEN pc.price END) AS price_fifteen_minutes_ago,
        MAX(CASE WHEN pc.timestamp <= pc.thirty_minutes_ago THEN pc.price END) AS price_thirty_minutes_ago,
        MAX(CASE WHEN pc.timestamp <= pc.one_hour_ago THEN pc.price END) AS price_one_hour_ago,
        MAX(CASE WHEN pc.timestamp <= pc.twenty_four_hours_ago THEN pc.price END) AS price_twenty_four_hours_ago,
        MAX(CASE WHEN pc.timestamp <= pc.one_month_ago THEN pc.price END) AS price_one_month_ago,
        MAX(CASE WHEN pc.timestamp <= pc.six_months_ago THEN pc.price END) AS price_six_months_ago,
        MAX(CASE WHEN pc.timestamp <= pc.one_year_ago THEN pc.price END) AS price_one_year_ago
    FROM 
        price_comparison pc
    GROUP BY 
        pc.api_id
)
SELECT 
    api_id,
    latest_price,
    -- 5-minute interval
    latest_price - price_five_minutes_ago AS price_increase_last_5_minutes,
    CASE 
        WHEN price_five_minutes_ago > 0 
        THEN ((latest_price - price_five_minutes_ago) / price_five_minutes_ago) * 100
        ELSE NULL
    END AS percent_change_last_5_minutes,
    -- 15-minute interval
    latest_price - price_fifteen_minutes_ago AS price_increase_last_15_minutes,
    CASE 
        WHEN price_fifteen_minutes_ago > 0 
        THEN ((latest_price - price_fifteen_minutes_ago) / price_fifteen_minutes_ago) * 100
        ELSE NULL
    END AS percent_change_last_15_minutes,
    -- 30-minute interval
    latest_price - price_thirty_minutes_ago AS price_increase_last_30_minutes,
    CASE 
        WHEN price_thirty_minutes_ago > 0 
        THEN ((latest_price - price_thirty_minutes_ago) / price_thirty_minutes_ago) * 100
        ELSE NULL
    END AS percent_change_last_30_minutes,
    -- 1-hour interval
    latest_price - price_one_hour_ago AS price_increase_last_1_hour,
    CASE 
        WHEN price_one_hour_ago > 0 
        THEN ((latest_price - price_one_hour_ago) / price_one_hour_ago) * 100
        ELSE NULL
    END AS percent_change_last_1_hour,
    -- 24-hour interval
    latest_price - price_twenty_four_hours_ago AS price_increase_last_24_hours,
    CASE 
        WHEN price_twenty_four_hours_ago > 0 
        THEN ((latest_price - price_twenty_four_hours_ago) / price_twenty_four_hours_ago) * 100
        ELSE NULL
    END AS percent_change_last_24_hours,
    -- 1-month interval
    latest_price - price_one_month_ago AS price_increase_last_1_month,
    CASE 
        WHEN price_one_month_ago > 0 
        THEN ((latest_price - price_one_month_ago) / price_one_month_ago) * 100
        ELSE NULL
    END AS percent_change_last_1_month,
    -- 6-month interval
    latest_price - price_six_months_ago AS price_increase_last_6_months,
    CASE 
        WHEN price_six_months_ago > 0 
        THEN ((latest_price - price_six_months_ago) / price_six_months_ago) * 100
        ELSE NULL
    END AS percent_change_last_6_months,
    -- 1-year interval
    latest_price - price_one_year_ago AS price_increase_last_1_year,
    CASE 
        WHEN price_one_year_ago > 0 
        THEN ((latest_price - price_one_year_ago) / price_one_year_ago) * 100
        ELSE NULL
    END AS percent_change_last_1_year
FROM 
    price_increase;
