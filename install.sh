#!/bin/bash

# Get the user's home directory
USER_HOME="$HOME"
GIT_REPO_DIR="$USER_HOME/omega"
SERVICE_NAME_UPDATER="omegaupdater"
SERVICE_FILE_UPDATER="/etc/systemd/system/$SERVICE_NAME_UPDATER.service"
SERVICE_NAME_OMEGA="omega"
SERVICE_FILE_OMEGA="/etc/systemd/system/$SERVICE_NAME_OMEGA.service"
ENV_FILE="$GIT_REPO_DIR/.env"

# Function to delete a service if it exists
delete_service() {
    local service_name=$1
    local service_file=$2
    if systemctl list-units --full --all | grep -Fq "$service_name.service"; then
        echo "Stopping and disabling service $service_name..."
        sudo systemctl stop $service_name
        sudo systemctl disable $service_name
        sudo rm -f $service_file
        echo "Service $service_name removed."
    else
        echo "Service $service_name does not exist."
    fi
}

# Remove existing services
delete_service "$SERVICE_NAME_UPDATER" "$SERVICE_FILE_UPDATER"
delete_service "$SERVICE_NAME_OMEGA" "$SERVICE_FILE_OMEGA"

# Create .env file if it doesn't exist
mkdir -p "$GIT_REPO_DIR"
touch "$ENV_FILE"

# Function to check key existence
check_key() {
    grep -q "$1=" "$ENV_FILE"
}

# Ask for API keys if they don't exist
if ! check_key "OPENAI_API_KEY"; then
    read -p "Enter OpenAI API Key: " openai_key
    echo "OPENAI_API_KEY=$openai_key" >> "$ENV_FILE"
fi

if ! check_key "GIPHY_API_KEY"; then
    read -p "Enter Giphy API Key: " giphy_key
    echo "GIPHY_API_KEY=$giphy_key" >> "$ENV_FILE"
fi

if ! check_key "DISCORD_BOT_TOKEN"; then
    read -p "Enter Discord API Key: " discord_key
    echo "DISCORD_BOT_TOKEN=$discord_key" >> "$ENV_FILE"
fi

echo "API keys checked/added in $ENV_FILE"

# Install omega service
echo "[Unit]
Description=Omega Discord Bot
After=network.target

[Service]
Type=simple
EnvironmentFile=$ENV_FILE
ExecStart=/usr/bin/python3 $GIT_REPO_DIR/main.py
Restart=on-failure
User=root
WorkingDirectory=$GIT_REPO_DIR

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE_OMEGA > /dev/null

chmod +x "$GIT_REPO_DIR/main.py"
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME_OMEGA
sudo systemctl start $SERVICE_NAME_OMEGA
echo "Service $SERVICE_NAME_OMEGA installed and started."

# Install updater service
echo "[Unit]
Description=Omega Git Update Service
After=network.target

[Service]
ExecStart=/bin/bash $GIT_REPO_DIR/tools/updater.sh
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE_UPDATER > /dev/null

chmod +x "$GIT_REPO_DIR/tools/updater.sh"
chmod +x "$GIT_REPO_DIR/tools/update.sh"
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME_UPDATER
sudo systemctl start $SERVICE_NAME_UPDATER
echo "Service $SERVICE_NAME_UPDATER installed and started."

echo "Installation complete"
