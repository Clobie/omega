#!/bin/bash

LOG_FILE="/var/log/omegaupdater.log"
GIT_REPO_DIR="/root/omega"

echo "Starting updater at $(date)" >> $LOG_FILE

if [ ! -d "$GIT_REPO_DIR" ]; then
    echo "Directory $GIT_REPO_DIR not found at $(date)" >> $LOG_FILE
    exit 1
fi

while true; do
    echo "Checking repository updates at $(date)" >> $LOG_FILE
    cd "$GIT_REPO_DIR" || { echo "Failed to cd to $GIT_REPO_DIR at $(date)" >> $LOG_FILE; exit 1; }

    git fetch origin >> $LOG_FILE 2>&1
    LOCAL_HEAD=$(git rev-parse HEAD)
    REMOTE_HEAD=$(git rev-parse origin/main)

    if [ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]; then
        echo "Updates detected. Resetting and pulling latest changes at $(date)" >> $LOG_FILE

        # Force reset and pull
        git reset --hard origin/main >> $LOG_FILE 2>&1
        git pull origin main >> $LOG_FILE 2>&1

        # Run the update script
        "$GIT_REPO_DIR/tools/update.sh" >> $LOG_FILE 2>&1
        echo "Updates applied successfully at $(date)" >> $LOG_FILE
        sleep 30
    fi

    sleep 15
done
