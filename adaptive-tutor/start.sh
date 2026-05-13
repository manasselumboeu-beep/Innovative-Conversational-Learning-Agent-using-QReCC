#!/usr/bin/env bash
# Start AdaptiveTutor for local development.
# Requires: HF_TOKEN set in .env.local

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "🎓 AdaptiveTutor — starting services..."
echo ""

# Activate virtualenv if present
if [ -f "$ROOT/.venv/bin/activate" ]; then
  source "$ROOT/.venv/bin/activate"
fi

# Start Python FastAPI backend
echo "▶  Python API  →  http://localhost:8001"
cd "$ROOT"
uvicorn api.server:app --reload --port 8001 &
PYTHON_PID=$!

sleep 1

# Start Next.js frontend
echo "▶  Next.js     →  http://localhost:3000"
npm --prefix "$ROOT" run dev &
NEXT_PID=$!

echo ""
echo "✓  AdaptiveTutor running at http://localhost:3000"
echo "   API health: http://localhost:8001/api/health"
echo ""
echo "   Press Ctrl+C to stop both services."
echo ""

trap "kill $PYTHON_PID $NEXT_PID 2>/dev/null; echo 'Stopped.'" INT TERM
wait