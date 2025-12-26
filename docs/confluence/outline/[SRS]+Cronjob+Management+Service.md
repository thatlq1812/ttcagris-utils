# \[SRS\] Cronjob Management Service

- [1. Giới thiệu](#id-[SRS]CronjobManagementService-1.Giới)

  - [1.1 Mục tiêu](#id-[SRS]CronjobManagementService-1.1Mục)

  - [1.2 Phạm vi hệ thống](#id-[SRS]CronjobManagementService-1.2Phạ)

  - [1.3 Đối tượng sử dụng](#id-[SRS]CronjobManagementService-1.3Đối)

- [2. Tổng quan hệ thống](#id-[SRS]CronjobManagementService-2.Tổng)

  - [2.1 Vị trí trong kiến
    trúc](#id-[SRS]CronjobManagementService-2.1Vịt)

  - [2.2 Giả định và ràng
    buộc](#id-[SRS]CronjobManagementService-2.2Giả)

- [3. Yêu cầu chức năng (Functional
  Requirements)](#id-[SRS]CronjobManagementService-3.Yêuc)

  - [3.1 Quản lý cronjob](#id-[SRS]CronjobManagementService-3.1Quả)

    - [FR-01: Tạo cronjob](#id-[SRS]CronjobManagementService-FR-01:)

    - [FR-02: Cập nhật
      cronjob](#id-[SRS]CronjobManagementService-FR-02:)

    - [FR-03: Bật / tắt
      cronjob](#id-[SRS]CronjobManagementService-FR-03:)

    - [FR-04: Xóa cronjob](#id-[SRS]CronjobManagementService-FR-04:)

  - [3.2 Scheduler và trigger](#id-[SRS]CronjobManagementService-3.2Sch)

    - [FR-05: Lập lịch
      cronjob](#id-[SRS]CronjobManagementService-FR-05:)

    - [FR-06: Trigger internal
      API](#id-[SRS]CronjobManagementService-FR-06:)

    - [FR-07: Chống trigger
      trùng](#id-[SRS]CronjobManagementService-FR-07:)

  - [3.3 Retry và lỗi](#id-[SRS]CronjobManagementService-3.3Ret)

    - [FR-08: Retry giới hạn](#id-[SRS]CronjobManagementService-FR-08:)

    - [FR-09: Xử lý lỗi](#id-[SRS]CronjobManagementService-FR-09:)

  - [3.4 API public cho
    portal](#id-[SRS]CronjobManagementService-3.4API)

    - [FR-10: API quản lý
      cronjob](#id-[SRS]CronjobManagementService-FR-10:)

    - [FR-11: Phân quyền](#id-[SRS]CronjobManagementService-FR-11:)

- [4. Format cấu hình cronjob](#id-[SRS]CronjobManagementService-4.Form)

  - [4.1 Cấu trúc JSON gợi ý](#id-[SRS]CronjobManagementService-4.1Cấu)

  - [4.2 Rule cấu hình](#id-[SRS]CronjobManagementService-4.2Rul)

- [5. Yêu cầu phi chức năng (Non-Functional
  Requirements)](#id-[SRS]CronjobManagementService-5.Yêuc)

  - [5.1 Độ tin cậy](#id-[SRS]CronjobManagementService-5.1Đột)

  - [5.2 Hiệu năng](#id-[SRS]CronjobManagementService-5.2Hiệ)

  - [5.3 Bảo mật](#id-[SRS]CronjobManagementService-5.3Bảo)

  - [5.4 Quan sát và logging](#id-[SRS]CronjobManagementService-5.4Qua)

- [6. Các giới hạn có chủ đích (Explicit
  Non-Goals)](#id-[SRS]CronjobManagementService-6.Cácg)

- [7. Khả năng mở rộng trong tương
  lai](#id-[SRS]CronjobManagementService-7.Khản)

- [8. Tiêu chí nghiệm thu tổng
  thể](#id-[SRS]CronjobManagementService-8.Tiêu)

## 1. Giới thiệu

### 1.1 Mục tiêu

Xây dựng một service quản lý tập trung các cronjob trong hệ thống
backend, cho phép:

- Quản lý cấu hình cronjob tập trung

- Tự động trigger các action thông qua internal API khi cronjob đến hạn

- Cho phép portal quản lý cronjob thông qua API public

Service được thiết kế theo hướng **đơn giản -- dễ vận hành -- giảm rủi
ro phổ biến**, phù hợp với hệ thống còn nhỏ.

### 1.2 Phạm vi hệ thống

Cronjob Management Service chịu trách nhiệm:

- Lưu trữ và quản lý metadata cấu hình cronjob

- Lập lịch và trigger cronjob

- Ghi nhận trạng thái chạy gần nhất

Cronjob service **không**:

- Thực thi logic nghiệp vụ

- Xử lý workflow phức tạp

- Đảm bảo HA hoặc scale lớn

### 1.3 Đối tượng sử dụng

- Backend Developer

- DevOps / Vận hành

- Portal (admin)

## 2. Tổng quan hệ thống

### 2.1 Vị trí trong kiến trúc

- Là service backend độc lập

- Gọi internal API đến các backend service khác

- Cung cấp API public cho portal

### 2.2 Giả định và ràng buộc

- Chạy **single instance**

- Số lượng cronjob ít đến trung bình

- Không yêu cầu độ chính xác tuyệt đối từng giây

## 3. Yêu cầu chức năng (Functional Requirements)

### 3.1 Quản lý cronjob

#### FR-01: Tạo cronjob

- Cho phép tạo mới cronjob với trạng thái mặc định là inactive

- Mỗi cronjob có code duy nhất và không được thay đổi

#### FR-02: Cập nhật cronjob

- Cho phép cập nhật cron expression và thông tin target

- Không ảnh hưởng cronjob đang chạy

#### FR-03: Bật / tắt cronjob

- Cronjob chỉ được trigger khi ở trạng thái active

#### FR-04: Xóa cronjob

- Chỉ xóa khi cronjob không đang chạy

### 3.2 Scheduler và trigger

#### FR-05: Lập lịch cronjob

- Scheduler đọc cron expression và xác định thời điểm trigger.

- Khoảng cách **ngắn nhất** của cron là **một phút**, những trường hợp
  cần khoảng cách ngắn hơn cần dùng giải pháp khác (như daemon).

- Không hỗ trợ catch-up khi miss lịch.

- Đối với UI cấu hình, cần sử dụng múi giờ Việt Nam (GMT +7), không sử
  dụng giờ server.

#### FR-06: Trigger internal API

- Khi đến hạn, gọi internal API theo cấu hình (gRPC).

- Có thể cấu hình timeout theo từng cron.

- Có cơ chế ghi nhận kết quả thực thi của cron.

#### FR-07: Chống trigger trùng

- Không trigger nếu cronjob đang chạy.

- Mỗi cronjob chỉ có 1 execution tại một thời điểm.

### 3.3 Retry và lỗi

#### FR-08: Retry giới hạn

- Retry tối đa 1 lần hoặc không retry.

- Không retry liên tục.

#### FR-09: Xử lý lỗi

- Khi trigger thất bại, ghi nhận lỗi và kết thúc execution.

- Không block scheduler.

### 3.4 API public cho portal

#### FR-10: API quản lý cronjob

Portal có thể:

- Xem danh sách cronjob

- Xem chi tiết cronjob

- Tạo, cập nhật, bật/tắt, xóa cronjob

#### FR-11: Phân quyền

- Tuân theo cơ chế phân quyền chung của portal.

## 4. Format cấu hình cronjob

### 4.1 Cấu trúc JSON gợi ý

{

\"code\": \"sync_farm_status\",

\"description\": \"Đồng bộ trạng thái trang trại\",

\"cron_expression\": \"0 0 \* \* \*\",

\"active\": false,

\"target\": {

\"service\": \"farm-service\",

\"url\": \"/internal/v1/cron/sync-status\",

\"method\": \"POST\",

\"timeout_ms\": 5000

},

\"retry\": {

\"max_attempts\": 1

}

}

### 4.2 Rule cấu hình

- code là immutable.

- Không chứa secret dạng plain text.

- Payload (nếu có) là JSON tĩnh.

## 5. Yêu cầu phi chức năng (Non-Functional Requirements)

### 5.1 Độ tin cậy

- Cronjob lỗi không ảnh hưởng cronjob khác.

- Service restart không gây trigger hàng loạt.

### 5.2 Hiệu năng

- Trigger cronjob không blocking scheduler

- API CRUD phản hồi nhanh với P95 \<= 200ms.

### 5.3 Bảo mật

- Internal API chỉ gọi trong network nội bộ

- API public yêu cầu xác thực và phân quyền

### 5.4 Quan sát và logging

- Lưu:

  - last_run_at

  - last_run_status

  - duration_ms

  - last_error_message (ngắn)

- Không log payload nhạy cảm

## 6. Các giới hạn có chủ đích (Explicit Non-Goals)

Để giữ cho service đơn giản, bên dưới sẽ liệt kê các điểm **không cần
thiết** của service này.

- Không multi-instance / HA.

- Không workflow hoặc dependency giữa cronjob.

- Không manual trigger từ portal.

- Không queue phân tán.

## 7. Khả năng mở rộng trong tương lai

- Có thể nâng cấp:

  - Distributed lock

  - Worker pool

  - Retry policy nâng cao

  - Manual trigger có kiểm soát

- Không cần refactor lớn kiến trúc

## 8. Tiêu chí nghiệm thu tổng thể

- Cronjob được trigger đúng lịch

- Không xảy ra trigger trùng

- Portal quản lý cronjob an toàn

- DevOps có đủ thông tin để debug
