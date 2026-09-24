#!/bin/sh
set -e

echo "Aplicando migrations..."
alembic upgrade head

echo "Rodando seed (idempotente)..."
python -m scripts.seed

echo "Iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
