#!/bin/bash
set -e

# Change ownership of the workspace and other github directories to appuser
# This runs as root before switching to appuser
if [ -d "/github" ]; then
    chown -R appuser:appuser /github
fi

# Switch to appuser and run the main entrypoint
exec gosu appuser python /action_entrypoint.py "$@"
