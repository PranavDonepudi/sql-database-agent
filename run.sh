#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Copy .env if not present
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit it to change settings"
fi

# Install deps if needed
if ! python -c "import fastapi" 2>/dev/null; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
fi

# Download DB if needed
python setup_db.py

# Pull the model if using Ollama and it's not present
MODEL=$(grep OLLAMA_MODEL .env | cut -d= -f2)
MODEL=${MODEL:-qwen2.5-coder:7b}
if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
  echo "Pulling Ollama model: $MODEL (this may take a few minutes)..."
  ollama pull "$MODEL"
fi

echo ""
echo "Starting server at http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
