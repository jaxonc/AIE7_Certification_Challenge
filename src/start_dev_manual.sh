#!/bin/bash

echo "🚀 Starting S.A.V.E. (Simple Autonomous Validation Engine) - Manual uv setup"
echo "=============================================="

# Check if we're in the right directory
if [ ! -d "src" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected to find: src/ directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   uv sync"
    exit 1
fi

echo "✅ Using existing virtual environment"
echo "ℹ️  API keys will be configured through the web interface"

# Start backend in background
echo "📡 Starting FastAPI backend on port 8000..."
echo "   Starting backend server with uv..."
uv run python -m src.api.app &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Install frontend dependencies if needed
echo "📦 Installing frontend dependencies..."
cd src/frontend
if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Node.js dependencies"
        cd ../..
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
fi

# Start frontend
echo "🎨 Starting Next.js frontend on port 3000..."
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo "🎉 Development environment started!"
echo "=================================="
echo "📡 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "To stop both services, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Development environment stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Keep script running
wait