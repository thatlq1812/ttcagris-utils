- Cách sử dụng dbeaver => các câu sql cơ bản
- Cách sử dụng postman => gọi rest api, grpc, viết script
- Cách sử dụng docker + docker-compose
- Cách sử dụng Firebase Cloud Messaging (FCM)
Mục tiêu:
- Sử dụng FCM để bắn event qua mobile app, từ đó mobile app sẽ có action tiếp theo khi nhận event đó
- Ví dụ: Khi update 1 supplier sẽ bắn event với nội dung là update abcd.... + action là update + target object là supplier đến mobile app. Mobile app nhận được event này sẽ chuyển màn hình hiện tại sang đến trang update supplier để user có thể update.
- NOTE:
 + Có thể sử dụng cách khác mà không sử dụng FCM
 + Không sử dụng websocket vì tốn nhiều tài nguyên
 + Sử dụng cách nào mà mobile app không cần giữ kết nối liên tục với server
 + Chỉ cần cận realtime
 + Tìm cách để test lại tính năng này khi đã implement (kím cách nào để tạo cái mobile app và gọi qua test thử)

Pritority to push event when user is using app, for near realtime experience.

So, the implementation steps should include:

1. Choose the context of demo mobile app (e.g., supplier management).
2. Implement FCM integration in the mobile app to receive events.
3. Connect the backend service to send events via FCM when relevant actions occur (e.g., supplier update).

Careful about: DO NOT CHANGE ANY EXISTING PART OF THE [noti-service], can implement but not change anything having done before in noti-service and others.

Next: Instead of sepherate docker service, NEED TO build compose docker file to include noti-service + other services if needed for testing.