#!/bin/bash

# Backend-only development startup script for Cat Food Ingredient Researcher
# Starts Docker services (Postgres + Qdrant) and the FastAPI backend.

set -e  # Exit on error

echo "🐱 Cat Food Ingredient Researcher - Backend Dev"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Loading environment variables...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo ""
    echo "Please create one:"
    echo "  cp .env.development .env"
    echo "  # Then edit .env (POSTGRES_PASSWORD is required)"
    echo ""
    exit 1
fi

# Export environment variables for docker-compose and application
set -a
source .env
set +a

echo -e "${GREEN}✓ Environment variables loaded${NC}"
echo ""

# Validate required environment variables
REQUIRED_VARS=("POSTGRES_PASSWORD")
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

echo -e "${GREEN}✓ Required environment variables are set${NC}"
echo ""

if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please create one with: python -m venv .venv"
    exit 1
fi

echo -e "${BLUE}🐳 Starting Docker services (Postgres + Qdrant)...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Docker services started${NC}"
echo ""

echo -e "${BLUE}🗄️  Running migrations...${NC}"
source .venv/bin/activate
alembic upgrade head
echo -e "${GREEN}✓ Migrations applied${NC}"
echo ""

echo -e "${GREEN}🚀 Starting Backend (FastAPI)...${NC}"
echo "   Backend will be available at: http://localhost:8000"
echo "   API docs at:               http://localhost:8000/docs"
echo ""

mkdir -p logs
exec python -m uvicorn src.api.main:app --reload --port 8000
