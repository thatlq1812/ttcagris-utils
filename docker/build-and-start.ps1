# =============================================================================
# AgriOS Dev Environment - Build and Start Script (Windows PowerShell)
# =============================================================================
# Usage: .\docker\build-and-start.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host "AgriOS Dev Environment - Build & Start"
Write-Host "=========================================="

# Save current location
$rootDir = Get-Location

# Set Go environment for Linux build
Write-Host ""
Write-Host "[1/5] Setting Go environment for Linux build..."
$env:CGO_ENABLED = "0"
$env:GOOS = "linux"
$env:GOARCH = "amd64"

# Build CAS
Write-Host ""
Write-Host "[2/5] Building CAS binary..."
Set-Location "$rootDir\centre-auth-service"

if (-not (Test-Path "bin")) {
    New-Item -ItemType Directory -Path "bin" | Out-Null
}

go build -o bin/cas-linux ./cmd/app/
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build CAS" -ForegroundColor Red
    Set-Location $rootDir
    exit 1
}
Write-Host "  CAS binary built: bin/cas-linux" -ForegroundColor Green

# Build Noti-Service
Write-Host ""
Write-Host "[3/5] Building Noti-Service binary..."
Set-Location "$rootDir\noti-service"

if (-not (Test-Path "bin")) {
    New-Item -ItemType Directory -Path "bin" | Out-Null
}

go build -o bin/noti-linux ./cmd/main.go
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build Noti-Service" -ForegroundColor Red
    Set-Location $rootDir
    exit 1
}
Write-Host "  Noti-Service binary built: bin/noti-linux" -ForegroundColor Green

# Return to root
Set-Location $rootDir

# Check FCM credentials
Write-Host ""
Write-Host "[4/5] Checking FCM credentials..."
$fcmPath = "$rootDir\noti-service\config\fcm-dev-sdk.json"
if (-not (Test-Path $fcmPath)) {
    Write-Host "WARNING: FCM credentials not found at: $fcmPath" -ForegroundColor Yellow
    Write-Host "         Please download from Firebase Console and place at:" -ForegroundColor Yellow
    Write-Host "         noti-service/config/fcm-dev-sdk.json" -ForegroundColor Yellow
} else {
    Write-Host "  FCM credentials found" -ForegroundColor Green
}

# Start Docker services
Write-Host ""
Write-Host "[5/5] Starting Docker services..."
docker compose -f docker/docker-compose.dev.yml up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start Docker services" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Waiting for services to be healthy..."
Write-Host "=========================================="
Start-Sleep -Seconds 20

# Check status
Write-Host ""
docker compose -f docker/docker-compose.dev.yml ps

Write-Host ""
Write-Host "=========================================="
Write-Host "Services Started Successfully!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Service Ports:"
Write-Host "  PostgreSQL:    localhost:5432"
Write-Host "  Redis:         localhost:6379"
Write-Host "  CAS gRPC:      localhost:50051"
Write-Host "  CAS HTTP:      localhost:4000"
Write-Host "  Noti gRPC:     localhost:9012"
Write-Host "  Noti HTTP:     localhost:8000"
Write-Host ""
Write-Host "Quick Test Commands:"
Write-Host "  grpcurl -plaintext localhost:9012 list"
Write-Host "  grpcurl -plaintext localhost:50051 list"
Write-Host ""
Write-Host "View Logs:"
Write-Host "  docker compose -f docker/docker-compose.dev.yml logs -f"
Write-Host ""
Write-Host "IMPORTANT: Update FCM token in database before testing!"
Write-Host "  docker exec -it agrios_dev_postgres psql -U postgres -d centre_auth"
Write-Host "  UPDATE device_sessions SET firebase_token = 'YOUR_TOKEN' WHERE account_id = 999;"
Write-Host ""
