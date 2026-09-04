set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default: check

sync:
    uv sync

edit:
    uv run marimo edit slides.py

present port="":
    ./present.sh {{ quote(port) }}

check:
    just --fmt --check
    uv lock --check
    uv run ruff check .
    uv run ruff format --check .
    uv run rumdl check .
    uv run ty check
    uv run marimo check --strict slides.py
    uv run python check_slide_variants.py

format:
    uv run ruff check --fix .
    uv run ruff format .
    uv run rumdl fmt .
