#!/bin/sh
set -eu

CDPATH= cd -P "$(dirname "$0")"
exec uv run --no-sync --offline marimo run slides.py --headless --host 127.0.0.1 --port "${1:-2718}"
