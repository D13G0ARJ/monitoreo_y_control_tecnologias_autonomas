#!/usr/bin/env bash

if [ ! -d ".venv" ]; then
  echo "Error: no existe .venv."
  echo "Ejecuta primero: ./setup.sh"
  return 1 2>/dev/null || exit 1
fi

source .venv/bin/activate

echo "Entorno virtual activado."
python --version
