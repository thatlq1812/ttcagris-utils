# Centre Auth Service - Deployment Guide

**Author:** thatlq1812  
**Created:** 2025-12-18  
**Last Updated:** 2025-12-18  
**Version:** 1.0.0  
**Status:** Active

---

## Overview

This guide covers deployment procedures for Centre Auth Service across different environments: development, UAT, and production.

**Deployment Methods:**
- Local development with Docker Compose
- Kubernetes deployment via Helm
- CI/CD with Azure Pipelines
- Manual deployment with Docker

---

## Prerequisites

### Required Software

**Local Development:**
- Go 1.21+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose
- Make

**Production Deployment:**
- Docker
- Kubernetes cluster (AWS EKS recommended)
- kubectl
- Helm 3+
- AWS CLI (for ECR)

### Required Access

- Azure DevOps repository access
- AWS ECR credentials (production)
- Kubernetes cluster access (kubectl config)
- Database credentials
- Vault access (optional, for secrets)

---

## Environment Configuration

### Development Environment

**File:** `config/config.yaml`

```yaml
server:
  name: "centre-auth-service"
  port: "4000"
  env: "development"
  debug: true

grpc:
  enabled: true
  port: 50051

database:
  host: "localhost"
  port: 5432
  username: "postgres"
  password: "postgres"
  database: "centre_auth"
  schema: "public"
  ssl_mode: "disable"
  max_open_conns: 25
  max_idle_conns: 5
  conn_max_lifetime: 5m

cache:
  redis:
    mode: "standalone"
    address:
      - "localhost:6379"
    username: ""
    password: ""
    db: 0
    pool_size: 10

jwt:
  secret_key_web: "dev-secret-web-key-change-in-production"
  secret_key_app: "dev-secret-app-key-change-in-production"
  access_token_duration: 15m
  refresh_token_duration: 168h

otp:
  expire_seconds: 120
  max_per_day: 5
  cooldown_seconds: 120
  verified_grace_seconds: 180

telemetry:
  enabled: true
  service_name: "centre-auth-service"
  exporter_type: "otlp-http"
  otlp_endpoint: "localhost:4318"
  sampling_ratio: 1.0

telegram:
  enabled: true
  bot_token: "YOUR_TELEGRAM_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"

services:
  notification: "localhost:9100"
```

---

### UAT Environment

**File:** `config/config.uat.yaml`

```yaml
server:
  name: "centre-auth-service"
  port: "4000"
  env: "uat"
  debug: false

grpc:
  enabled: true
  port: 50051

database:
  host: "uat-postgres.example.com"
  port: 5432
  username: "cas_user"
  password: "${DB_PASSWORD}"  # From environment
  database: "centre_auth_uat"
  schema: "public"
  ssl_mode: "require"
  max_open_conns: 50
  max_idle_conns: 10
  conn_max_lifetime: 10m

cache:
  redis:
    mode: "standalone"
    address:
      - "uat-redis.example.com:6379"
    password: "${REDIS_PASSWORD}"
    db: 0
    pool_size: 20

jwt:
  secret_key_web: "${JWT_SECRET_WEB}"
  secret_key_app: "${JWT_SECRET_APP}"
  access_token_duration: 15m
  refresh_token_duration: 168h

vault:
  enabled: true
  address: "https://vault.example.com"
  token: "${VAULT_TOKEN}"
  path: "secret/data/cas/uat"

telemetry:
  enabled: true
  service_name: "centre-auth-service-uat"
  exporter_type: "otlp-http"
  otlp_endpoint: "otel-collector.example.com:4318"
  sampling_ratio: 0.1
```

---

### Production Environment

**File:** `config/config.production.yaml`

