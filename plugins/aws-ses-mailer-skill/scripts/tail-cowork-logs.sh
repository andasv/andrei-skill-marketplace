#!/usr/bin/env bash
# Tail all Claude Cowork logs in real-time with color-coded filenames
# Usage: ./tail-cowork-logs.sh [filter]
# Example: ./tail-cowork-logs.sh ses-mailer

LOG_DIR="$HOME/Library/Logs/Claude"

if [[ ! -d "$LOG_DIR" ]]; then
  echo "Error: Log directory not found: $LOG_DIR"
  exit 1
fi

if [[ -n "$1" ]]; then
  tail -f "$LOG_DIR"/*.log | grep --line-buffered -i "$1"
else
  tail -f "$LOG_DIR"/*.log
fi
