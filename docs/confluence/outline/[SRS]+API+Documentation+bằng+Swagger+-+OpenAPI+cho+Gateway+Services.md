# \[SRS\] API Documentation bằng Swagger - OpenAPI cho Gateway Services

- [1. Giới thiệu](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [1.1 Mục tiêu](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [1.2 Phạm vi](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [1.3 Đối tượng sử dụng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [2. Tổng quan hệ thống](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [2.1 Vai trò của Swagger](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [2.2 Giả định và ràng
    buộc](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [3. Yêu cầu chung cho tất cả
  Gateway](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [3.1 Yêu cầu chức năng
    chung](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-01: Chuẩn OpenAPI](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-02: Phạm vi mô tả
      API](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-03: Nội dung bắt buộc cho mỗi
      API](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [3.2 Schema và tái sử
    dụng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-04: Chuẩn hóa
      schema](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-05: Response lỗi
      chuẩn](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [3.3 Xác thực và bảo mật](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-06: Mô tả cơ chế xác
      thực](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [4. Yêu cầu riêng theo từng
  Gateway](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [4.1 App Gateway](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.1.1 Phạm vi](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.1.2 Yêu cầu chức năng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-A01: Nhóm API rõ
      ràng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-A02: Version API](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-A03: Ví dụ dữ liệu](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.1.3 Giới hạn có chủ
    đích](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [4.2 Portal Gateway](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.2.1 Phạm vi](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.2.2 Yêu cầu chức năng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-P01: Phân biệt vai
      trò](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-P02: API danh sách](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-P03: Schema ổn định](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.2.3 Giới hạn có chủ
    đích](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [4.3 Third Party Gateway](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.3.1 Phạm vi](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.3.2 Yêu cầu chức năng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-T01: Mô tả đầy đủ](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-T02: Xác thực rõ
      ràng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-T03: Ổn định
      contract](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [4.3.3 Giới hạn có chủ
    đích](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [5. Tài liệu hướng dẫn Swagger ↔
  Postman](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [5.1 Yêu cầu chức năng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-D01: Export OpenAPI](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-D02: Import vào
      Postman](#id-[SRS]APIDocumentationbằngSwagger-Ope)

    - [FR-D03: Kiểm thử cơ
      bản](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [6. Yêu cầu phi chức năng (Non-Functional
  Requirements)](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [6.1 Khả năng sử dụng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [6.2 Bảo trì](#id-[SRS]APIDocumentationbằngSwagger-Ope)

  - [6.3 Hiệu năng](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [7. Các giới hạn có chủ đích (Explicit
  Non-Goals)](#id-[SRS]APIDocumentationbằngSwagger-Ope)

- [8. Tiêu chí nghiệm thu tổng
  thể](#id-[SRS]APIDocumentationbằngSwagger-Ope)

## 1. Giới thiệu

### 1.1 Mục tiêu

Xây dựng tài liệu API thống nhất bằng Swagger (OpenAPI) cho các gateway
service nhằm:

- Giảm phụ thuộc trao đổi miệng giữa các team

- Chuẩn hóa cách mô tả API

- Hỗ trợ tích hợp, kiểm thử và onboarding nhanh

- Là nguồn sự thật duy nhất (single source of truth) cho API public

### 1.2 Phạm vi

Áp dụng cho **3 gateway service dạng application gateway**:

- App Gateway (mobile app)

- Portal Gateway (web portal nội bộ)

- Third Party Gateway (đối tác bên ngoài)

Swagger chỉ mô tả **API public**, không bao gồm API nội bộ hoặc endpoint
kỹ thuật.

### 1.3 Đối tượng sử dụng

- Backend Developer

- Frontend / Mobile Developer

- PO / Tester

- Đối tác tích hợp (đối với Third Party Gateway)

## 2. Tổng quan hệ thống

### 2.1 Vai trò của Swagger

- Là tài liệu kỹ thuật chính thức của API

- Là đầu vào cho Postman, mock server, test automation

- Không thay thế code, nhưng phản ánh chính xác contract API

### 2.2 Giả định và ràng buộc

- Swagger tuân theo chuẩn **OpenAPI 3.x**

- Không yêu cầu backward compatibility phức tạp ở giai đoạn đầu

- Swagger được quản lý cùng repository với source code

## 3. Yêu cầu chung cho tất cả Gateway

### 3.1 Yêu cầu chức năng chung

#### FR-01: Chuẩn OpenAPI

- Tất cả Swagger phải tuân theo OpenAPI 3.x

- Có thể export dưới dạng JSON hoặc YAML

#### FR-02: Phạm vi mô tả API

- Chỉ mô tả API public

- Không mô tả endpoint internal hoặc debug

#### FR-03: Nội dung bắt buộc cho mỗi API

Mỗi endpoint phải có:

- Mô tả ngắn gọn mục đích

- HTTP method

- Tham số đầu vào (path, query, body)

- Response thành công

- Response lỗi phổ biến (4xx, 5xx)

### 3.2 Schema và tái sử dụng

#### FR-04: Chuẩn hóa schema

- Sử dụng components/schemas cho model dùng chung

- Không lặp lại định nghĩa schema giữa các endpoint

#### FR-05: Response lỗi chuẩn

- Định nghĩa schema lỗi dùng chung

- Mã lỗi và thông điệp rõ ràng

### 3.3 Xác thực và bảo mật

#### FR-06: Mô tả cơ chế xác thực

- Mỗi gateway phải mô tả rõ:

  - Loại xác thực (Bearer token, API key, OAuth, JWT)

  - Header sử dụng

- Không mô tả chi tiết implementation bảo mật nội bộ

## 4. Yêu cầu riêng theo từng Gateway

## 4.1 App Gateway

### 4.1.1 Phạm vi

- API phục vụ mobile app

- Tập trung vào nghiệp vụ chính của ứng dụng

### 4.1.2 Yêu cầu chức năng

#### FR-A01: Nhóm API rõ ràng

- Sử dụng tag để nhóm API theo domain nghiệp vụ

#### FR-A02: Version API

- Có version rõ ràng trong path (ví dụ: /v1)

#### FR-A03: Ví dụ dữ liệu

- Các API chính phải có example request/response

### 4.1.3 Giới hạn có chủ đích

- Không mô tả logic xử lý phía server

- Không mô tả flow UI

## 4.2 Portal Gateway

### 4.2.1 Phạm vi

- API phục vụ web portal nội bộ

- Có phân quyền và nghiệp vụ vận hành

### 4.2.2 Yêu cầu chức năng

#### FR-P01: Phân biệt vai trò

- Mỗi API phải ghi chú rõ vai trò được phép truy cập (admin,
  operator...)

#### FR-P02: API danh sách

- Mô tả rõ pagination, filter, sort

#### FR-P03: Schema ổn định

- Thêm field mới không làm hỏng client cũ

### 4.2.3 Giới hạn có chủ đích

- Không dùng Swagger để quản lý quyền động

- Không mô tả chi tiết truy vấn dữ liệu nội bộ

## 4.3 Third Party Gateway

### 4.3.1 Phạm vi

- API public cho đối tác bên ngoài

- Swagger là API contract chính thức

### 4.3.2 Yêu cầu chức năng

#### FR-T01: Mô tả đầy đủ

- Mỗi API phải có example request/response đầy đủ

- Mô tả rõ mã lỗi và ý nghĩa

#### FR-T02: Xác thực rõ ràng

- Mô tả chính xác cơ chế xác thực

- Không thay đổi tùy tiện sau khi công bố

#### FR-T03: Ổn định contract

- Không thay đổi field hiện có

- Nếu thay đổi lớn, phải version API mới

### 4.3.3 Giới hạn có chủ đích

- Không reuse schema internal

- Không để lộ chi tiết triển khai backend

## 5. Tài liệu hướng dẫn Swagger ↔ Postman

### 5.1 Yêu cầu chức năng

#### FR-D01: Export OpenAPI

- Hướng dẫn export OpenAPI từ Swagger UI (JSON/YAML)

#### FR-D02: Import vào Postman

- Hướng dẫn import OpenAPI vào Postman

- Cấu hình environment (base URL, token)

#### FR-D03: Kiểm thử cơ bản

- Gọi thử API

- Nhận diện lỗi thường gặp

## 6. Yêu cầu phi chức năng (Non-Functional Requirements)

### 6.1 Khả năng sử dụng

- Dev mới có thể sử dụng Swagger mà không cần hướng dẫn thêm

- Portal / mobile team tự test API

### 6.2 Bảo trì

- Swagger cập nhật cùng code

- Không sinh ra Swagger lỗi schema

### 6.3 Hiệu năng

- Swagger UI tải nhanh trong môi trường dev

## 7. Các giới hạn có chủ đích (Explicit Non-Goals)

- Không dùng Swagger làm API gateway

- Không dùng Swagger để enforce runtime validation

- Không sinh mock server phức tạp

## 8. Tiêu chí nghiệm thu tổng thể

- Swagger phản ánh đúng API đang chạy

- Import vào Postman thành công

- Đối tác có thể tích hợp dựa hoàn toàn vào Swagger
