#!/usr/bin/env bash
set -euo pipefail

# Ensure the models directory exists
mkdir -p "${OLLAMA_MODELS}"

# Start Ollama in the background and capture logs
ollama serve > /tmp/ollama.log 2>&1 &
echo "Starting Ollama..."

# Wait for Ollama readiness with an upper limit of ninety seconds
for i in {1..90}; do
  if curl -s http://127.0.0.1:11434/api/tags >/dev/null; then
    echo "Ollama is up."
    break
  fi
  if [[ $i -eq 90 ]]; then
    echo "Ollama failed to start. Logs:"
    tail -n +200 /tmp/ollama.log || true
    exit 1
  fi
  sleep 1
done

# Pull the mistral model if it is not present
if ! ollama show mistral >/dev/null 2>&1; then
  echo "Pulling model mistral..."
  ollama pull mistral
fi
# Enable this block when an embedding model from Ollama is required
# if ! ollama show nomic-embed-text >/dev/null 2>&1; then
#   ollama pull nomic-embed-text
# fi

# Launch the Streamlit application
exec streamlit run streamlit_app.py --server.port 7860 --server.address 0.0.0.0
