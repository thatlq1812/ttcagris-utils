# Centre Auth Service (CAS)

***Được tạo:*** 2025-12-26

***Cập nhật lần cuối:*** 2025-12-26

***Phiên bản:*** 1.0.0

***Trạng thái:*** Hoạt động

---

## Tổng quan

**Centre Auth Service (CAS)** là microservice xác thực và ủy quyền tập trung cho Nền tảng AgriOS. Nó quản lý danh tính người dùng, các luồng xác thực, kiểm soát truy cập dựa trên vai trò (RBAC) và tích hợp với các dịch vụ bên ngoài để xác minh eKYC.

**Các Trách Nhiệm Chính:**

- Xác thực người dùng (email, điện thoại, SSO)
- Quản lý tài khoản và định danh
- Kiểm soát truy cập dựa trên vai trò (RBAC)
- Quản lý JWT token
- Xác minh danh tính eKYC
- Quản lý hồ sơ nông dân và nhà cung cấp

---

## Tham khảo Nhanh

| Mục | Giá trị |
| --- | --- |
| **gRPC Port** | 50051 |
| **HTTP Port** | 4000 |
| **Database** | PostgreSQL 17+ |
| **Cache** | Redis 7+ |
| **Language** | Go 1.25+ |

---

## Các Tính Năng Chính

### Xác thực

- Xác thực Email/mật khẩu
- Xác thực bằng Điện thoại/OTP
- Tích hợp Azure SSO
- JWT access và refresh tokens
- Quản lý phiên thiết bị

### Quản lý User

- Các thao tác CRUD của Tài khoản
- Quản lý hồ sơ User
- Đăng ký và quản lý nông dân
- Đăng ký và quản lý nhà cung cấp

### Ủy quyền

- Kiểm soát truy cập dựa trên vai trò (RBAC) thông qua Casbin
- Quản lý permission
- Ủy quyền cấp độ API

### Tích hợp eKYC

- OCR để đọc thẻ căn cước
- Phát hiện độ sống động của khuôn mặt
- So sánh khuôn mặt
- Quy trình xác minh danh tính

---

## Kiến trúc

```
┌─────────────────┐      ┌─────────────────┐
│   API Gateway   │─────▶│       CAS       │
│   (REST/JSON)   │      │   (gRPC:50051)  │
└─────────────────┘      └────────┬────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
   │  PostgreSQL │         │    Redis    │         │   Azure     │
   │  (Database) │         │   (Cache)   │         │   Blob      │
   └─────────────┘         └─────────────┘         └─────────────┘
```

---

## Các Domain Entities

| Entity | Mô tả |
| --- | --- |
| **Account** | Định danh xác thực (email/phone/SSO) |
| **User** | Hồ sơ cá nhân được liên kết với account |
| **Farmer** | Hồ sơ nhà sản xuất nông nghiệp |
| **Supplier** | Hồ sơ nhà cung cấp dịch vụ |
| **Ekyc** | Dữ liệu xác minh danh tính |
| **Role** | Vai trò kiểm soát truy cập |
| **Permission** | Quyền truy cập API endpoint |

---

## gRPC Services

| Service | Mô tả |
| --- | --- |
| `AuthService` | Đăng nhập, đăng xuất, quản lý token |
| `MobileAuthService` | Xác thực dành riêng cho thiết bị di động |
| `AccountService` | Các hoạt động CRUD tài khoản |
| `UserService` | Quản lý hồ sơ người dùng |
| `FarmerService` | Quản lý nông dân |
| `SupplierService` | Quản lý nhà cung cấp |
| `RoleService` | Quản lý vai trò |
| `PermissionService` | Quản lý quyền |
| `EkycService` | Các hoạt động eKYC |
| `DeviceService` | Quản lý phiên thiết bị |

---

## Tài liệu Liên quan

| Tài liệu | Mô tả | Đối tượng |
| --- | --- | --- |
| [SRS_centre_auth_service.md](SRS_centre_auth_service.md) | Đặc tả Yêu cầu Phần mềm | PO, QA, Dev |
| [TDD_centre_auth_service.md](TDD_centre_auth_service.md) | Tài liệu Thiết kế Kỹ thuật | Dev, DevOps |
| [PROC_development_workflow.md](PROC_development_workflow.md) | Quy trình Phát triển | Dev |
| [centre-auth-service/README.md](../../../centre-auth-service/README.md) | README Kỹ thuật | Dev |

---

## Liên hệ

- **Team**: Backend Team
- **Repository**: `dev.azure.com/agris-agriculture/Core/_git/centre-auth-service`