```yaml
server:
  name: "centre-auth-service"
  port: "4000"
  env: "production"
  debug: false

grpc:
  enabled: true
  port: 50051
  max_concurrent_streams: 1000

database:
  host: "${DB_HOST}"
  port: 5432
  username: "${DB_USERNAME}"
  password: "${DB_PASSWORD}"
  database: "centre_auth_prod"
  schema: "public"
  ssl_mode: "require"
  max_open_conns: 100
  max_idle_conns: 20
  conn_max_lifetime: 15m

cache:
  redis:
    mode: "cluster"
    address:
      - "redis-node-1.example.com:6379"
      - "redis-node-2.example.com:6379"
      - "redis-node-3.example.com:6379"
    password: "${REDIS_PASSWORD}"
    db: 0
    pool_size: 50

jwt:
  secret_key_web: "${JWT_SECRET_WEB}"
  secret_key_app: "${JWT_SECRET_APP}"
  access_token_duration: 15m
  refresh_token_duration: 168h

vault:
  enabled: true
  address: "${VAULT_ADDR}"
  token: "${VAULT_TOKEN}"
  path: "secret/data/cas/prod"

telemetry:
  enabled: true
  service_name: "centre-auth-service-prod"
  exporter_type: "otlp-http"
  otlp_endpoint: "${OTEL_ENDPOINT}"
  sampling_ratio: 0.01  # 1% sampling in prod

telegram:
  enabled: false  # Disable in production

services:
  notification: "notification-service.default.svc.cluster.local:9100"
```

---

## Local Development Deployment

### Option 1: Direct Run

```bash
# 1. Start PostgreSQL
docker run -d \
  --name cas-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=centre_auth \
  -p 5432:5432 \
  postgres:14

# 2. Start Redis
docker run -d \
  --name cas-redis \
  -p 6379:6379 \
  redis:7

# 3. Configure service
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your settings

# 4. Run database migrations (auto-runs on startup)
# Migrations in migrations/ folder run automatically

# 5. Start service
make api
# Or: go run cmd/app/main.go api

# Service will start on:
# - HTTP: http://localhost:4000
# - gRPC: localhost:50051
```

---

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: cas-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: centre_auth
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: cas-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  cas:
    build:
      context: .
      dockerfile: Dockerfile
      secrets:
        - git_token
    container_name: cas-service
    ports:
      - "4000:4000"   # HTTP
      - "50051:50051" # gRPC
    environment:
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_USERNAME: postgres
      DATABASE_PASSWORD: postgres
      DATABASE_NAME: centre_auth
      REDIS_ADDRESS: redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./config:/app/config
    restart: unless-stopped

volumes:
  postgres_data:

secrets:
  git_token:
    file: ./.secrets/git_token.txt
```

Start services:

```bash
# Create secrets file
mkdir -p .secrets
echo "YOUR_AZURE_PAT_TOKEN" > .secrets/git_token.txt

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f cas

# Stop services
docker-compose down
```

---

## Docker Build

### Build Docker Image

```bash
# Create git token secret
echo "YOUR_AZURE_PAT_TOKEN" > .secrets/git_token.txt

# Build with BuildKit
DOCKER_BUILDKIT=1 docker build \
  --secret id=git_token,src=.secrets/git_token.txt \
  --build-arg CACHE_BUST=$(date +%s) \
  -t centre-auth-service:latest \
  .

# Test image
docker run -d \
  --name cas-test \
  -p 4000:4000 \
  -p 50051:50051 \
  -e DATABASE_HOST=host.docker.internal \
  -e DATABASE_PASSWORD=postgres \
  -e REDIS_ADDRESS=host.docker.internal:6379 \
  centre-auth-service:latest

