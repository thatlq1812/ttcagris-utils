#!/bin/bash
# =============================================================================
# AgriOS Dev Environment - Build and Start Script (Linux/macOS)
# =============================================================================
# Usage: ./docker/build-and-start.sh
# =============================================================================

set -e

echo "=========================================="
echo "AgriOS Dev Environment - Build & Start"
echo "=========================================="

# Get script directory and root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Set Go environment for Linux build
echo ""
echo "[1/5] Setting Go environment for Linux build..."
export CGO_ENABLED=0
export GOOS=linux
export GOARCH=amd64

# Build CAS
echo ""
echo "[2/5] Building CAS binary..."
mkdir -p centre-auth-service/bin
go build -o centre-auth-service/bin/cas-linux ./centre-auth-service/cmd/app/
echo "  CAS binary built: centre-auth-service/bin/cas-linux"

# Build Noti-Service
echo ""
echo "[3/5] Building Noti-Service binary..."
mkdir -p noti-service/bin
go build -o noti-service/bin/noti-linux ./noti-service/cmd/main.go
echo "  Noti-Service binary built: noti-service/bin/noti-linux"

# Check FCM credentials
echo ""
echo "[4/5] Checking FCM credentials..."
FCM_PATH="$ROOT_DIR/noti-service/config/fcm-dev-sdk.json"
if [ ! -f "$FCM_PATH" ]; then
    echo "WARNING: FCM credentials not found at: $FCM_PATH"
    echo "         Please download from Firebase Console and place at:"
    echo "         noti-service/config/fcm-dev-sdk.json"
else
    echo "  FCM credentials found"
fi

# Start Docker services
echo ""
echo "[5/5] Starting Docker services..."
docker compose -f docker/docker-compose.dev.yml up -d --build

echo ""
echo "=========================================="
echo "Waiting for services to be healthy..."
echo "=========================================="
sleep 20

# Check status
echo ""
docker compose -f docker/docker-compose.dev.yml ps

echo ""
echo "=========================================="
echo "Services Started Successfully!"
echo "=========================================="
echo ""
echo "Service Ports:"
echo "  PostgreSQL:    localhost:5432"
echo "  Redis:         localhost:6379"
echo "  CAS gRPC:      localhost:50051"
echo "  CAS HTTP:      localhost:4000"
echo "  Noti gRPC:     localhost:9012"
echo "  Noti HTTP:     localhost:8000"
echo ""
echo "Quick Test Commands:"
echo "  grpcurl -plaintext localhost:9012 list"
echo "  grpcurl -plaintext localhost:50051 list"
echo ""
echo "View Logs:"
echo "  docker compose -f docker/docker-compose.dev.yml logs -f"
echo ""
echo "IMPORTANT: Update FCM token in database before testing!"
echo "  docker exec -it agrios_dev_postgres psql -U postgres -d centre_auth"
echo "  UPDATE device_sessions SET firebase_token = 'YOUR_TOKEN' WHERE account_id = 999;"
echo ""
