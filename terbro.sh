#!/usr/bin/env bash

APP="$HOME/Documents/workspace/terbro"
VENV="$APP/tbr-env"
PY="$VENV/bin/python"
SCRIPT="$APP/main.py"

# Capture all flags
ARGS="$@"

# Logic:
# If arguments contain --navigate, --history (without a URL), or --save, 
# we run Python directly so it handles the interaction.
# Otherwise, we pipe to 'less' for reading.

if [[ -z "$ARGS" ]]; then
    "$PY" "$SCRIPT" --help
    exit 0
fi

if [[ "$ARGS" == *"--navigate"* ]] || [[ "$ARGS" == *"--save"* ]] || [[ "$ARGS" == *"--history"* ]] || [[ "$ARGS" == *"--help"* ]]; then
    # Interactive mode or modes that don't need paging
    "$PY" "$SCRIPT" $ARGS
else
    # Reading mode: Pipe to less
    # -R: Read color codes
    # -i: Ignore case in search
    # -M: Verbose prompt (shows percentage)
    # --fold-w: Handle long lines better
    "$PY" "$SCRIPT" $ARGS | less -R -i -M
fi