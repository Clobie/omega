#!/bin/bash

# Use the full path to the repository directory
GIT_REPO_DIR="$HOME/omega"

while true; do
    # Navigate to the Git repository directory
    cd "$GIT_REPO_DIR" || { echo "Directory $GIT_REPO_DIR not found"; exit 1; }
    
    # Fetch updates from the remote repository
    git fetch origin
    
    # Check if the local HEAD is different from the remote HEAD
    if [ "$(git -C "$GIT_REPO_DIR" rev-parse HEAD)" != "$(git -C "$GIT_REPO_DIR" rev-parse origin/main)" ]; then
        # Save the current HEAD commit hash to a file
        echo "$(git -C "$GIT_REPO_DIR" rev-parse HEAD)" > "$GIT_REPO_DIR/.last_commit"
        
        # Execute the update script
        "$GIT_REPO_DIR/tools/update.sh"
        
        # Wait for 30 seconds before continuing
        sleep 30
    fi
    
    # Wait for 15 seconds before the next iteration
    sleep 15
done
