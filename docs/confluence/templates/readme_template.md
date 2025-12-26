# [Service/Library Name]

Brief one-line description of what this service/library does.

---

## Overview

**Purpose**: Explain the main purpose and business value of this service.

**Key Features**:
- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

**Architecture**: Proto-first gRPC microservice following Clean Architecture with CQRS patterns.

---

## Quick Start

### Prerequisites

- Go 1.23+
- Docker & Docker Compose
- PostgreSQL 17+
- Redis 7+ (if applicable)
- Make

### Installation

```bash
# Clone repository
git clone https://dev.azure.com/agris-agriculture/Core/_git/[service-name]
cd [service-name]

# Install dependencies
go mod download

# Setup configuration
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings

# Run database migrations
make migrate-up

# Run service
make api
```

Service will start on configured port (default: [port]).

---

## Configuration

Configuration is managed via `config/config.yaml` with environment variable overrides.

### config.yaml Structure

```yaml
server:
  port: 8080
  host: "0.0.0.0"
  timeout: 30s

database:
  host: localhost
  port: 5432
  name: database_name
  user: postgres
  password: postgres
  sslmode: disable
  maxOpenConns: 25
  maxIdleConns: 5

services:
  auth:
    grpcAddr: "localhost:50051"
  notification:
    grpcAddr: "localhost:9012"

logging:
  level: info
  format: json
```

### Environment Variables

Override config values with environment variables:
```bash
export SERVER_PORT=9000
export DATABASE_HOST=prod-db.example.com
export LOG_LEVEL=debug
```

### Using .env File

For local development:
```bash
cp .env.example .env
# Edit .env with your values
```

**WARNING**: Never commit `.env` files with secrets to version control.

---

## Project Structure

```
.
├── cmd/                    # Application entry points
│   ├── api.go             # API server command
│   └── root.go            # Root command
├── config/                 # Configuration files
│   ├── config.go          # Config struct
│   └── config.yaml        # YAML configuration
├── internal/               # Private application code
│   ├── entities/          # Domain models (DB tables)
│   ├── dtos/              # Data Transfer Objects
│   ├── application/       # Business logic (CQRS)
│   │   ├── command/       # Write operations
│   │   └── query/         # Read operations
│   ├── handler/           # HTTP/gRPC handlers
│   ├── infras/
│   │   ├── repository/    # Data access layer
│   │   └── adapter/       # External service clients
│   └── middleware/        # HTTP/gRPC middleware
├── pkg/                    # Public reusable packages
├── migrations/             # Database migration files
├── proto/                  # Protocol buffer definitions (if any)
├── vendor/                 # Vendored dependencies
├── Makefile               # Build automation
├── go.mod                 # Go module definition
└── README.md              # This file
```

### Clean Architecture Layers

```
┌─────────────────────────────────────┐
│        handler (Interface)          │
├─────────────────────────────────────┤
│    application (Business Logic)     │
│      - command/ (Write)              │
│      - query/ (Read)                 │
├─────────────────────────────────────┤
│        entities (Domain)             │
├─────────────────────────────────────┤
│         infras (Data)                │
│      - repository/                   │
│      - adapter/                      │
└─────────────────────────────────────┘
```

---

## API Documentation

### gRPC Services

**Service Definition**: [proto/[service]/v1/[service].proto](proto/[service]/v1/[service].proto)

**Available Methods**:
```protobuf
service [ServiceName] {
  rpc Create[Resource](Create[Resource]Request) returns ([Resource]);
  rpc Get[Resource](Get[Resource]Request) returns ([Resource]);
  rpc Update[Resource](Update[Resource]Request) returns ([Resource]);
  rpc Delete[Resource](Delete[Resource]Request) returns (google.protobuf.Empty);
  rpc List[Resources](List[Resources]Request) returns (List[Resources]Response);
}
```

### REST API (if exposed via gateway)

See [API Gateway Documentation](../app-api-gateway/README.md) for REST endpoints.

**Example Endpoints**:
- `POST /api/v1/[resource]` - Create resource
- `GET /api/v1/[resource]/{id}` - Get resource by ID
- `PUT /api/v1/[resource]/{id}` - Update resource
- `DELETE /api/v1/[resource]/{id}` - Delete resource
- `GET /api/v1/[resources]` - List resources