# Check logs
docker logs -f cas-test
```

### Multi-stage Dockerfile

The service uses a multi-stage Dockerfile for optimal image size:

**Stage 1: Builder**
- Base: `golang:1.25.5-alpine`
- Installs build dependencies
- Downloads Go modules with Azure DevOps authentication
- Compiles application binary

**Stage 2: Runtime**
- Base: `alpine:3.18`
- Minimal runtime dependencies
- Copies binary from builder
- Runs as non-root user
- Final image size: ~30MB

---

## CI/CD with Azure Pipelines

### Pipeline Configuration

The service uses Azure Pipelines for automated builds and deployments.

**File:** `azure-pipelines.yml`

**Branch Strategy:**
- `main` → Development environment
- `uat` → UAT environment
- `release` → Production environment
- `testing` → Testing environment

**Pipeline Stages:**

1. **Build Stage:**
   - Detect environment from branch
   - Clean Docker and Go caches
   - Build Docker image with secrets
   - Tag with environment and commit SHA
   - Push to AWS ECR

2. **Deploy Stage (Auto-triggered):**
   - Pull image from ECR
   - Apply Kubernetes manifests
   - Update deployment with new image
   - Verify deployment health

### Pipeline Variables

Configure in Azure DevOps Library group `CICD`:

```yaml
# AWS Credentials
AWS_ACCESS_KEY_ID: "your-access-key"
AWS_SECRET_ACCESS_KEY: "your-secret-key"
AWS_REGION: "ap-southeast-1"

# Git Authentication
GIT_TOKEN: "your-azure-pat-token"

# Docker Registry
ECR_REPO: "339935009501.dkr.ecr.ap-southeast-1.amazonaws.com/centre-auth-service"

# Kubernetes
K8S_NAMESPACE: "default"
K8S_DEPLOYMENT_NAME: "centre-auth-service"
```

### Trigger Build

```bash
# Push to main (deploys to dev)
git push origin main

# Push to uat (deploys to uat)
git checkout uat
git merge main
git push origin uat

# Push to release (deploys to prod)
git checkout release
git merge uat
git push origin release
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Configure kubectl
aws eks update-kubeconfig --region ap-southeast-1 --name your-cluster

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Kubernetes Manifests

**Deployment:** `k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: centre-auth-service
  namespace: default
  labels:
    app: centre-auth-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: centre-auth-service
  template:
    metadata:
      labels:
        app: centre-auth-service
    spec:
      containers:
      - name: cas
        image: 339935009501.dkr.ecr.ap-southeast-1.amazonaws.com/centre-auth-service:prod-latest
        ports:
        - containerPort: 4000
          name: http
          protocol: TCP
        - containerPort: 50051
          name: grpc
          protocol: TCP
        env:
        - name: DATABASE_HOST
          valueFrom:
            secretKeyRef:
              name: cas-secrets
              key: db-host
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: cas-secrets
              key: db-password
        - name: REDIS_ADDRESS
          valueFrom:
            configMapKeyRef:
              name: cas-config
              key: redis-address
        - name: JWT_SECRET_WEB
          valueFrom:
            secretKeyRef:
              name: cas-secrets
              key: jwt-secret-web
        - name: JWT_SECRET_APP
          valueFrom:
            secretKeyRef:
              name: cas-secrets
              key: jwt-secret-app
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          tcpSocket:
            port: 4000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          tcpSocket:
            port: 50051
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: cas-config
      imagePullSecrets:
      - name: ecr-registry-secret
```

**Service:** `k8s/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: centre-auth-service
  namespace: default
  labels:
    app: centre-auth-service
spec:
  type: ClusterIP
  ports:
  - port: 4000
    targetPort: 4000
    name: http
    protocol: TCP
  - port: 50051
    targetPort: 50051
    name: grpc
    protocol: TCP
  selector:
    app: centre-auth-service
```

**ConfigMap:** `k8s/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cas-config
  namespace: default
data:
  redis-address: "redis-cluster.default.svc.cluster.local:6379"
  otel-endpoint: "otel-collector.observability.svc.cluster.local:4318"
  notification-service: "notification-service.default.svc.cluster.local:9100"
  config.yaml: |
    server:
      name: "centre-auth-service"
      port: "4000"
      env: "production"
    grpc:
      enabled: true
      port: 50051
    telemetry:
      enabled: true
      service_name: "centre-auth-service-prod"
```

**Secret:** `k8s/secret.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cas-secrets
  namespace: default
type: Opaque
data:
  db-host: cG9zdGdyZXMtcHJvZC5leGFtcGxlLmNvbQ==  # base64 encoded
  db-password: c2VjdXJlUGFzc3dvcmQxMjM=           # base64 encoded
  jwt-secret-web: d2ViLXNlY3JldC1rZXk=            # base64 encoded
  jwt-secret-app: YXBwLXNlY3JldC1rZXk=            # base64 encoded
```

