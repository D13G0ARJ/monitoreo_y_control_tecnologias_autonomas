#!/usr/bin/env bash
set -euo pipefail
uv run --group dev pytest "$@"
