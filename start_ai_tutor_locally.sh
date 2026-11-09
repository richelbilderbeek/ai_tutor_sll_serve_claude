#!/bin/bash
#
# Start the AI tutor locally, then open http://localhost:7860
#
# Usage:
#
#   ./start_ai_tutor_locally.sh
#
# Needs a file called 'api_key' in this folder, containing the API key.
# Stop the AI tutor with ./stop_ai_tutor.sh
set -e

if [ ! -f api_key ]; then
  echo "Error: file 'api_key' not found. Put your API key in a file called 'api_key'."
  exit 1
fi

docker run --rm --name ai_tutor -p 7860:7860 -e LLM_API_KEY="$(cat api_key)" ghcr.io/richelbilderbeek/ai_tutor_sll_serve_claude:3287d96
