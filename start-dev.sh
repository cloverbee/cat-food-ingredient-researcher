#!/bin/bash

# Development startup script for Cat Food Ingredient Researcher
# This script starts both backend and frontend in development mode

echo "🐱 Cat Food Ingredient Researcher - Development Environment"
echo "==========================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please create one with: python -m venv .venv"
    exit 1
fi

# Check if node_modules exists in frontend
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}❌ Frontend dependencies not installed!${NC}"
    echo "Please run: cd frontend && npm install"
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${BLUE}🛑 Shutting down services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap SIGINT and SIGTERM to cleanup
trap cleanup INT TERM

# Start Backend
echo -e "${GREEN}🚀 Starting Backend (FastAPI)...${NC}"
echo "   Backend will be available at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"
echo ""
source .venv/bin/activate
cd src
python -m uvicorn api.main:app --reload --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start! Check logs/backend.log for details${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Backend started successfully (PID: $BACKEND_PID)${NC}"
echo ""

# Start Frontend
echo -e "${GREEN}🚀 Starting Frontend (Next.js)...${NC}"
echo "   Frontend will be available at: http://localhost:3000"
echo ""
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

echo ""
echo -e "${GREEN}✅ Frontend started successfully (PID: $FRONTEND_PID)${NC}"
echo ""
echo "==========================================================="
echo -e "${BLUE}📍 Services Running:${NC}"
echo "   🔧 Backend:  http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🎨 Frontend: http://localhost:3000"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "==========================================================="
echo ""

# Wait for user interrupt
wait

