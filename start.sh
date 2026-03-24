#!/bin/bash
echo ""
echo "🚀 Starting Kaspim..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 not found. Install it from python.org"
  exit 1
fi

# Install deps if needed
cd backend
if ! python3 -c "import fastapi" 2>/dev/null; then
  echo "📦 Installing backend dependencies..."
  pip install -r requirements.txt
fi

# Start backend in background
echo "✅ Backend starting at http://localhost:8000"
echo "📖 API docs at http://localhost:8000/docs"
python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
echo "✅ Frontend starting at http://localhost:3000"
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Open: http://localhost:3000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
