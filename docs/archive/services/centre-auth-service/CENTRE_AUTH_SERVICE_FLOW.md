**CENTRE_AUTH_SERVICE_FLOW**

**Flow 1: Đăng Ký (Registration)**

![](media/image1.png){width="6.263888888888889in" height="7.9875in"}

### Kịch bản 1 (SC1): Luồng Đăng Ký (Full Flow)

Mỗi \"User\" trong kịch bản này sẽ thực hiện 4 bước (4 request) liên
tiếp.

- **Thành phần chịu tải:** API-APP-GATEWAY, CENTRE-AUTHEN-SERVICE,
  PostgreSQL (WRITE/READ).

#### Luồng đi của API (API Sequence)

1.  **Step 1: Check Phone**

    - **Call:** POST /api/v1/cas/auth/check-phone

    - **Data:** { \"phone\": \"USER_DATA_PHONE\" } (Lấy từ data pool)

    - **Validate:** Nhận 200 OK (Phone chưa tồn tại).

> *curl \--location
> \'https://dev-api.agrios.vn/app/api/v1/cas/auth/check-phone\' \\*
>
> *\--data \'{*
>
> *\"phone_number\": \"0375625474\"*
>
> *}\'*

2.  **Step 2: Send OTP**

    - **Call:** POST /api/v1/cas/auth/otp-register

    - **Data:** { \"phone\": \"USER_DATA_PHONE\" } (Dùng lại SĐT ở Step
      1)

    - **Validate:** Nhận 200 OK.

> curl \--location
> \'https://dev-api.agrios.vn/app/api/v1/cas/auth/otp-register\' \\
>
> \--data \'{
>
> \"phone_number\": \"0375625486\"
>
> }
>
> \'

3.  **Step 3: Check OTP**

    - **Call:** POST /api/v1/cas/auth/check-otp

    - **Data:** { \"phone\": \"USER_DATA_PHONE\", \"otp\": \"999999\" }
      (Dùng SĐT ở Step 1 và mã OTP Bypass)

    - **Validate:** Nhận 200 OK (OTP hợp lệ).

> curl \--location
> \'https://dev-api.agrios.vn/app/api/v1/cas/auth/check-otp\' \\
>
> \--data \'{
>
> \"phone_number\": \"0375625486\",
>
> \"otp_code\": \"664807\",
>
> \"purpose\": \"register\"
>
> }\'

4.  **Step 4: Register**

    - **Call:** POST /api/v1/cas/auth/register

    - **Data:** { \"phone\": \"USER_DATA_PHONE\", \"pin\": \"123456\",
      \"full_name\": \"Test User\" \... }

    - **Validate:** Nhận 201 Created.

> curl \--location
> \'https://dev-api.agrios.vn/app/api/v1/cas/auth/register\' \\
>
> \--data \'{
>
> \"phone_number\": \"0375625486\",
>
> \"pin\": \"111111\",
>
> \"otp_id\": \"185927dc-aa57-4d94-88ce-2c3c36d0c0b9\",
>
> \"device_info\": {
>
> \"firebase_token\": \"fcm_token_abc123\",
>
> \"device_id\": \"device_unique_id\",
>
> \"device_type\": \"android\",
>
> \"device_name\": \"Samsung Galaxy A30\",
>
> \"os_version\": \"Android 13\",
>
> \"app_version\": \"1.0.0\"
>
> }
>
> }
>
> \'

### Flow 2: Onboarding Farmer

### Kịch bản 2 (SC2): Luồng Onboarding Farmer (Full Flow)

Kịch bản này giả định User đã \"Đăng Ký\" (từ SC1) và bây giờ thực hiện
Login và Onboard.

- **Thành phần chịu tải:** API-APP-GATEWAY, CENTRE-AUTHEN-SERVICE,
  PostgreSQL (WRITE/READ), EKYC-Mock-Service.

#### Luồng đi của API (API Sequence)

1.  **Step 1: Login**

    - **Data:** Dữ liệu User (phone, pin) phải là user đã tồn tại (từ
      SC1 hoặc data chuẩn bị trước) nhưng **chưa** onboarding.

    - **Call:** POST /api/v1/cas/auth/login

    - **Validate:** Nhận 200 OK và trích xuất (extract) access_token từ
      response.

> curl \--location
> \'https://dev-api.agrios.vn/app/api/v1/cas/auth/login\' \\
>
> \--data \'{
>
> \"phone_number\": \"0395075456\",
>
> \"pin\": \"111111\",
>
> \"device_info\": {
>
> \"firebase_token\": \"fcm_token_abc123\",
>
> \"device_id\": \"device_unique_id\",
>
> \"device_type\": \"android\",
>
> \"device_name\": \"Samsung Galaxy S23\",
>
> \"os_version\": \"Android 13\",
>
> \"app_version\": \"1.0.0\"
>
> }
>
> }
>
> \'

