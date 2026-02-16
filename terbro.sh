#!/usr/bin/env bash

APP="$HOME/Documents/workspace/terbro"
VENV="$APP/tbr-env"
PY="$VENV/bin/python"
SCRIPT="$APP/main.py"

# If user asks for help, history, or saving a file, don't use the pager
if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]] || [[ "$*" == *"--save"* ]] || [[ "$*" == *"--history"* ]] || [[ "$*" == *"--search"* ]]; then
    "$PY" "$SCRIPT" "$@"
else
    # Use -R for ANSI color support in less
    "$PY" "$SCRIPT" "$@" | less -R -M -i -j5
fi