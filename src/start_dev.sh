#!/bin/bash

echo "🚀 Starting S.A.V.E. (Simple Autonomous Validation Engine) Development Environment"
echo "=============================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if uv is available
if ! command_exists uv; then
    echo "❌ uv is required but not found. Please install uv."
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if Node.js is available
if ! command_exists node; then
    echo "❌ Node.js is required but not found. Please install Node.js."
    exit 1
fi

# Check if npm is available
if ! command_exists npm; then
    echo "❌ npm is required but not found. Please install npm."
    exit 1
fi

# Check if we're in the right directory
if [ ! -d "src" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected to find: src/ directory"
    exit 1
fi

if [ ! -d "src/api" ]; then
    echo "❌ src/api directory not found"
    exit 1
fi

if [ ! -d "src/frontend" ]; then
    echo "❌ src/frontend directory not found"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment with uv..."
    uv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

echo "✅ Prerequisites check passed"

# Set environment variables (these will be configured via the web interface)
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
export TAVILY_API_KEY="${TAVILY_API_KEY:-}"
export USDA_API_KEY="${USDA_API_KEY:-}"

echo "ℹ️  API keys will be configured through the web interface"

# Start backend in background
echo "📡 Starting FastAPI backend on port 8000..."
cd src/api

echo "   Syncing Python dependencies with uv..."
cd ../..
uv sync
if [ $? -ne 0 ]; then
    echo "❌ Failed to sync Python dependencies"
    exit 1
fi
cd src/api

echo "   Starting backend server..."
cd ../..
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