#!/usr/bin/env bash
set -e

if [ ! -d ".venv" ]; then
  echo "No existe .venv. Ejecuta primero: ./setup.sh"
  exit 1
fi

echo "Ejecutando aplicación..."
uv run python main.py