### Deploy to Kubernetes

```bash
# Create namespace (if needed)
kubectl create namespace default

# Create secrets
echo -n 'postgres-prod.example.com' | base64
kubectl create secret generic cas-secrets \
  --from-literal=db-host='postgres-prod.example.com' \
  --from-literal=db-password='SecurePassword123' \
  --from-literal=jwt-secret-web='web-secret-key' \
  --from-literal=jwt-secret-app='app-secret-key'

# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Apply Service
kubectl apply -f k8s/service.yaml

# Apply Deployment
kubectl apply -f k8s/deployment.yaml

# Check rollout status
kubectl rollout status deployment/centre-auth-service

# Verify pods
kubectl get pods -l app=centre-auth-service

# Check logs
kubectl logs -l app=centre-auth-service -f

# Get service endpoint
kubectl get svc centre-auth-service
```

### Update Deployment

```bash
# Update image
kubectl set image deployment/centre-auth-service \
  cas=339935009501.dkr.ecr.ap-southeast-1.amazonaws.com/centre-auth-service:prod-v2.0.0

# Or apply updated manifest
kubectl apply -f k8s/deployment.yaml

# Watch rollout
kubectl rollout status deployment/centre-auth-service

# Rollback if needed
kubectl rollout undo deployment/centre-auth-service
```

---

## Database Migration

### Auto-migration on Startup

The service automatically runs migrations on startup:

```go
// internal/api/init.go
func RunMigrations(db *gorm.DB) error {
    // Auto-runs all .sql files in migrations/ folder
    // Migrations are tracked in schema_migrations table
}
```

**Migration Files:** `migrations/*.sql`

Migrations run in numerical order:
- 001_create_users_table.sql
- 002_create_accounts_table.sql
- ...
- 070_add_action_by_to_audit_logs.sql

### Manual Migration

```bash
# Run migrations manually (if needed)
psql -U postgres -d centre_auth -f migrations/001_create_users_table.sql

# Check migration status
psql -U postgres -d centre_auth -c "SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 10;"
```

---

## Monitoring & Health Checks

### Health Endpoints

```bash
# Check HTTP health (if implemented)
curl http://localhost:4000/health

# Check gRPC with grpcurl
grpcurl -plaintext localhost:50051 list

# Check database connection
psql -U postgres -h localhost -d centre_auth -c "SELECT 1"

# Check Redis connection
redis-cli -h localhost ping
```

### Prometheus Metrics

Metrics exposed at `/metrics` (if implemented):

```bash
curl http://localhost:4000/metrics
```

**Key Metrics:**
- `grpc_server_handled_total` - Total gRPC requests
- `http_requests_total` - Total HTTP requests
- `database_connections_open` - Active DB connections
- `cache_hits_total` - Redis cache hits
- `jwt_token_validations_total` - Token validations

### OpenTelemetry Tracing

Traces sent to OTLP endpoint configured in `telemetry.otlp_endpoint`.

View traces in Jaeger or other OTLP-compatible backend.

---

## Backup & Restore

### Database Backup

```bash
# Full backup
pg_dump -U postgres -h localhost -d centre_auth \
  -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# Schema only
pg_dump -U postgres -h localhost -d centre_auth \
  -s -f schema_$(date +%Y%m%d).sql

# Data only
pg_dump -U postgres -h localhost -d centre_auth \
  -a -f data_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U postgres -h localhost -d centre_auth | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Database Restore

```bash
# Restore from custom format
pg_restore -U postgres -h localhost -d centre_auth_new backup_20251218.dump

# Restore from SQL
psql -U postgres -h localhost -d centre_auth_new < backup_20251218.sql

