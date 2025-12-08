#!/bin/bash

# Development startup script for Cat Food Ingredient Researcher
# This script starts both backend and frontend in development mode

set -e  # Exit on error

echo "🐱 Cat Food Ingredient Researcher - Development Environment"
echo "==========================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables from .env file
echo -e "${BLUE}📋 Loading environment variables...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo ""
    echo "Please create one:"
    echo "  cp .env.development .env"
    echo "  # Then edit .env and add your API keys"
    echo ""
    exit 1
fi

# Export environment variables for docker-compose and application
set -a  # Automatically export all variables
source .env
set +a  # Stop automatically exporting

echo -e "${GREEN}✓ Environment variables loaded${NC}"
echo ""

# Validate required environment variables
REQUIRED_VARS=("POSTGRES_PASSWORD" "SECRET_KEY" "GEMINI_API_KEY")
MISSING_VARS=()

for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        MISSING_VARS+=("$VAR")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing required environment variables:${NC}"
    for VAR in "${MISSING_VARS[@]}"; do
        echo "   - $VAR"
    done
    echo ""
    echo "Please set these in your .env file"
    exit 1
fi

echo -e "${GREEN}✓ All required environment variables are set${NC}"
echo ""

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

# Check if Docker services are running
echo -e "${BLUE}🐳 Checking Docker services...${NC}"

if ! docker ps | grep -q cat_food_db; then
    echo -e "${YELLOW}⚠️  PostgreSQL container not running${NC}"
    echo "Starting Docker services..."
    docker-compose up -d
    echo -e "${GREEN}✓ Docker services started${NC}"
    echo "Waiting for database to be ready..."
    sleep 5
else
    echo -e "${GREEN}✓ Docker services are running${NC}"
fi

echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${BLUE}🛑 Shutting down services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${YELLOW}Note: Docker services are still running. To stop them, run: docker-compose down${NC}"
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
echo "   🐳 PostgreSQL: localhost:${POSTGRES_PORT:-5433}"
echo "   🐳 Qdrant:     localhost:${QDRANT_PORT:-6333}"
echo "   🔧 Backend:    http://localhost:8000"
echo "   📚 API Docs:   http://localhost:8000/docs"
echo "   🎨 Frontend:   http://localhost:3000"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo "   Docker:   docker-compose logs -f"
echo ""
echo -e "${BLUE}🛑 Stopping Services:${NC}"
echo "   Press Ctrl+C to stop backend and frontend"
echo "   Run 'docker-compose down' to stop Docker services"
echo "==========================================================="
echo ""

# Wait for user interrupt
wait
