#!/usr/bin/env bash
set -euo pipefail

# Function to normalize username: lowercase and replace spaces with hyphens
normalize_username() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | tr ' ' '-'
}

# Function to find existing task users
find_existing_users() {
  local tasks_dir="${1:-tasks}"
  if [ -d "$tasks_dir" ]; then
    # Find directories in tasks/ and extract just the directory names
    find "$tasks_dir" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort | tr '\n' ',' | sed 's/,$//'
  fi
}

# Collect metadata
DATETIME_TZ=$(date '+%Y-%m-%d %H:%M:%S %Z')
FILENAME_TS=$(date '+%Y-%m-%d_%H-%M-%S')

if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  REPO_ROOT=$(git rev-parse --show-toplevel)
  REPO_NAME=$(basename "$REPO_ROOT")
  GIT_BRANCH=$(git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD)
  GIT_COMMIT=$(git rev-parse HEAD)
  RESEARCHER_NAME=$(git config user.name 2>/dev/null || echo "")
  
  # Determine normalized username
  if [ -n "$RESEARCHER_NAME" ]; then
    NORMALIZED_USERNAME=$(normalize_username "$RESEARCHER_NAME")
  else
    NORMALIZED_USERNAME=""
  fi
else
  REPO_ROOT=""
  REPO_NAME=""
  GIT_BRANCH=""
  GIT_COMMIT=""
  RESEARCHER_NAME=""
  NORMALIZED_USERNAME=""
fi

# Find existing users in tasks directory
EXISTING_USERS=$(find_existing_users "${REPO_ROOT}/tasks")

# Print metadata
echo "Current Date/Time (TZ): $DATETIME_TZ"
[ -n "$GIT_COMMIT" ] && echo "Current Git Commit Hash: $GIT_COMMIT"
[ -n "$GIT_BRANCH" ] && echo "Current Branch Name: $GIT_BRANCH"
[ -n "$REPO_NAME" ] && echo "Repository Name: $REPO_NAME"
[ -n "$RESEARCHER_NAME" ] && echo "Researcher Name: $RESEARCHER_NAME"
[ -n "$NORMALIZED_USERNAME" ] && echo "Normalized Username: $NORMALIZED_USERNAME"
[ -n "$EXISTING_USERS" ] && echo "Existing Users: $EXISTING_USERS"
echo "Timestamp For Filename: $FILENAME_TS"