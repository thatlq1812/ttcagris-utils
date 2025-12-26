[Training] Map grpc supplier-service to web-gateway-api-service

supplier-service
- get list plant types
- get list stages
- get list units
- get list services
- create service
- update service

Requirements:
- Map gRPC to REST API, create curl commads for each rest api endpoint


Testing:
- Call from rest api endpoint using curl will forward to grpc

- map grpc to rest api
- mỗi rest api thì tạo curl tương ứng
- test: gọi từ rest api sẽ gọi qua service thông grpc

git@ssh.dev.azure.com:v3/agris-agriculture/Gateway/web-api-gateway

git@ssh.dev.azure.com:v3/agris-agriculture/Marketplace/supplier-service