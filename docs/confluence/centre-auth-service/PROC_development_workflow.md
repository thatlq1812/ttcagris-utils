# [PROC] Centre Auth Service - Development Workflow

| Version | Date | Author | Description |
| --- | --- | --- | --- |
| 1.0.0 | 26 Dec 2025 | That Le | Initial document |

**Status**: Active

---

## 1. Purpose

This document defines the development workflow, deployment process, and operational procedures for the Centre Auth Service (CAS). It ensures consistent practices across the team and provides guidance for common development scenarios.

---

## 2. Scope

### 2.1 Applies To

- Backend Developers working on CAS
- DevOps Engineers managing deployments
- QA Team testing CAS features

### 2.2 Does Not Apply To

- Frontend/Mobile development (separate process)
- Other microservices (see their respective process docs)

---

## 3. Definitions and Terminology

| Term | Definition |
| --- | --- |
| CAS | Centre Auth Service |
| Proto | Protocol Buffers definition files |
| Core | Central repository for proto definitions |
| Migration | Database schema change script |
| Usecase | Business logic layer component |
| gRPC | Remote procedure call framework |

---

## 4. Roles and Responsibilities

### 4.1 Backend Developer

- Implements features according to requirements
- Writes unit tests (minimum 80% coverage)
- Creates migrations for schema changes
- Updates documentation

### 4.2 Tech Lead

- Reviews pull requests
- Approves schema changes
- Coordinates with other service teams

### 4.3 DevOps Engineer

- Manages deployment pipelines
- Monitors service health
- Handles infrastructure issues

---

## 5. Development Process

### 5.1 Environment Setup

#### 5.1.1 Prerequisites

- Go 1.25+
- PostgreSQL 17+
- Redis 7+
- Docker and Docker Compose
- Make

#### 5.1.2 Initial Setup

```bash
# Clone repository
git clone https://dev.azure.com/agris-agriculture/Core/_git/centre-auth-service
cd centre-auth-service

# Install dependencies
go mod download

# Copy configuration
cp config/config.example.yaml config/config.yaml

# Edit config.yaml with local database credentials

# Run service
make api
```

### 5.2 Feature Development Workflow

#### Step 1: Create Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/TASK-123-feature-name
```

**Branch Naming Convention:**
- Feature: `feature/TASK-123-description`
- Bug fix: `fix/TASK-456-description`
- Hotfix: `hotfix/TASK-789-description`

#### Step 2: Proto Changes (If Required)

If the feature requires new gRPC methods:

1. **Update Core repository first**
   ```bash
   cd ../Core
   git checkout -b feature/TASK-123-proto-changes
   
   # Edit proto files
   vim proto/auth/v1/auth.proto
   
   # Generate code
   make generate
   
   # Commit and push
   git add .
   git commit -m "[TASK-123] Add new RPC method"
   git push origin feature/TASK-123-proto-changes
   ```

2. **Create PR and wait for merge**

3. **Update CAS to use new Core**
   ```bash
   cd ../centre-auth-service
   make update-core
   ```

#### Step 3: Implement Feature

Follow Clean Architecture layers:

1. **Domain** (internal/domain/)
   - Define request/response structs
   - Define domain models

2. **Repository** (internal/repository/)
   - Implement data access methods

3. **Usecase** (internal/usecase/)
   - Implement business logic

4. **gRPC Handler** (internal/grpc/)
   - Implement gRPC service methods

#### Step 4: Database Migrations

If schema changes are needed:

```bash
# Create migration file
touch migrations/XXX_description.sql

# Edit migration
vim migrations/XXX_description.sql
```

**Migration File Naming:**
- Format: `XXX_description.sql`
- XXX: Sequential number (e.g., 071, 072)
- Description: Snake case description

**Example Migration:**
```sql
-- 071_add_new_column.sql

-- Add new column
ALTER TABLE accounts ADD COLUMN new_field VARCHAR(50);

-- Create index if needed
CREATE INDEX idx_accounts_new_field ON accounts(new_field);
```

#### Step 5: Write Tests

```bash
# Run tests
make test

