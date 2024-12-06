#!/bin/bash

LOG_FILE="/var/log/omegaupdater.log"
echo "Starting updater at $(date)" >> $LOG_FILE

GIT_REPO_DIR="$HOME/omega"

if [ ! -d "$GIT_REPO_DIR" ]; then
    echo "Directory $GIT_REPO_DIR not found at $(date)" >> $LOG_FILE
    exit 1
fi

while true; do
    echo "Checking repository updates at $(date)" >> $LOG_FILE
    cd "$GIT_REPO_DIR" || { echo "Failed to cd to $GIT_REPO_DIR at $(date)" >> $LOG_FILE; exit 1; }

    git fetch origin >> $LOG_FILE 2>&1
    if [ "$(git -C "$GIT_REPO_DIR" rev-parse HEAD)" != "$(git -C "$GIT_REPO_DIR" rev-parse origin/main)" ]; then
        echo "Updates detected. Applying updates at $(date)" >> $LOG_FILE
        "$GIT_REPO_DIR/tools/update.sh" >> $LOG_FILE 2>&1
        echo "$(git -C "$GIT_REPO_DIR" rev-parse HEAD)" > "$GIT_REPO_DIR/.last_commit"
        sleep 30
    fi
    sleep 15
done
