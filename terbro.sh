#!/usr/bin/env bash

# Location of project
APP="$HOME/Documents/workspace/terbro"
VENV="$APP/tbr-env"
PY="$VENV/bin/python"
SCRIPT="$APP/main.py"

if [ -z "$1" ]; then
    echo "Usage: terbro <url>"
    exit 1
fi

# run program inside venv and open pager
"$PY" "$SCRIPT" "$1" | less -R -M -i