# Restore from compressed
gunzip -c backup_20251218.sql.gz | psql -U postgres -h localhost -d centre_auth_new
```

### Automated Backups

**Kubernetes CronJob:** `k8s/backup-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cas-db-backup
  namespace: default
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:14
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h $DB_HOST -U $DB_USER -d centre_auth -F c | \
              aws s3 cp - s3://backups/cas/backup-$(date +%Y%m%d).dump
            env:
            - name: DB_HOST
              value: "postgres-prod.example.com"
            - name: DB_USER
              value: "postgres"
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: cas-secrets
                  key: db-password
          restartPolicy: OnFailure
```

---

## Troubleshooting

### Common Issues

**Issue:** Service fails to start  
**Check:**
```bash
# Check logs
docker logs cas-service
kubectl logs -l app=centre-auth-service

# Verify database connection
psql -U postgres -h localhost -d centre_auth -c "SELECT 1"

# Verify Redis connection
redis-cli -h localhost ping
```

**Issue:** Database migration fails  
**Solution:**
```bash
# Check migration status
psql -U postgres -d centre_auth -c "SELECT * FROM schema_migrations;"

# Manually fix migration and rerun
psql -U postgres -d centre_auth -f migrations/XXX_fix.sql
```

**Issue:** gRPC connection refused  
**Check:**
```bash
# Verify gRPC port
netstat -tulpn | grep 50051

# Test with grpcurl
grpcurl -plaintext localhost:50051 list
```

**Issue:** High memory usage  
**Solution:**
```bash
# Check database connection pool
# Reduce max_open_conns in config

# Check for memory leaks
go tool pprof http://localhost:4000/debug/pprof/heap
```

---

## Rollback Procedures

### Kubernetes Rollback

```bash
# View rollout history
kubectl rollout history deployment/centre-auth-service

# Rollback to previous version
kubectl rollout undo deployment/centre-auth-service

# Rollback to specific revision
kubectl rollout undo deployment/centre-auth-service --to-revision=3

# Verify rollback
kubectl rollout status deployment/centre-auth-service
```

### Docker Rollback

```bash
# Pull previous image
docker pull centre-auth-service:previous-tag

# Stop current container
docker stop cas-service

# Start previous version
docker run -d \
  --name cas-service \
  -p 4000:4000 \
  -p 50051:50051 \
  centre-auth-service:previous-tag
```

---

## Security Checklist

Before production deployment:

- [ ] Change all default passwords
- [ ] Generate secure JWT secret keys (min 32 characters)
- [ ] Enable SSL/TLS for PostgreSQL
- [ ] Enable SSL/TLS for Redis
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Enable Vault for secret management
- [ ] Rotate JWT secrets regularly (every 90 days)
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Enable automatic backups
- [ ] Test disaster recovery procedures
- [ ] Review Casbin policies
- [ ] Disable debug mode (`debug: false`)
- [ ] Disable Telegram bot in production
- [ ] Enable CORS restrictions in API Gateway
- [ ] Set proper resource limits in Kubernetes

---

## Performance Tuning

### Database Optimization

```yaml
database:
  max_open_conns: 100      # Increase for high load
  max_idle_conns: 20       # Keep connections ready
  conn_max_lifetime: 15m   # Rotate connections
```

### Redis Optimization

```yaml
cache:
  redis:
    pool_size: 50          # Connection pool size
    min_idle_conns: 10     # Minimum idle connections
```

### gRPC Optimization

```yaml
grpc:
  max_concurrent_streams: 1000  # Max concurrent requests
  keepalive_time: 10s
  keepalive_timeout: 3s
```

---

## Navigation

### Documentation Home
- [Back to README](../../README.md) - Main documentation hub

### Related Documentation
- [Architecture Overview](../architecture/overview.md) - System design and components
- [API Reference](../api/api_reference.md) - Complete API documentation
- [Database Schema](../database/schema.md) - Data models and relationships
- [Testing Guide](testing_guide.md) - Testing procedures

### Project Documentation
- [CHANGELOG](../../CHANGELOG.md) - Version history and updates
- [Port Allocation](../../../docs/PORT_ALLOCATION.md) - System-wide port assignments

**Version**: 1.0.0 | [Back to Top](#centre-auth-service-deployment-guide)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-18 | Initial deployment guide with comprehensive procedures |
