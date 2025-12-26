# Quy trình Quản lý Công việc

  ---------------------------------------------------
  **Phiên   **Người tạo**  **Ngày cập   **Thay đổi**
  bản**                    nhật**       
  --------- -------------- ------------ -------------
  1.0       Trần Đăng      16 Dec 2025  Khởi tạo tài
            Quang                       liệu.

                                        
  ---------------------------------------------------

Tài liệu này mô tả vắn tắt các định nghĩa, quy tắc, quy trình công việc
được áp dụng tại phòng Phát triển Phần mềm.

Các thành viên mới khi tham gia vào dự án, cần xem trước để thực hiện
cho đúng.

**Quy trình phát triển phần mềm**: sử dụng **Agile/Scrum**. Thời hạn của
mỗi sprint phụ thuộc vào quyết định của trưởng dự án và theo từng giai
đoạn cụ thể của dự án. Ở thời điểm hiện tại, thời hạn một sprint là **1
tuần**.

**Quản lý công việc**: công việc của phòng Phát triển Phần mềm (SD) được
quản lý theo các task. Định nghĩa, cấu trúc, thuộc tính, quan hệ,... của
các task chủ yếu sử dụng theo định nghĩa của Atlassian Jira.

**Spaces**: dự án sẽ có một space chung để quản lý công việc do product
owner (PO) quản lý. Hiện tại là **AgriOS Platform**. Các thành viên của
SD không làm việc trực tiếp trên space này mà sử dụng space **Tech
Board**. Công việc tại Tech Board sẽ được người quản lý tạo dựa trên
thông tin tại AgriOS Platform và nhập vào trước khi bắt đầu sprint.

**Phân cấp task**: sử dụng phân cấp chuẩn của Jira theo thứ tự Epic →
Task → Sub-task (không sử dụng story).

- **Epic**: tương ứng với story tại space AgriOS Platform.

- **Task**: các đầu việc cần thực hiện để hoàn thành một epic. Công việc
  của dự án tại space Tech Board như lập kế hoạch, báo cáo, theo dõi
  tiến độ, ... đều thực hiện trên đơn vị là task. Nhân sự phụ trách
  (assignee) cũng sẽ làm việc trên đơn vị này. Task luôn thuộc về duy
  nhất một epic. Epic sẽ hoàn thành khi tất cả các task hoàn thành.

- **Sub-task**: các thành phần của task do assignee tự phân chia và quản
  lý ở cấp độ cá nhân, tùy ý sử dụng theo nhu cầu. Sub-task được quản lý
  theo quy tắc chung của hệ thống Jira. Lưu ý: **Sub-task** không ảnh
  hưởng tới trạng thái của Task và **không được dùng để đánh giá tiến
  độ** sprint.

**Quy tắc đặt tên epic**: \[Dev\] + Tên epic.

> \[Dev\]: là tiền tố cố định.
>
> Tên epic: khuyến khích sử dụng tên của story tương ứng tại space
> AgriOS Platform.

**Quy tắc đặt tên task**: \[Platform\] + Tên task.

> \[Platform\]: bao gồm API, Mobile, Portal, và các platform khác có thể
> phát sinh trong tương lai.
>
> Tên task: mô tả ngắn gọn và phạm vi của công việc.

**Trạng thái của task**: TODO, In-Progress, In-Review, Done.

- TODO: task chưa thực hiện.

> Trước khi thực hiện, lập trình viên (LTV) cần lưu ý kiểm tra field
> *assignee* phải là **tên của mình**.
>
> Khi LTV bắt đầu thực hiện task, chuyển trạng thái sang In-Progress.

- In-Progress: task đang được thực hiện.

> Khi LTV đã hoàn thành xong task (lập trình và kiểm tra trên môi trường
> DEV), chuyển trạng thái sang In-Review.

- In-Review: task đã hoàn thành, đang trong giải đoạn thiết lập cho kiểm
  thử.