2.  **Step 2: Ekyc**

    - **Call:** POST /api/v1/cas/ekyc/id/verify

    - **Header:** Đính kèm Authorization: Bearer \<access_token\> (lấy
      từ Step 1).

    - **Data:** { \"cccd\": \"USER_DATA_CCCD\" \... }

    - **Validate:** Nhận 200 OK (Service đã gọi EKYC Mock thành công).

> curl \--location
> \'https://dev-api.agrios.vn/app/api/v1/cas/ekyc/id/verify\' \\
>
> \--data \'{
>
> \"cccd\": \"044195000xxx\",
>
> \"dg1\": \"111111\",
>
> \"dg13\": \"111111\",
>
> \"dg2\": \"111111\",
>
> \"sod\": \"111111\"
>
> }
>
> \'

3.  **Step 3.1: Check Consent**

    - **Call:** GET /api/v1/cas/consents

    - **Header:** Đính kèm Authorization: Bearer \<access_token\>.

    - **Validate:** Nhận 404 Not Found (Giả định user này chưa có
      consent).

> curl \--location
> \'https://dev-api.agrios.vn/app/api/v1/cas/consents?consent_type=share_frm_data\'
> \\
>
> \--data \'\'

4.  **Step 3.2: Create Consent**

    - **Call:** CREATE /api/v1/cas/consents

    - **Header:** Đính kèm Authorization: Bearer \<access_token\>.

    - **Validate:** Nhận 201 Created.

> curl \--location \'https://dev-api.agrios.vn/app/api/v1/cas/consents\'
> \\
>
> \--data \'
>
> {
>
> \"consent_type\": \"share_frm_data\",
>
> \"policy_type_id\": 1
>
> }
>
> \'

5.  **Step 4: Check FRM**

    - **Call:** POST /api/v1/cas/frm-farmers/check

    - **Header:** Đính kèm Authorization: Bearer \<access_token\>.

    - **Validate:** Nhận 200 OK và response (ví dụ: {\"is_frm\":
      false}).

> curl \--location
> \'https://dev-api.agrios.vn/app/api/v1/cas/frm-farmers/check\' \\
>
> \--data \'\'

6.  **Step 5: Create Farmer (Giả định kịch bản \"No FRM\")**

    - **Call:** POST /api/v1/cas/farmers

    - **Header:** Đính kèm Authorization: Bearer \<access_token\>.

    - **Data:** { \"survey_data\": \"\...\" } (Dữ liệu khảo sát)

    - **Validate:** Nhận 201 Created.

> curl \--location \'https://dev-api.agrios.vn/app/api/v1/cas/farmers\'
> \\
>
> \--data \'{
>
> \"agricultural_officer\": \"Nguyễn Văn A\",
>
> \"area\": 15.5,
>
> \"avarta_url\": \"https://example.com/images/avatar/24761.jpg\",
>
> \"crop_types\": \[\"Mía\", \"Lúa\", \"Bắp\"\],
>
> \"cultivated_area\": {
>
> \"address\": \"83 nguyễn văn đậu\",
>
> \"district\": {
>
> \"id\": \"1\",
>
> \"value\": \"Gò vấp\"
>
> },
>
> \"province\": {
>
> \"id\": \"2\",
>
> \"value\": \"Ho Chi Minh\"
>
> },
>
> \"ward_commune\": {
>
> \"id\": \"2\",
>
> \"value\": \"Phường 3\"
>
> }
>
> },
>
> \"customer_code\": \"24761\",
>
> \"customer_group\": \"Nhóm khách hàng Bạc\",
>
> \"customer_type\": \"Nông dân\",
>
> \"img_back_url\":
> \"https://example.com/images/idcard/24761_back.jpg\",
>
> \"img_front_url\":
> \"https://example.com/images/idcard/24761_front.jpg\",
>
> \"investment_area\": \"Miền Đông\",
>
> \"investment_programs\": \[\"Hỗ trợ giống\", \"Vay vốn lãi suất ưu
> đãi\"\],
>
> \"investment_zone\": \"Khu vực Tây Ninh\",
>
> \"status\": \"Chính thức\",
>
> \"is_skip\": false
>
> }
>
> \'

### 

![](media/image2.png){width="5.985416666666667in"
height="9.694444444444445in"}
