# Cấu trúc Phòng Phát triển Phần mềm

  ---------------------------------------------------
  **Phiên   **Người tạo**  **Ngày cập   **Thay đổi**
  bản**                    nhật**       
  --------- -------------- ------------ -------------
  1.0       Trần Đăng      08 Dec 2025  Khởi tạo tài
            Quang                       liệu.

                                        
  ---------------------------------------------------

1.  **Chức năng nhiệm vụ**

**Phát triển** và **vận hành** các giải pháp phần mềm phục vụ cho dự án
AgriOS. Đảm bảo hệ thống được xây dựng đúng với các yêu cầu nghiệp vụ,
đáp ứng đầy đủ tiêu chuẩn kỹ thuật hiện đại trong ngành công nghiệp phần
mềm.

2.  **Cơ cấu tổ chức**

+---------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------------+
| **Nhóm chức   | **Nhiệm vụ đảm nhận**                      | **Thành viên**                                                                                            |
| năng**        |                                            |                                                                                                           |
+===============+============================================+===========================================================================================================+
| **Mobile      | Phát triển và vận hành ứng dụng di động    | [Trần Thị Hằng                                                                                            |
| application** | cho dự án AgriOS trên 02 nền tảng là iOS   | Nga](https://gmbc.atlassian.net/wiki/people/712020:9d1ea775-3602-4d9b-a240-5a2f39e42661?ref=confluence)   |
|               | và Android.                                |                                                                                                           |
|               |                                            | [Ngô Công                                                                                                 |
|               |                                            | Dũng](https://gmbc.atlassian.net/wiki/people/712020:3f7b553b-5373-4826-8667-5b588a6c53c6?ref=confluence)  |
+---------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------------+
| **Frontend**  | Phát triển và vận hành các website cho dự  | [Trần Phú                                                                                                 |
|               | án AgriOS.                                 | Quý](https://gmbc.atlassian.net/wiki/people/712020:7924a3ac-3b1b-4d21-9393-74fdf7e38ec4?ref=confluence)   |
|               |                                            |                                                                                                           |
|               | - Operation hub portal.                    | [Phạm Minh                                                                                                |
|               |                                            | Tiến](https://gmbc.atlassian.net/wiki/people/712020:61204e31-a644-4f5d-ae6b-60d2682d8e2a?ref=confluence)  |
|               | - Sale portal.                             |                                                                                                           |
|               |                                            |                                                                                                           |
|               | - AgriOS landing page.                     |                                                                                                           |
+---------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------------+
| **Backend**   | Phát triển và vận hành hệ thống API /      | [Diệp Chí                                                                                                 |
|               | services xử lý logic nghiệp vụ tại server. | Cường](https://gmbc.atlassian.net/wiki/people/712020:0e3dd0d8-90b5-4af7-b992-dc5005663128?ref=confluence) |
|               |                                            |                                                                                                           |
|               |                                            | [Lê Văn                                                                                                   |
|               |                                            | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
|               |                                            |                                                                                                           |
|               |                                            | [Nguyễn Đăng Phúc                                                                                         |
|               |                                            | Lợi](https://gmbc.atlassian.net/wiki/people/712020:0e669b45-e98d-4c74-a83f-4a2f0db84e8e?ref=confluence)   |
|               |                                            |                                                                                                           |
|               |                                            | [Trần Tiến                                                                                                |
|               |                                            | Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   |
+---------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------------+
| **DevOps**    | Xây dựng và vận hành hệ thống hạ tầng ổn   | [Nguyễn Minh                                                                                              |
|               | định, tự động, tối ưu chi phí.             | Duy](https://gmbc.atlassian.net/wiki/people/712020:91bbc30a-b687-428c-84e7-67703f2633e6?ref=confluence)   |
|               |                                            |                                                                                                           |
|               |                                            | [Hoàng Văn                                                                                                |
|               |                                            | Anh](https://gmbc.atlassian.net/wiki/people/712020:8de7c17d-e8d7-4b3c-a06f-430aab853491?ref=confluence)   |
+---------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------------+
| **Quản lý     | Quản lý lịch biểu, hỗ trợ kỹ thuật và giúp | [Trần Đăng                                                                                                |
| chung**       | giải quyết các vấn đề phát sinh.           | Quang](https://gmbc.atlassian.net/wiki/people/712020:ad3ae34a-9ca8-4605-b129-1590f793961f?ref=confluence) |
+---------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------------+

3.  **Danh sách service owner**

Hệ thống backend AgriOS sẽ được xây dựng theo hướng mini/microservice.
Mỗi service sẽ có một service owner chịu trách nhiệm chính cho service
đó.

Service owner là người **chịu trách nhiệm** chính cho **chất lượng hoạt
động, độ ổn định** của service đó.

Service owner có phần lớn quyền hạn với service mà mình quản lý như:
quyền merge code; quyền xem log vận hành; quyền quyết định cấu trúc
codebase, công nghệ sử dụng; ...

Đối với các application platform do tính chất khác biệt nên sẽ không có
service owner.

+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| **No.** | **Tên service**          | **Owner**                                                                                                 |
+=========+==========================+===========================================================================================================+
| 1       | agrios-portal            | [Phạm Minh                                                                                                |
|         |                          | Tiến](https://gmbc.atlassian.net/wiki/people/712020:61204e31-a644-4f5d-ae6b-60d2682d8e2a?ref=confluence)  |
|         |                          |                                                                                                           |
|         |                          | [Trần Phú                                                                                                 |
|         |                          | Quý](https://gmbc.atlassian.net/wiki/people/712020:7924a3ac-3b1b-4d21-9393-74fdf7e38ec4?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 2       | agrios-sale-portal       | [Trần Phú                                                                                                 |
|         |                          | Quý](https://gmbc.atlassian.net/wiki/people/712020:7924a3ac-3b1b-4d21-9393-74fdf7e38ec4?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 3       | agrios-webview           | [Phạm Minh                                                                                                |
|         |                          | Tiến](https://gmbc.atlassian.net/wiki/people/712020:61204e31-a644-4f5d-ae6b-60d2682d8e2a?ref=confluence)  |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 4       | app-api-gateway          | [Lê Văn                                                                                                   |
|         |                          | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 5       | area-hub-service         | [Lê Văn                                                                                                   |
|         |                          | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 6       | article-service          | [Trần Tiến                                                                                                |
|         |                          | Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 7       | cart-service             | [Lê Văn                                                                                                   |
|         |                          | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 8       | centre-auth-service      | [Nguyễn Đăng Phúc                                                                                         |
|         |                          | Lợi](https://gmbc.atlassian.net/wiki/people/712020:0e669b45-e98d-4c74-a83f-4a2f0db84e8e?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 9       | common-service           | [Lê Văn                                                                                                   |
|         |                          | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 10      | file-upload-service      | [Trần Tiến                                                                                                |
|         |                          | Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 11      | finance-service          | [Lê Văn                                                                                                   |
|         |                          | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 12      | frm-connector-service    | [Diệp Chí                                                                                                 |
|         |                          | Cường](https://gmbc.atlassian.net/wiki/people/712020:0e3dd0d8-90b5-4af7-b992-dc5005663128?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 13      | mequip-service           | [Trần Tiến                                                                                                |
|         |                          | Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 14      | noti-service             | [Trần Tiến                                                                                                |
|         |                          | Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 15      | order-service            | [Lê Văn                                                                                                   |
|         |                          | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 16      | product-service          | [Trần Tiến                                                                                                |
|         |                          | Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 17      | user-event-service       | [Trần Tiến                                                                                                |
|         |                          | Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 18      | vn-location-service      | [Trần Tiến                                                                                                |
|         |                          | Đạt](https://gmbc.atlassian.net/wiki/people/712020:e3daa6d5-e9b7-4b92-8fde-f8c47662e89c?ref=confluence)   |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 19      | weather-service          | [Phạm Minh                                                                                                |
|         |                          | Tiến](https://gmbc.atlassian.net/wiki/people/712020:61204e31-a644-4f5d-ae6b-60d2682d8e2a?ref=confluence)  |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 20      | web-api-gateway          | [Lê Văn                                                                                                   |
|         |                          | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 21      | web-api-gateway-consumer | [Lê Văn                                                                                                   |
|         |                          | Thiết](https://gmbc.atlassian.net/wiki/people/712020:6fc4e2b5-09c8-45dd-9f00-fc41e2b385f1?ref=confluence) |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
| 22      |                          |                                                                                                           |
+---------+--------------------------+-----------------------------------------------------------------------------------------------------------+