### Testing with grpcurl

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Describe service
grpcurl -plaintext localhost:50051 describe [package].[ServiceName]

# Call method
grpcurl -plaintext -d '{
  "field1": "value1",
  "field2": "value2"
}' localhost:50051 [package].[ServiceName]/[MethodName]
```

---

## Development

### Makefile Commands

```bash
make api              # Run service locally
make build            # Build binary to bin/
make test             # Run unit tests
make test-coverage    # Run tests with coverage report
make lint             # Run golangci-lint
make fmt              # Format code
make migrate-up       # Apply database migrations
make migrate-down     # Rollback last migration
make docker-build     # Build Docker image
make docker-run       # Run Docker container
```

### Adding New Features

#### 1. Define Proto (if adding gRPC method)

```bash
cd ../Core
# Edit proto files
make generate
# Push to Core repo
```

#### 2. Update Service

```bash
# Update Core dependency
make update-core

# Or use local Core for development
make use-local-core CORE_PATH=../Core
```

#### 3. Implement Business Logic

Following CQRS pattern:

**Command (Write Operation)**:
```go
// internal/application/[domain]/command/create_[resource]_cmd.go
type Create[Resource]Command struct {
    // fields
}

func (c *Create[Resource]Command) Execute(ctx context.Context) (*entities.[Resource], error) {
    // validation
    // business logic
    // repository call
}
```

**Query (Read Operation)**:
```go
// internal/application/[domain]/query/get_[resource]_qry.go
type Get[Resource]Query struct {
    ID string
}

func (q *Get[Resource]Query) Execute(ctx context.Context) (*entities.[Resource], error) {
    // repository call
    // data transformation
}
```

#### 4. Add Handler

```go
// internal/handler/[resource]_handler.go
func (h *[Resource]Handler) Create[Resource](ctx context.Context, req *pb.Create[Resource]Request) (*pb.[Resource], error) {
    cmd := &command.Create[Resource]Command{
        // map request to command
    }
    result, err := cmd.Execute(ctx)
    // handle error
    // map result to response
}
```

#### 5. Add Tests

```bash
# Create test file
touch internal/application/[domain]/command/create_[resource]_cmd_test.go

# Run tests
make test
```

---

## Database

### Migrations

Migrations are managed using [migration tool name].

**Create new migration**:
```bash
migrate create -ext sql -dir migrations -seq [migration_name]
```

**Apply migrations**:
```bash
make migrate-up
```

**Rollback migrations**:
```bash
make migrate-down
```

### Schema

See [migrations/](migrations/) directory for complete schema.

**Key Tables**:
- `[table1]`: Description
- `[table2]`: Description

---

## Deployment

### Docker

**Build image**:
```bash
make docker-build
```

**Run container**:
```bash
docker run -p [port]:[port] \
  -e DATABASE_HOST=host.docker.internal \
  -e DATABASE_PORT=5432 \
  [service-name]:latest
```

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes (via Helm)

See [azure-pipelines-helm](azure-pipelines-helm) for Helm chart configuration.

```bash
helm install [service-name] ./charts/[service-name] \
  --set image.tag=v1.0.0 \
  --set env.DATABASE_HOST=postgres-service
```

---

## Monitoring

### Health Checks

- **Liveness**: `GET /health/live` - Basic health check
- **Readiness**: `GET /health/ready` - Check dependencies (DB, Redis, etc.)

### Metrics

Prometheus metrics available at `/metrics`:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `grpc_requests_total` - Total gRPC requests
- `grpc_request_duration_seconds` - gRPC request duration
- `database_connections` - Active DB connections

### Logging

Structured logging using [aglog](https://dev.azure.com/agris-agriculture/Core/_git/library.git/go/aglog):

```go
aglog.Infow("message",
    "key1", value1,
    "key2", value2,
)
```

**Log Levels**:
- `ERROR`: System errors requiring attention
- `WARN`: Potential issues
- `INFO`: Normal operation events
- `DEBUG`: Detailed diagnostic information

---

## Testing

### Unit Tests

```bash
make test
```

### Integration Tests

```bash
# Start dependencies
docker-compose up -d postgres redis

