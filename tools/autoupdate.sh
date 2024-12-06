#!/bin/bash

SERVICE_NAME="omega"
GIT_REPO_DIR="/root/omega"
UPDATE_FLAG_FILE="/root/omega/logs"

# Function to check if the service is running
check_service() {
    systemctl is-active --quiet $SERVICE_NAME
}

# Function to stop the service
stop_service() {
    systemctl stop $SERVICE_NAME
}

# Function to start the service
start_service() {
    systemctl start $SERVICE_NAME
}

# Function to update the service from git
update_service() {
    cd $GIT_REPO_DIR || exit
    git checkout main
    start_service
    echo '1' > $UPDATE_FLAG_FILE
}

# Monitor service and perform actions
if ! check_service; then
    start_service
fi

# Check for updates from the remote
cd $GIT_REPO_DIR || exit
git fetch origin

# Compare local branch with remote branch
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    echo "$(git rev-parse HEAD)" > $GIT_REPO_DIR/.last_commit
    stop_service
    update_service
fi