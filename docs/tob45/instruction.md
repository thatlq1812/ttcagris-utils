tob-45
[Tranning] Send deactive supplier event to app
send deactive supplier event to app

Đây là hướng dẫn và lưu ý để bắt đầu thực hiện task tob-45.

Sau khi đã hoàn thành luồng gửi thông báo từ noti-service đến app, ta sẽ tiếp tjc bổ sung luồng xử lý ngay trong hàm DeactivateSupplier của CAS, để sau khi hoàn thành việc deactive supplier, CAS sẽ gửi 1 notification đến noti-service để chuyển tiếp đến app, tiến hành deactive supplier trên app.

internal/grpc/supplier_server.go

```go
func (s *SupplierServer) DeactiveSupplier(ctx context.Context, req *pb.DeactiveSupplierRequest) (*pb.DeactiveSupplierResponse, error) {
	s.logger.Info("DeactiveSupplier request",
		zap.Int64("supplier_id", req.Id))

	// Call usecase to toggle is_active_supplier
	newIsActiveSupplier, err := s.supplierUsecase.DeactiveSupplier(ctx, req.Id)
	if err != nil {
		s.logger.Error("DeactiveSupplier failed",
			zap.Int64("supplier_id", req.Id),
			zap.Error(err))
		if errors.Is(err, customerrors.ErrNotFound) {
			return nil, status.Error(codes.NotFound, "supplier not found")
		}
		return nil, status.Error(codes.InvalidArgument, "failed to toggle supplier status")
	}

	s.logger.Info("DeactiveSupplier success",
		zap.Int64("supplier_id", req.Id),
		zap.Bool("is_active_supplier", newIsActiveSupplier))

	// PLACEHOLDER: SEND EVENT NOTIFICATION TO NOTI SERVICE - FOR FORCE LOGOUT IF DEACTIVATED

	return &pb.DeactiveSupplierResponse{
		Code:    "000",
		Message: "Supplier status toggled successfully",
		Data: &pb.DeactiveSupplierData{
			IsActiveSupplier: newIsActiveSupplier,
		},
	}, nil
}

```

pkg/grpcclient/notification_client.go
- Đây là nơi đang có sẵn một cái gì đó, kiểu như send otp, ta có thể tham khảo ở đây

Quá trình:

khi supplier bị deactive, CAS sẽ dùng ("supplier_id", req.Id) để tra cứu thông tin supplier, lấy được device_id, từ đó tra cứu sang firebase token, rồi gửi cùng với message deactive supplier đến noti-service.

Theo ghi nhận, ta có thể dùng D:\ttcagris\docs\tob37\TOB37_IMPLEMENTATION.md để tham khảo cấu hình gửi notification từ noti-service đến app, chỉ cần token, các nội dung còn lại là hardcode nên có thể cắt giảm.

Luồng hiện thực hóa: 
1. Khi admin toggle deactive supplier trên CAS, hàm DeactiveSupplier sẽ được gọi, sau khi deactive supplier thành công, CAS sẽ gọi grpc client của noti-service để gửi notification đến app, nội dung notification sẽ bao gồm firebase token lấy từ device_id của supplier, và message thông báo deactive supplier. ( Gắn 1 go func trong 1 go func khác là go routine để không block luồng chính, đây là định nghĩa được yêu cầu nghiên cứu)
2. Vì đầu vào noti-service đã dược xác định rõ ràng, nên ta chỉ cần implement grpc client trong CAS để gửi notification đến noti-service.
3. firebase token có thể lấy từ user id -> device id -> firebase token, ta có thể tham khảo luồng lấy firebase token từ user id trong grpc client của noti-service hiện có trong CAS.
4. Nội dung message gửi đến app có thể hardcode, ví dụ: "Your supplier account has been deactivated. Please contact support for more information.", chỉ có firebase token là động.

5. Luồng test sẽ là khởi động cas và ns, gọi api deactive supplier trên cas, kiểm tra app có nhận được notification và force logout hay không.

6. Khó khăn là: cơ chế account cần được implement luôn vào trong demo app, để đăng nhập, đăng xuất sẽ đúng cơ chế, tài khoản, device id, firebase token sẽ đúng với luồng thực tế.

7. Lưu ý, không chỉnh sửa code cũ đã có, không dùng icon hay emoji, không làm ảnh hưởng tới code đang có, chỉ implement thêm code mới.

7. demo app nằm tại D:\ttcagris\TOB-37\demo-mobile-app