CREATE TABLE discord_users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    credits INT DEFAULT 0,
    messages_count INT DEFAULT 0
);

CREATE TABLE discord_servers (
    server_id SERIAL PRIMARY KEY,
    server_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_server_activity (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES discord_users(user_id),
    server_id INT REFERENCES discord_servers(server_id),
    word_count JSONB,
    activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE openapi_usage (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    tokens INT NOT NULL,
    cost_value NUMERIC(18, 8) NOT NULL,
    usage_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