# Run with coverage
make test-coverage
```

**Test Requirements:**
- Minimum 80% code coverage
- Unit tests for all usecase methods
- Integration tests for repository methods

#### Step 6: Create Pull Request

1. Push branch
   ```bash
   git push origin feature/TASK-123-feature-name
   ```

2. Create PR in Azure DevOps

3. Fill PR template:
   - Description of changes
   - Link to Jira task
   - Testing instructions
   - Screenshots (if applicable)

4. Request review from Tech Lead

### 5.3 Code Review Checklist

Reviewers should verify:

- [ ] Code follows Clean Architecture
- [ ] Proto changes are in Core (if applicable)
- [ ] Migrations are backward compatible
- [ ] Tests pass with 80%+ coverage
- [ ] No hardcoded secrets
- [ ] Proper error handling
- [ ] Logging added for key operations
- [ ] Documentation updated

---

## 6. Deployment Process

### 6.1 Environments

| Environment | Branch | Auto Deploy |
| --- | --- | --- |
| DEV | main | Yes |
| UAT/TESTING | release/* | Manual |
| PRODUCTION | main (tag) | Manual |

### 6.2 DEV Deployment

Automatic on merge to main:

1. PR merged to main
2. Azure Pipeline triggers
3. Build Docker image
4. Push to container registry
5. Deploy to DEV cluster
6. Run smoke tests

### 6.3 UAT Deployment

Manual trigger:

1. Create release branch: `release/v1.2.3`
2. Trigger pipeline manually
3. Build and deploy to UAT
4. Notify QA team

### 6.4 Production Deployment

Requires approval:

1. Create tag: `v1.2.3`
2. Create release in Azure DevOps
3. Request approval from Tech Lead
4. Deploy during maintenance window
5. Monitor for 30 minutes
6. Rollback if issues detected

### 6.5 Rollback Procedure

If issues detected in production:

```bash
# Option 1: Redeploy previous version
az pipelines run --name "CAS-Deploy" --variables version=v1.2.2

# Option 2: Database rollback (if migration issue)
# Prepare rollback migration
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f rollback.sql
```

---

## 7. Operational Procedures

### 7.1 Health Monitoring

Check service health:

```bash
# Health endpoint
curl http://cas-service:4000/health

# gRPC health
grpcurl -plaintext localhost:50051 grpc.health.v1.Health/Check
```

### 7.2 Log Analysis

```bash
# View recent logs
kubectl logs -f deployment/centre-auth-service

# Search for errors
kubectl logs deployment/centre-auth-service | grep ERROR
```

### 7.3 Common Issues

#### Issue: Token validation failures

**Symptoms:** 401 errors on authenticated requests

**Resolution:**
1. Check Redis connectivity
2. Verify JWT secrets match between services
3. Check token expiry configuration

#### Issue: Database connection errors

**Symptoms:** 500 errors, connection timeout logs

**Resolution:**
1. Check database availability
2. Verify connection pool settings
3. Check network policies

#### Issue: High latency

**Symptoms:** P90 latency > 200ms

**Resolution:**
1. Check database query performance
2. Review Redis cache hit rate
3. Scale replicas if needed

---

## 8. Local Development Tips

### 8.1 Using Local Core

For development with local proto changes:

```bash
# Use local Core directory
make use-local-core CORE_PATH=../Core

# After development, restore remote
make use-remote-core
```

### 8.2 Hot Reload

Service auto-restarts on file changes in development mode.

### 8.3 Debug Mode

Enable debug logging:

```yaml
# config.yaml
log_config:
  level: debug
```

### 8.4 Testing gRPC Endpoints

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Describe service
grpcurl -plaintext localhost:50051 describe auth.v1.AuthService

# Call method
grpcurl -plaintext -d '{"type":"email","identifier":"test@example.com","password":"password123"}' \
  localhost:50051 auth.v1.AuthService/Login
```

---

## 9. Security Procedures

### 9.1 Secret Management

- Store secrets in HashiCorp Vault
- Never commit secrets to repository
- Use environment variables for local development
- Rotate JWT secrets quarterly

### 9.2 Access Control

- Use separate JWT secrets for web and mobile
- Implement API key rotation for service-to-service
- Review Casbin policies quarterly

### 9.3 Incident Response

If security incident detected:

1. Notify Tech Lead immediately
2. Revoke compromised credentials
3. Rotate affected secrets
4. Audit access logs
5. Document incident and resolution

---

## 10. Documentation Maintenance

### 10.1 When to Update

Update documentation when:
- New feature added
- API changed
- Configuration changed
- Process updated

### 10.2 Documentation Locations

| Document Type | Location |
| --- | --- |
| Technical README | centre-auth-service/README.md |
| SRS | docs/confluence/centre-auth-service/SRS_centre_auth_service.md |
| TDD | docs/confluence/centre-auth-service/TDD_centre_auth_service.md |
| Process | docs/confluence/centre-auth-service/PROC_development_workflow.md |

---

## 11. Related Documents

- [SRS] Centre Auth Service - Software Requirements
- [TDD] Centre Auth Service - Technical Design
- [PROC] Sprint Workflow - General sprint process
- Core Repository - Proto definitions
