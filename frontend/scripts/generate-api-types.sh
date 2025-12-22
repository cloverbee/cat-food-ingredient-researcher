#!/bin/bash

# Generate TypeScript types from OpenAPI schema
echo "🚀 Generating API types from OpenAPI schema..."

# Check if backend is running
if ! curl -s http://localhost:8000/openapi.json > /dev/null 2>&1; then
    echo "❌ Backend is not running on localhost:8000"
    echo "Please start the backend server first: uvicorn src.api.main:app --reload --port 8000"
    exit 1
fi

# Fetch OpenAPI schema
echo "📥 Fetching OpenAPI schema..."
curl -s http://localhost:8000/openapi.json -o ./openapi.json

# Check if openapi.json was downloaded successfully
if [ ! -f "./openapi.json" ]; then
    echo "❌ Failed to download openapi.json"
    exit 1
fi

# Generate TypeScript types
echo "🔧 Generating TypeScript types..."
npx openapi-typescript ./openapi.json -o ./lib/api-types.ts

echo "✅ API types generated successfully!"
echo "📋 Types are available in ./lib/api-types.ts"

# Show available endpoints
echo ""
echo "📡 Available API endpoints:"
cat ./openapi.json | jq -r '.paths | keys[]'


