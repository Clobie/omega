#!/bin/bash

GIT_REPO_DIR="~/omega"

while true; do
    cd $GIT_REPO_DIR || exit
    git fetch origin
    if [ "$(git -C "$GIT_REPO_DIR" rev-parse HEAD)" != "$(git -C "$GIT_REPO_DIR" rev-parse origin/main)" ]; then
        echo "$(git -C "$GIT_REPO_DIR" rev-parse HEAD)" > "$GIT_REPO_DIR/.last_commit"
        ~/omega/tools/update.sh
        sleep 30
    fi
    sleep 15
done