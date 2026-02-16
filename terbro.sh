#!/usr/bin/env bash

APP="$HOME/Documents/workspace/terbro"
VENV="$APP/tbr-env"
PY="$VENV/bin/python"
SCRIPT="$APP/main.py"

# 1. Clear Cache - No pager
if [[ "$*" == *"--clear"* ]]; then
    "$PY" "$SCRIPT" --clear
    exit 0
fi

# 2. History Mode - Interactive
if [[ "$*" == *"--history"* ]]; then
    # We capture stdout. The menu prints to stderr so you'll see it.
    SELECTED_URL=$("$PY" "$SCRIPT" --history)
    
    if [ -n "$SELECTED_URL" ]; then
        # If user picked something, display it through less
        "$PY" "$SCRIPT" "$SELECTED_URL" | less -R -i -M
    fi
    exit 0
fi

# 3. Help - No pager
if [[ "$*" == *"-h"* ]] || [[ "$*" == *"--help"* ]] || [ -z "$1" ]; then
    "$PY" "$SCRIPT" --help
    exit 0
fi

# 4. Standard Usage (Direct URL or Refresh)
# We pipe to less only for content viewing
"$PY" "$SCRIPT" "$@" | less -R -i -M