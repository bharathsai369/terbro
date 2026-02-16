#!/usr/bin/env bash

APP="$HOME/Documents/workspace/ter-bro-reads"
VENV="$APP/tbr-env"
PY="$VENV/bin/python"
SCRIPT="$APP/main.py"

# Capture all flags
ARGS="$@"

# Check if we should SKIP the pager (less)
# We skip if no args, or if help/save/history is involved
if [[ -z "$ARGS" ]] || [[ "$ARGS" == *"--help"* ]] || [[ "$ARGS" == *"-h"* ]] || [[ "$ARGS" == *"--save"* ]] || [[ "$ARGS" == *"--history"* ]] || [[ "$ARGS" == *"--search"* ]]; then
    "$PY" "$SCRIPT" $ARGS
else
    # -R : Allows ANSI colors in less
    # -i : Case-insensitive search inside less
    # -+G: FORCE less to start at the top (Line 1)
    "$PY" "$SCRIPT" $ARGS | less -R -i -M -+G
fi