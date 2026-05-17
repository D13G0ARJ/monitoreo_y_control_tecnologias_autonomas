#!/usr/bin/env bash
set -e

echo "Configurando entorno Python..."

if [ ! -f ".python-version" ]; then
  echo "Fijando Python 3.12..."
  uv python pin 3.12
fi

if [ ! -d ".venv" ]; then
  echo "Creando entorno virtual..."
  uv venv --python 3.12
else
  echo "El entorno virtual ya existe."
fi

echo "Instalando dependencias..."
uv pip install -r requirements.txt

echo "Setup completado."
echo "Para ejecutar las pruebas: ./test.sh"