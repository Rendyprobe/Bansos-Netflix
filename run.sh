#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ -x "$SCRIPT_DIR/myenv/bin/python" ]; then
    exec "$SCRIPT_DIR/myenv/bin/python" "$SCRIPT_DIR/nf-token-generator.py"
fi

exec python3 "$SCRIPT_DIR/nf-token-generator.py"
