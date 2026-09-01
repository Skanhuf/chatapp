#!/bin/bash

========================================
🚀 ChatApp Deploy Script
========================================

# Configuration
PROJECT_DIR="/home/shogan/ChatAPP"
COMPOSE_FILE="docker-compose.yml"

echo "========================================"
echo "🚀 ChatApp Deploy Script"
echo "========================================"

# Step 1: Pull latest changes
echo ""
echo "[1/4] Pulling latest changes from git..."
cd "$PROJECT_DIR" || { echo "❌ Error: Directory $PROJECT_DIR not found"; exit 1; }
git pull origin main

# Step 2: Build and start services
echo ""
echo "[2/4] Building and starting services..."
docker-compose -f "$COMPOSE_FILE" up --build -d

# Step 3: Check service health
echo ""
echo "[3/4] Checking service health..."
sleep 10

# Check if containers are running
CONTAINERS=$(docker-compose -f "$COMPOSE_FILE" ps --services --filter "status=running" 2>/dev/null | wc -l)
TOTAL_SERVICES=$(docker-compose -f "$COMPOSE_FILE" config --services 2>/dev/null | wc -l)

if [ "$CONTAINERS" -eq "$TOTAL_SERVICES" ]; then
    echo "✅ All $CONTAINERS services are running"
else
    echo "⚠️  Warning: Only $CONTAINERS/$TOTAL_SERVICES services are running"
    echo ""
    echo "Container status:"
    docker-compose -f "$COMPOSE_FILE" ps
fi

# Step 4: Show logs (last 20 lines)
echo ""
echo "[4/4] Recent logs:"
echo "---"
docker-compose -f "$COMPOSE_FILE" logs --tail=20

echo ""
echo "========================================"
echo "✅ Deployment complete!"
echo "========================================"
echo ""
echo "Access the app at: http://localhost:8081"
echo ""
echo "Useful commands:"
echo "  View logs:     docker-compose -f $COMPOSE_FILE logs -f"
echo "  Restart:       docker-compose -f $COMPOSE_FILE restart"
echo "  Stop:          docker-compose -f $COMPOSE_FILE down"
echo "  Rebuild:       docker-compose -f $COMPOSE_FILE up --build -d"
