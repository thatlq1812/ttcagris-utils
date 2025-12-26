# \[SRS\] Product Review & Rating System

  ----------------------------------------------------------------------------------------------------------------------------------------------------
  **Version**   **Date**   **Author**                                                                                                **Description**
  ------------- ---------- --------------------------------------------------------------------------------------------------------- -----------------
  1.0.0         22 Dec     [Trần Tiến                                                                                                Tạo tài liệu
                2025       Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   

                                                                                                                                     
  ----------------------------------------------------------------------------------------------------------------------------------------------------

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mục đích

Xây dựng hệ thống đánh giá và xếp hạng sản phẩm cho nền tảng e-commerce
nông nghiệp, cho phép người dùng đánh giá sản phẩm và tìm kiếm sản phẩm
phù hợp.

### 1.2 Phạm vi

- **User Service**: Quản lý người dùng, xác thực, phân quyền

- **Product Service**: Quản lý sản phẩm, tìm kiếm, rating

- **Gateway**: Traefik làm API Gateway

- **Timeline**: 1 sprint (1 week)

### 1.3 Định nghĩa thuật ngữ

- **P90 Latency**: 90% request phải hoàn thành trong thời gian quy định
  (\<200ms)

- **gRPC**: Remote Procedure Call framework hiệu năng cao

- **JWT**: JSON Web Token cho authentication

- **Admin**: User có quyền quản trị hệ thống

- **User**: Người dùng thông thường

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1 System Architecture

![](media/image1.tmp){width="4.875in" height="1.9916666666666667in"}

### 2.2 Technology Stack

  ----------------------------------------------------------------------
  **Component**   **Technology**   **Version**   **Purpose**
  --------------- ---------------- ------------- -----------------------
  Language        Go               1.25+         Programming Language

  Framework       Fiber            2.x           HTTP router

  ORM             GORM             latest        Database operations

  Database        PostgreSQL       17+           Data storage

  Cache           Redis            7+            Performance
                                                 optimization

  Gateway         Traefik          2.10+         API Gateway, Load
                                                 balancing

  RPC             gRPC             latest        Inter-service
                                                 communication

  Auth            JWT              \-            Token-based
                                                 authentication

  Access Control  RBAC             \-            Authorize
  ----------------------------------------------------------------------

## 2. Biz Requirement

### 2.1 User Management

- **BR-001**: Hệ thống phải cho phép người dùng đăng ký tài khoản mới
  với email và password.

- **BR-002**: Hệ thống phải xác thực người dùng thông qua JWT tokens.

- **BR-003**: Hệ thống phải phân biệt 2 loại user: **User** (người dùng
  thường) và **Admin** (quản trị viên).

- **BR-004**: Admin phải có khả năng xem danh sách tất cả users và thay
  đổi phân quyền của họ.

- **BR-005**: Admin không được phép tự thay đổi role của chính mình.

### 2.2 Product Management

- **BR-006**: Hệ thống phải hiển thị danh sách sản phẩm với khả năng
  phân trang.

- **BR-007**: Người dùng phải có thể tìm kiếm sản phẩm theo tên (không
  phân biệt dấu và hoa thường trong tiếng Việt).

- **BR-008**: Hệ thống phải gợi ý các sản phẩm tương tự (cùng category)
  cho mỗi sản phẩm.

- **BR-009**: Hệ thống phải hiển thị các sản phẩm đi kèm/phụ kiện liên
  quan đến sản phẩm chính.

- **BR-010**: Hệ thống phải có chức năng hiển thị sản phẩm được yêu
  thích dựa vào rating.

### 2.3 Rating & Review

- **BR-011**: Chỉ người dùng đã đăng nhập mới được phép đánh giá sản
  phẩm.

- **BR-012**: Một user chỉ được phép tạo **một** rating cho mỗi sản
  phẩm.

- **BR-013**: User có thể cập nhật rating của chính mình nhưng không thể
  tạo rating mới cho cùng sản phẩm.

- **BR-014**: Rating phải là số nguyên từ 1 đến 5 sao.

- **BR-015**: Hệ thống phải tự động tính toán và cập nhật average rating
  của sản phẩm khi có rating mới/cập nhật/xóa.

- **BR-016**: User chỉ có thể xóa rating của chính mình. Admin có thể
  xóa bất kỳ rating nào.

## 3. FUNCTIONAL REQUIREMENTS

### 3.1 User Service - Authentication & Authorization

#### Feature List:

- **F-U01**: User Registration

- **F-U02**: User Login

- **F-U03**: Token Validation (gRPC endpoint)

- **F-U04**: Get Current User Info

- **F-U05**: Admin - List All Users (with pagination, search, filter)

- **F-U06**: Admin - Update User Role

#### Requirements:

- JWT-based authentication

- Password hashing (bcrypt recommended)

- Token expiry management

- Account lockout sau N lần login sai (optional but recommended)

- gRPC service để validate token cho Product Service

### 3.2 Product Service - Product Management

#### Feature List:

- **F-P01**: List Products (with pagination)

- **F-P02**: Search Products by Name (Vietnamese text search)

- **F-P03**: Get Product Detail

- **F-P04**: Get Similar Products (same category)

- **F-P05**: Get Related Products (có relationship)

- **F-P06**: Get Popular Products (sorted by rating)

#### Requirements:

- Vietnamese text normalization cho search

- Efficient pagination

- Category-based filtering

- Redis caching cho expensive queries

### 3.3 Product Service - Rating Management

#### Feature List:

- **F-R01**: Create Product Rating

- **F-R02**: Update Own Rating

- **F-R03**: Delete Rating (owner or admin)

- **F-R04**: Get Product Ratings (with pagination, filter by star)

- **F-R05**: Get Rating Statistics (average, distribution)

- **F-R06**: Get My Ratings (user\'s own ratings)

#### Requirements:

- Enforce unique constraint (1 user = 1 rating per product)

- Auto-update average rating

- Support image uploads trong rating (optional)

- Cache invalidation khi rating changes

## 4. Technical Requirement

- **TC-001**: Hệ thống PHẢI được chia thành 2 services độc lập:

  - User Service (port 8005 HTTP, port 9005 gRPC)

  - Product Service (port 8010 HTTP)

- **TC-002**: User Service PHẢI expose gRPC endpoint Authenticate() để
  Product Service gọi từ middleware.

- **TC-003**: Product Service hoặc gateway PHẢI sử dụng gRPC để validate
  token thay vì REST API.

- **TC-004**: PHẢI sử dụng Traefik làm API Gateway để route requests.

- **TC-005**: Mỗi service có database riêng (không share database).

- **TC-008**: Search PHẢI hỗ trợ tiếng Việt:

  - Không phân biệt dấu: \"Máy cày\" = \"may cay\" = \"MÁY CÀY\"

  - Không phân biệt hoa thường

  - Hỗ trợ partial match

- **TC-009**: Phải seed database với:

  - **5,000-10,000 products** (distributed across categories)

  - **20 categories**

  - average 5 ratings/product

## 5. NON-FUNCTIONAL REQUIREMENTS

### 5.1 Performance (CRITICAL)

**NFR-P01**: **P90 Latency ≤ 200ms**

- Measurement: 90% of requests must complete within 200ms

- Test conditions:

  - 10,000 products in database

  - 100 concurrent users

  - Focus on: List Products, Search Products, Get Ratings

**NFR-P02**: Caching Strategy Required

- MUST cache expensive queries trong Redis

- Minimum requirements:

  - Similar products (TTL: 1 hour)

  - Popular products (TTL: 30 minutes)

  - Related products (TTL: 1 hour)

- Cache hit rate target: ≥ 80%

**NFR-P03**: Database Optimization

- MUST create appropriate indexes

- Query performance target: Most queries \< 50ms

- Connection pooling configured properly

### 5.2 Security

**NFR-S01**: Authentication

- JWT tokens with reasonable expiry (suggest: 1 hour)

- Secure password hashing (bcrypt min cost 10)

- Token validation on every protected route

**NFR-S02**: Authorization

- Role-based access control (User vs Admin)

- Middleware để check permissions

- Admin endpoints MUST validate admin role

**NFR-S03**: Input Validation

- Validate all user inputs

- Prevent SQL injection (GORM parameterized queries)

- Sanitize data before storage

### 5.3 Code Quality

**NFR-Q01**: Code Structure

- Follow clean architecture principles

- Separate layers: handler → service → repository

**NFR-Q02**: Testing

- Unit tests cho business logic (target: ≥ 50% coverage)

**NFR-Q03**: Documentation

- API documentation (Swagger/Postman collection)

- README với setup instructions

# Hướng dẫn thực hiện

- Confirm các issue và các target cần thực hiện trong tài liệu.

- Gửi lại thiết kế ERD cho mentor và phần sequence diagram (overview
  flow)

- Tạo nhờ mentor tạo 1 một story/epic trong Jira và assigne tự break ra
  các task nhỏ hơn để thực hiện. Khi code thì tạo ra các branch có name
  tương ứng với với ID của task sau đó merge vào main để tracking. Có
  prefix để thực hiện check các tính năng ví dụ

  - feat/ID-123: thực hiện implement future cho task ID-123.

  - improve/ID-456: thực hiện việc improve các chức năng trong task 456.

  - fix/ID-789: các commit thực hiện cho việc fix bug.

- Các message commit phải thêm prefix sau để highlight công việc thực
  hiện

  - #add: thêm mới.

  - #update: sửa đỗi.

  - #remove: xóa.

  - #fix: sửa lỗi.

- Khi merge code từ branch khác sang main cần được review và approve bởi
  mentor.

- Khi thực hiện 1 feature mới luôn phải checkout từ main ra branch mới
  và thực hiện.

# Mục tiêu đầu ra

- Làm quen với workflow hiện tại.

- Khả năng phân chia công việc.

- Tư duy thiết kế hệ thống, xử lý công việc.

- Nắm được các công nghệ Go.
