#!/bin/bash

GIT_REPO_DIR="~/omega"
SERVICE_NAME_UPDATER="omegaupdater"
SERVICE_FILE_UPDATER="/etc/systemd/system/$SERVICE_NAME_UPDATER.service"
SERVICE_NAME_OMEGA="omega"
SERVICE_FILE_OMEGA="/etc/systemd/system/$SERVICE_NAME_OMEGA.service"
ENV_FILE=~/omega/.env

# Create .env file if it doesn't exist
mkdir -p ~/omega
touch $ENV_FILE

# Function to check key existence
check_key() {
    grep -q "$1=" "$ENV_FILE"
}

# Ask for API keys if they don't exist
if ! check_key "OPENAI_API_KEY"; then
    read -p "Enter OpenAI API Key: " openai_key
    echo "OPENAI_API_KEY=$openai_key" >> $ENV_FILE
fi

if ! check_key "GIPHY_API_KEY"; then
    read -p "Enter Giphy API Key: " giphy_key
    echo "GIPHY_API_KEY=$giphy_key" >> $ENV_FILE
fi

if ! check_key "DISCORD_BOT_TOKEN"; then
    read -p "Enter Discord API Key: " discord_key
    echo "DISCORD_BOT_TOKEN=$discord_key" >> $ENV_FILE
fi

echo "API keys checked/added in $ENV_FILE"

# Install omega service
if systemctl list-units --full --all | grep -Fq "$SERVICE_NAME_UPDATER.service"; then
    echo "Service $SERVICE_NAME_UPDATER is already installed."
else
    echo "Description=Omega Discord Bot
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/omega/main.py
Restart=on-failure
User=root
WorkingDirectory=/root/omega
[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE_OMEGA > /dev/null

    chmod +x ~/omega/main.py
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME_OMEGA
    sudo systemctl start $SERVICE_NAME_OMEGA
    echo "Service $SERVICE_NAME_OMEGA installed and started."
fi

# Install updater service
if systemctl list-units --full --all | grep -Fq "$SERVICE_NAME_UPDATER.service"; then
    echo "Service $SERVICE_NAME_UPDATER is already installed."
else
    echo "[Unit]
Description=Omega Git Update Service

[Service]
ExecStart=/root/omega/tools/updater.sh
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE_UPDATER > /dev/null

    chmod +x ~/omega/tools/updater.sh
    chmod +x ~/omega/tools/update.sh
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME_UPDATER
    sudo systemctl start $SERVICE_NAME_UPDATER
    echo "Service $SERVICE_NAME_UPDATER installed and started."
fi

echo "Installation complete"