# Run integration tests
go test -tags=integration ./...
```

### Load Testing

```bash
# Using k6
k6 run tests/load/[scenario].js
```

---

## Troubleshooting

### Common Issues

#### Service won't start

**Symptom**: Error binding to port
**Solution**: Check if port is already in use
```bash
# Windows
netstat -ano | findstr :[port]

# Linux/Mac
lsof -i :[port]
```

#### Database connection failed

**Symptom**: `connection refused` error
**Solution**: 
1. Verify PostgreSQL is running
2. Check `config.yaml` database settings
3. Ensure database exists: `createdb [database_name]`

#### Proto file not found

**Symptom**: Import errors for proto files
**Solution**: Update Core dependency
```bash
make update-core
go mod tidy
```

#### Hot reload not working

**Symptom**: Changes not reflected without restart
**Solution**: Check if Air is running correctly
```bash
# Restart with Air
air
```

### Support & On-call

#### Emergency Contacts

**Production Incidents** (Severity 1 - System Down):
- **On-call Engineer**: Check PagerDuty/OpsGenie rotation
- **Backup**: @Senior Engineer Name
- **Emergency Hotline**: [Phone/Slack Channel]

**Business Hours Support**:
- **Tech Lead**: @Tech Lead Name
- **DevOps Team**: @DevOps Channel
- **Backend Team**: @Backend Channel

#### Escalation Path

1. **Level 1**: On-call engineer (0-15 minutes)
2. **Level 2**: Tech Lead (15-30 minutes)
3. **Level 3**: Engineering Manager (30+ minutes)

#### Incident Response

**For Production Incidents**:
1. Check monitoring dashboards: [Grafana/DataDog URL]
2. Review recent deployments: `git log --oneline -10`
3. Check service logs: `kubectl logs -f [pod-name]`
4. Create incident ticket: [Jira/ServiceNow]
5. Notify stakeholders in #incidents channel

**Common Emergency Scenarios**:
- **Database down**: Contact DBA team immediately
- **High CPU/Memory**: Check for memory leaks, restart pod
- **API rate limit exceeded**: Review traffic patterns, enable throttling

---

## Contributing

### Code Style

- Follow [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- Run `make lint` before committing
- Use meaningful variable names
- Write clear comments for exported functions

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add user authentication
fix: resolve database connection timeout
docs: update API documentation
refactor: simplify error handling logic
test: add unit tests for user service
```

### Pull Request Process

1. Create feature branch: `git checkout -b feature/[feature-name]`
2. Make changes and commit
3. Push to remote: `git push origin feature/[feature-name]`
4. Create Pull Request on Azure DevOps
5. Wait for CI checks to pass
6. Request review from team members
7. Address feedback and merge

---

## Dependencies

### Core Dependencies

- **Core Proto**: [dev.azure.com/agris-agriculture/Core](https://dev.azure.com/agris-agriculture/Core/_git/Core.git)
- **Library**: [dev.azure.com/agris-agriculture/Core/library](https://dev.azure.com/agris-agriculture/Core/_git/library.git)
- **gRPC**: [google.golang.org/grpc](https://pkg.go.dev/google.golang.org/grpc)
- **GORM**: [gorm.io/gorm](https://gorm.io)
- **Viper**: [github.com/spf13/viper](https://github.com/spf13/viper)

### Development Dependencies

- **Air**: Hot reload for Go apps
- **golangci-lint**: Linter aggregator
- **Mockery**: Mock generator

---

## License

Proprietary - AgriOS Agriculture

---

## Support

### Documentation

- [Architecture Decision Records](docs/adr/)
- [API Specifications](docs/api/)
- [Runbooks](docs/runbooks/)

### Contacts

- **Team**: AgriOS Backend Team
- **Tech Lead**: @[Name]
- **Project Manager**: @[Name]

### Useful Links

- [Confluence Space](https://confluence.example.com/agrios)
- [Jira Board](https://jira.example.com/agrios)
- [Azure DevOps](https://dev.azure.com/agris-agriculture)

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

**Latest Version**: v1.0.0
**Release Date**: DD MMM YYYY
