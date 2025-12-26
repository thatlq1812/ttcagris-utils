# \[SRS\] Mobile App Quality of Service (QoS) Tracking -- MVP

- [1. Giới thiệu](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [1.1 Mục tiêu](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [1.2 Phạm vi](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [1.3 Đối tượng sử dụng](#id-[SRS]MobileAppQualityofService(QoS)T)

- [2. Nguyên tắc thiết kế](#id-[SRS]MobileAppQualityofService(QoS)T)

- [3. Bộ QoS Metrics tối thiểu
  (MVP)](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [3.1 Stability](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [M-01: Crash Rate](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [3.2 Performance](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [M-02: App Launch Time (Cold
      Start)](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [M-03: Screen Load Time (Critical
      Screens)](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [3.3 Reliability](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [M-04: API Error Rate
      (Client-side)](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [M-05: API Latency (p95,
      Client-side)](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [3.4 Context (để khoanh vùng nguyên
    nhân)](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [M-06: Network Type](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [M-07: Device
      Information](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [M-08: App Version](#id-[SRS]MobileAppQualityofService(QoS)T)

- [4. Yêu cầu chức năng (Functional
  Requirements)](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [4.1 Thu thập dữ liệu phía
    mobile](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [FR-01: Ghi nhận sự kiện
      QoS](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [FR-02: Gửi dữ liệu bất đồng
      bộ](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [FR-03: Sampling tại
      client](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [4.2 Backend tiếp nhận và xử
    lý](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [FR-04: API tiếp nhận QoS
      event](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [FR-05: Lưu trữ dữ liệu
      QoS](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [4.3 Tổng hợp và truy vấn cho mục đích kỹ
    thuật](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [FR-06: Tổng hợp metric](#id-[SRS]MobileAppQualityofService(QoS)T)

    - [FR-07: Truy vấn và
      drill-down](#id-[SRS]MobileAppQualityofService(QoS)T)

- [5. Yêu cầu phi chức năng (Non-Functional
  Requirements)](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [5.1 Hiệu năng](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [5.2 Độ tin cậy](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [5.3 Bảo mật & quyền riêng
    tư](#id-[SRS]MobileAppQualityofService(QoS)T)

  - [5.4 Khả năng vận hành](#id-[SRS]MobileAppQualityofService(QoS)T)

- [6. Các giới hạn có chủ đích (Explicit
  Non-Goals)](#id-[SRS]MobileAppQualityofService(QoS)T)

- [7. Tiêu chí nghiệm thu tổng
  thể](#id-[SRS]MobileAppQualityofService(QoS)T)

- [8. Định hướng mở rộng (không thuộc
  MVP)](#id-[SRS]MobileAppQualityofService(QoS)T)

## 1. Giới thiệu

### 1.1 Mục tiêu

Xây dựng hệ thống theo dõi **Quality of Service (QoS)** từ phía **mobile
app** nhằm:

- Phát hiện sớm các vấn đề ảnh hưởng đến trải nghiệm người dùng

- Khoanh vùng nguyên nhân kỹ thuật theo phiên bản app, thiết bị, mạng

- Hỗ trợ team kỹ thuật ra quyết định nhanh: điều tra, hotfix, rollback

Hệ thống **không phục vụ mục đích báo cáo quản trị hoặc KPI**.

### 1.2 Phạm vi

Áp dụng cho:

- Mobile app (Android, iOS)

**Không** bao gồm:

- Portal QoS

- Backend system monitoring

- Phân tích hành vi người dùng

- Báo cáo tổng hợp cho quản lý

### 1.3 Đối tượng sử dụng

- Backend Developer

- Mobile Developer

- QC / Vận hành kỹ thuật

- Engineering Manager

## 2. Nguyên tắc thiết kế

- **Client là nguồn dữ liệu chính (source of truth)**

- Thu thập dữ liệu **không làm ảnh hưởng UX**

- Ưu tiên **phát hiện xu hướng và bất thường**, không cần độ chính xác
  tuyệt đối

- Đo **ít nhưng đúng**, gắn với user flow quan trọng

- Hệ thống phục vụ **drill-down kỹ thuật**, không phải trình bày

## 3. Bộ QoS Metrics tối thiểu (MVP)

Tất cả các metric dạng **tỷ lệ** hoặc **percentile** (ví dụ crash rate,
error rate, p95 latency) đều là metric tổng hợp, được tính toán ở
backend dựa trên các sự kiện thô (raw events) do mobile app gửi lên.

### 3.1 Stability

#### M-01: Crash Rate

- Định nghĩa: Tỷ lệ phiên app kết thúc bằng crash. Được tính toán ở
  backend dựa trên số lượng **session start event** và **crash event**
  do mobile app gửi lên.

- Mục đích: Phát hiện release nguy hiểm

- Nguồn dữ liệu: Mobile client

### 3.2 Performance

#### M-02: App Launch Time (Cold Start)

- Định nghĩa: Thời gian từ lúc mở app đến khi màn hình đầu tiên usable

- Mục đích: Phát hiện regression hiệu năng tổng thể

#### M-03: Screen Load Time (Critical Screens)

- Định nghĩa: Thời gian load các màn hình quan trọng

- Phạm vi: 3--5 màn hình được cấu hình trước

- Mục đích: Xác định màn hình gây chậm

### 3.3 Reliability

#### M-04: API Error Rate (Client-side)

- Định nghĩa: Tỷ lệ request API từ app trả về lỗi hoặc timeout. Được
  tính toán ở Backend, mobile app gửi lỗi gọi API thuộc critical flow.

- Mục đích: Phân biệt lỗi backend và lỗi môi trường người dùng

#### M-05: API Latency (p95, Client-side)

- Định nghĩa: Thời gian phản hồi API đo từ client (percentile 95). Được
  tính toán ở Backend, mobile app gửi latency của từng lần gọi API thuộc
  critical flow.

- Phạm vi: API thuộc critical user flow

- Mục đích: Phát hiện API "bắt đầu chậm"

### 3.4 Context (để khoanh vùng nguyên nhân)

#### M-06: Network Type

- Giá trị: offline, 3G, 4G, 5G, WiFi

#### M-07: Device Information

- OS (Android / iOS)

- OS version

- Device model (lưu ý phân biệt với tên thiết bị). Ví dụ mong muốn:
  Samsung Galaxy A56, Apple iPhone 17 Pro Max,...

#### M-08: App Version

- Phiên bản ứng dụng đang sử dụng

**M-09: Signal Strength** (optional)

- Độ mạnh của sóng, giá trị theo OS. Bỏ qua nếu phải xin quyền hoặc OS
  không hỗ trợ

**M-10: RAM capacity** (optional)

- Dung lượng RAM của thiết bị. Đơn vị tính khuyến khích sử dụng Mega
  Byte

## 4. Yêu cầu chức năng (Functional Requirements)

### 4.1 Thu thập dữ liệu phía mobile

#### FR-01: Ghi nhận sự kiện QoS

- Mobile app phải ghi nhận các sự kiện tương ứng với M-01 → M-05

- Mỗi sự kiện **bắt buộc** kèm context **M-06 → M-08** và **tuỳ chọn**
  kèm context **M-09 → M-10**

- Mỗi sự kiện có timestamp chính xác

- Mỗi sự kiện cần được gán UUID do thiết bị tự sinh (để server xử lý
  trùng lặp)

#### FR-02: Gửi dữ liệu bất đồng bộ

- QoS event được gửi nền

- Không block user action

- Có thể gửi theo batch

#### FR-03: Sampling tại client

- Cho phép cấu hình sampling rate (ví dụ 5--10%)

- Sampling thực hiện trước khi gửi dữ liệu

### 4.2 Backend tiếp nhận và xử lý

#### FR-04: API tiếp nhận QoS event

- Backend cung cấp API để nhận QoS event

- Validate dữ liệu ở mức tối thiểu (schema, type)

- Không reject event vì thiếu field không quan trọng

- Backend cần ghi lại thời gian tiếp nhận

#### FR-05: Lưu trữ dữ liệu QoS

- Lưu dữ liệu theo dạng event

- Có khả năng tổng hợp theo:

  - Thời gian

  - App version

  - Network type

  - Device model

  - Screen / API name

### 4.3 Tổng hợp và truy vấn cho mục đích kỹ thuật

#### FR-06: Tổng hợp metric

- Backend tổng hợp metric theo cửa sổ thời gian (giờ/ngày)

- Tính:

  - Tỷ lệ (crash, error)

  - Percentile (p95 latency)

#### FR-07: Truy vấn và drill-down

- Cho phép truy vấn dữ liệu theo:

  - Khoảng thời gian

  - App version

  - Network type

  - Device model

  - Screen / API

- Ưu tiên tốc độ truy vấn hơn độ chính xác tuyệt đối

## 5. Yêu cầu phi chức năng (Non-Functional Requirements)

### 5.1 Hiệu năng

- Ghi nhận và gửi QoS event không ảnh hưởng UX

- Backend chịu được burst ngắn từ client

### 5.2 Độ tin cậy

- Mất một phần dữ liệu QoS được chấp nhận

- Không yêu cầu đảm bảo delivery 100%

### 5.3 Bảo mật & quyền riêng tư

- Không thu thập thông tin cá nhân người dùng

- Không log payload nghiệp vụ

- Dữ liệu chỉ dùng cho mục đích kỹ thuật

### 5.4 Khả năng vận hành

- Có log khi backend không nhận được QoS event

- Có thể phát hiện:

  - QoS giảm theo phiên bản app

  - Bất thường theo thiết bị hoặc mạng

## 6. Các giới hạn có chủ đích (Explicit Non-Goals)

- Không realtime streaming

- Không alert tự động ở MVP

- Không dashboard phục vụ quản lý

- Không SLA / SLO

- Không phân tích root-cause tự động

## 7. Tiêu chí nghiệm thu tổng thể

- QoS event được thu thập ổn định từ mobile app

- Team kỹ thuật phát hiện được vấn đề sớm hơn trước

- Có thể khoanh vùng nguyên nhân trong thời gian ngắn

- Hệ thống đơn giản, dễ vận hành

## 8. Định hướng mở rộng (không thuộc MVP)

- Alert theo ngưỡng

- So sánh QoS trước/sau release

- Mở rộng sang portal QoS

- Kết hợp backend metric để phân tích sâu hơn
