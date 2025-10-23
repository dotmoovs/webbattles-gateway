#!/bin/bash

echo "=========================================="
echo "  Starting SATP Gateway for Testnets"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ ERROR: Docker is not running!"
    echo ""
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start the gateway
echo "Starting gateway..."
docker compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Gateway started successfully!"
    echo ""
    echo "Waiting for gateway to be ready..."
    
    # Wait for gateway to be ready
    for i in {1..30}; do
        if curl -s http://localhost:4010/api/v1/api-docs > /dev/null 2>&1; then
            echo "✅ Gateway is ready!"
            echo ""
            echo "You can now run the testnet demo:"
            echo "  cd webbattles"
            echo "  python3 run-full-testnet-demo.py"
            echo ""
            echo "To check gateway logs:"
            echo "  docker compose logs -f"
            echo ""
            exit 0
        fi
        sleep 2
        echo "  Waiting... ($i/30)"
    done
    
    echo "⚠️  Gateway started but not responding yet"
    echo "Check logs with: docker compose logs -f"
else
    echo "❌ Failed to start gateway"
    exit 1
fi