> Đây là trạng thái trung gian, chuẩn bị cho quá trình kiểm thử (nếu
> có).
>
> Tại đây, LTV tiến hành chuẩn bị, tập hợp các thông tin cần thiết để
> gửi sản phẩm của mình cho QC, chẳng hạn như: SIT giữa backend và
> frontend, build code lên môi trường TESTING, chuẩn bị các tài liệu kỹ
> thuật/API, ... Cuối cùng, kiểm tra các tiêu chí hoàn thành (DoD) bên
> dưới, nếu đã thỏa mãn tất cả, chuyển trạng thái sang Done.
>
> **Lưu ý**: nếu task không yêu cầu QC/ ngoài phạm vi của QC thì bước
> In-Review này tự người làm task thực hiện và chuyển sang Done khi
> xong.

- Done: task đã hoàn thành.

> *Assignee* giữ nguyên tên của người thực hiện task.

Luồng chuẩn

TODO → In-Progress → In-Review → Done

Việc cập nhật trạng thái của task do duy nhất người làm task (assignee)
thực hiện.

Tiêu chí hoàn thành (Definition of Done - DoD):

- Đã merge vào main tất cả code.

- Đã build thành công lên môi trường DEV.

- Đã tạo brand release.

- Đã build brand release lên môi trường TESTING.

- Đã tạo tài liệu kỹ thuật/API.

- (Nếu có) Đã có đủ dữ liệu khởi tạo trên TESTING.

- (Nếu có) Đã gửi build cho QC.

![](media/image1.tmp){width="4.875in" height="1.95in"}

**Gửi build**: là thao tác một LTV gửi các tính năng mà mình đã phát
triển xong cho đội QC để nhờ kiểm tra lại chất lượng.

- Nơi gửi build: gửi vào channel **\[AgriOS\]\_QC_Builds** và chọn
  thread tương ứng trên Microsoft Teams gồm có:

  - \[BUILD\]BE-QC: dành cho tính năng backend.

  - \[BUILD\]Mobile App - QC: dành cho tính năng mobile.

  - \[BUILD\]WEB - QC: dành cho tính năng website.

![](media/image2.tmp){width="3.966666666666667in" height="3.05in"}

- Thông tin cần thiết khi gửi build:

  - Tên tính năng: khuyến khích sử dụng tên task.

  - Thông tin task trên Jira.

  - Phạm vi của tính năng: các phần thêm mới hoặc thay đổi, các phần bị
    ảnh hưởng.

  - Tài liệu kỹ thuật tương ứng với tính năng (nếu có)

  - Thông tin cần thiết để kiểm thử: API collection, đường dẫn website,
    file APK để cài đặt app,...

![](media/image3.tmp){width="4.875in" height="1.65in"}

**Trách nhiệm tạo task**:

- Người quản lý: tạo epic và task.

- Thành viên: tạo sub-task.

**Xử lý ngoại lệ**:

- Bug phát sinh trong sprint sẽ không được tính vào effort của sprint,
  nhân sự tự sắp xếp để sửa. Bug được quản lý trên space của QC, không
  copy về space của SD.

- Tất cả các task ad-hoc, không liên quan đến sprint không tạo trong
  space của SD mà tạo trong space vận hành Tech Operation Board.

- Khi task đã chuyển sang Done thì không được chuyển ngược lại các trạng
  thái khác, nếu có thay đổi hoặc cập nhật thì tạo task mới và link vào
  task hiện tại.

**Giao tiếp trên task**:

- Mọi trao đổi liên quan đến task cần phải được comment tường minh trong
  task tại space chính AgriOS Platform để tất cả các nhóm liên quan của
  dự án có thể đọc được.

- Tất cả các tin nhắn riêng đều chỉ để tham khảo, KHÔNG được phép sử
  dụng như mô tả chính thức của task mà không có sự xác nhận của các bên
  liên quan. Sau khi được xác nhận cũng cần comment rõ ràng trong task.

to be continue...
