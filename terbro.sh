#!/usr/bin/env bash

APP="$HOME/Documents/workspace/terbro"
VENV="$APP/tbr-env"
PY="$VENV/bin/python"
SCRIPT="$APP/main.py"

# 1. Clear Cache/Save Mode - No pager
if [[ "$*" == *"--clear"* ]] || [[ "$*" == *"--save"* ]]; then
    "$PY" "$SCRIPT" "$@"
    exit 0
fi

# 2. History Mode - Interactive
if [[ "$*" == *"--history"* ]]; then
    SELECTED_URL=$("$PY" "$SCRIPT" --history)
    if [ -n "$SELECTED_URL" ]; then
        # Pipe the history selection directly to less
        "$PY" "$SCRIPT" "$SELECTED_URL" | less -R -i -M
    fi
    exit 0
fi

# 3. Help
if [[ "$*" == *"-h"* ]] || [[ "$*" == *"--help"* ]] || [ -z "$1" ]; then
    "$PY" "$SCRIPT" --help
    exit 0
fi

# 4. Standard Usage (Direct URL, Markdown, or Refresh)
"$PY" "$SCRIPT" "$@" | less -R -i -M