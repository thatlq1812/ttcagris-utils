# Docker Development Environment Changelog

All notable changes to the Docker development environment will be documented in this file.

## [2.0.0] - 2025-12-25

### Added - TOB-46 Completion

- **Web API Gateway** integration: 6 gRPC supplier-service methods mapped to REST endpoints
- **Supplier Service** integration into Docker environment (port 9088 gRPC, 8088 HTTP)
- **Complete implementation workflow** document with 5 phases and detailed step-by-step guide
- **Pre-deployment checklist** with 35+ verification items
- **Database migration automation** - 70+ migration files applied to centre_auth database
- **Test accounts** - 4 accounts with different role combinations for comprehensive testing
- **Quick reference commands** - 40+ copy-paste ready commands for all operations
- **Lessons learned documentation** - 10 key insights from implementation

### Enhanced

- Updated `docker-compose.dev.yml` with 6 services (added supplier-service, web-api-gateway)
- Created `Dockerfile.supplier.dev` for supplier-service
- Created `Dockerfile.webgw.dev` for web-api-gateway
- Fixed all ENTRYPOINT commands in Dockerfiles to include service startup arguments
- Added health checks for all services
- Improved database initialization with complete schema creation

### Verified (Post-TOB-46)

- **Web API Gateway** running and accessible on port 4001
- **Supplier Service** integrated with 6 gRPC endpoints:
  - GetListPlantTypes: Returns 4 items ✅
  - GetListStages: Returns 4 items ✅
  - GetListUnits: Returns 4 items ✅
  - GetListServices: Returns 14+ items ✅
  - CreateService: Creates services with auto-generated codes ✅
  - UpdateService: Updates service details and status ✅
- **Authentication** - 4 test accounts with phone-based authentication all working
- **Database schema** - centre_auth and supplier_svc_db fully migrated
- **Multi-user testing** - Accounts with different roles (Farmer, Supplier, Both) tested
- **End-to-end workflow** - Complete implementation path documented and verified

### Configuration Changes

- PostgreSQL: Now has centre_auth and supplier_svc_db databases
- Redis: Unchanged (port 6379)
- CAS service: gRPC 50051, HTTP 4000 (unchanged)
- Noti-service: gRPC 9012, HTTP 8000 (unchanged)
- **Supplier Service (NEW)**: gRPC 9088, HTTP 8088
- **Web API Gateway (NEW)**: HTTP 4001

### Services Status

```
✅ Web API Gateway: Running on port 4001
✅ Centre Auth Service: Running on ports 50051 (gRPC), 4000 (HTTP)
✅ Supplier Service: Running on ports 9088 (gRPC), 8088 (HTTP)
✅ Noti Service: Running on ports 9012 (gRPC), 8000 (HTTP)
✅ PostgreSQL: Running on port 5432 (2 databases)
✅ Redis: Running on port 6379
```

### Test Accounts

Four phone-based test accounts with different role combinations:

| Account ID | Phone | Farmer | Supplier | Status |
|-----------|-------|--------|----------|--------|
| 5 | 0901111111 | ✅ | ✅ | ✅ Working |
| 6 | 0902222222 | ✅ | ❌ | ✅ Working |
| 7 | 0903333333 | ❌ | ✅ | ✅ Working |
| 999 | 0909999999 | ❌ | ✅ | ✅ Working |

All accounts: Password `password123`

### Documentation

- **TOB46_IMPLEMENTATION.md**: 1741-line comprehensive guide with:
  - Complete 5-phase implementation workflow
  - 40+ quick reference commands
  - Pre-deployment checklist (35+ items)
  - Lessons learned (10 key insights)
  - Troubleshooting guide with solutions
  - Best practices for future integrations

- **IMPLEMENTATION_SUMMARY.md**: Quick reference summary with key metrics and next steps

### Known Issues Resolved

- ✅ Docker binary format errors (Windows → Linux builds)
- ✅ ENTRYPOINT missing service command
- ✅ Missing config.yaml files
- ✅ Email account authentication failures
- ✅ Database migration conflicts (expected and handled)
- ✅ JWT secret synchronization (documented requirement)

---

## [1.0.0] - 2025-12-25

### Added

- Initial Docker development environment for TOB-37 and TOB-45 testing
- `docker-compose.dev.yml` with 4 services: postgres, redis, cas-service, noti-service
- `Dockerfile.cas.dev` for CAS service with pre-built Linux binary
- `Dockerfile.noti.dev` for Noti-service with pre-built Linux binary
- Database initialization scripts in `init-db/`
- Test data seeding for supplier deactivation flow
- Comprehensive README with quick start guide

### Verified

- Login API working with phone/password authentication
- DeactiveSupplier API triggering FCM notifications
- CAS -> Noti-service gRPC communication working
- FCM multicast delivery successful with real device token
- Mobile app receiving push notifications

### Configuration

- PostgreSQL 17-alpine on port 5432
- Redis 7-alpine on port 6379
- CAS service: gRPC 50051, HTTP 4000
- Noti-service: gRPC 9012, HTTP 8000

### Test Credentials

- Phone: 0909999999
- Password: password123
- Account ID: 999
- Supplier ID: 888

### Known Issues

- Must build Linux binaries before Docker build (no in-container Go build)
- FCM requires real token from mobile app (placeholder fails)
- `suppliers.name` column must be added manually if using old schema

### Documentation

- `docker/README.md` - Detailed setup guide
- `docs/DOCKER_DEV_QUICKSTART.md` - Quick start guide
- `docs/tob45/seed_test_data.sql` - Test data SQL script
