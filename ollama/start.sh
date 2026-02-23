#!/bin/bash
set -e

MODEL="${OLLAMA_MODEL:-qwen2.5:0.5b}"

echo "Starting Ollama server..."
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama server to start..."
until ollama list > /dev/null 2>&1; do
    echo "  Ollama not ready yet, retrying in 2s..."
    sleep 2
done
echo "Ollama server is ready!"

# Pull model if not already present
if ! ollama list | grep -q "$MODEL"; then
    echo "Pulling model: $MODEL (this may take a while on first run)..."
    ollama pull "$MODEL"
    echo "Model $MODEL pulled successfully!"
else
    echo "Model $MODEL already available."
fi

echo "Ollama is ready with model: $MODEL"

# Keep container alive
wait
