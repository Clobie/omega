#!/bin/bash

SERVICE_NAME="omega"
REPO_DIR="/root/omega"
BRANCH="main"

# Stop the service
echo "Stopping $SERVICE_NAME service..."
sudo systemctl stop "$SERVICE_NAME"
if [ $? -ne 0 ]; then
    echo "Failed to stop $SERVICE_NAME service. Exiting."
    exit 1
fi

# Navigate to the repository directory
echo "Navigating to repository directory: $REPO_DIR"
cd "$REPO_DIR" || { echo "Failed to navigate to $REPO_DIR. Exiting."; exit 1; }

# Perform git checkout
echo "Checking out branch: $BRANCH"
git checkout "$BRANCH"
if [ $? -ne 0 ]; then
    echo "Git checkout failed. Exiting."
    exit 1
fi

# Pull latest changes (optional, if you want the latest updates)
echo "Pulling latest changes from $BRANCH branch..."
git pull origin "$BRANCH"
if [ $? -ne 0 ]; then
    echo "Git pull failed. Exiting."
    exit 1
fi

# Restart the service
echo "Starting $SERVICE_NAME service..."
sudo systemctl start "$SERVICE_NAME"
if [ $? -ne 0 ]; then
    echo "Failed to start $SERVICE_NAME service. Exiting."
    exit 1
fi

# Print the service status
echo "Service status:"
sudo systemctl status "$SERVICE_NAME"

echo "Script completed successfully."
