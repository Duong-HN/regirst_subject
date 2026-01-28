# 🐳 Docker Deployment Guide - Level 2 Architecture

## 📋 Yêu cầu

- **Docker Desktop** đã cài đặt và đang chạy
- **8GB RAM** trở lên (khuyến nghị)
- **Windows 10/11** với WSL2

## 🏗️ Kiến trúc

```
User (Client)
    ↓
API Gateway :8888
    ↓
┌─────────────┬─────────────┬─────────────┐
│             │             │             │
HAProxy       HAProxy       HAProxy
Auth :9001    Course :9002  Trans :9003
│             │             │
├─ Auth1      ├─ Course1    ├─ Trans1
├─ Auth2      ├─ Course2    ├─ Trans2
│             │             │
└─────────────┴─────────────┴─────────────┘
                    ↓
            MySQL Database :3306
```

**Tổng cộng: 11 containers**
- 1x MySQL
- 2x Auth Service
- 2x Course Service  
- 2x Transaction Service
- 3x HAProxy (mỗi service 1 cái)
- 1x API Gateway

## 🚀 Cách chạy

### Bước 1: Khởi động toàn bộ hệ thống

```bash
cd "c:\Users\DELL\Documents\2_2026\Ứng dụng phân tán\regist_subject"
docker-compose up --build
```

**Lần đầu sẽ mất 2-3 phút** (download images, build, khởi tạo DB)

### Bước 2: Kiểm tra trạng thái

Mở terminal mới:
```bash
docker-compose ps
```

Bạn sẽ thấy 11 containers đang chạy (State: Up)

### Bước 3: Chạy Client

```bash
cd client
python client.py
# Nhập IP: localhost (hoặc Enter)
```

### Bước 4: Xem Stats (Optional)

Mở trình duyệt:
- Auth HAProxy: http://localhost:8401/stats
- Course HAProxy: http://localhost:8402/stats
- Transaction HAProxy: http://localhost:8403/stats

## 🧪 Test Failover

### Test 1: Tắt 1 Auth Service
```bash
docker stop auth_1
```
→ Thử đăng nhập từ Client → **Vẫn hoạt động!** (HAProxy tự động dùng auth_2)

### Test 2: Bật lại
```bash
docker start auth_1
```
→ HAProxy tự động phát hiện và phân tải lại cho cả 2

### Test 3: Xem logs
```bash
docker logs -f api_gateway
docker logs -f haproxy_auth
docker logs -f auth_1
```

## 🛑 Dừng hệ thống

```bash
# Dừng tất cả (giữ data)
docker-compose down

# Dừng và XÓA data
docker-compose down -v
```

## 📊 Monitoring

### Xem resource usage
```bash
docker stats
```

### Xem logs của tất cả services
```bash
docker-compose logs -f
```

### Xem logs của 1 service cụ thể
```bash
docker-compose logs -f auth_service_1
docker-compose logs -f haproxy_auth
```

## 🔧 Troubleshooting

### Lỗi: Port already in use
```bash
# Kiểm tra port nào đang dùng
netstat -ano | findstr :8888
netstat -ano | findstr :3306

# Dừng container cũ
docker-compose down
```

### Lỗi: Cannot connect to MySQL
```bash
# Chờ MySQL khởi động xong (30s)
docker-compose logs mysql

# Hoặc restart
docker-compose restart mysql
```

### Rebuild từ đầu
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## 📈 Scale thêm instances

Muốn thêm Auth Service thứ 3? Sửa `docker-compose.yml`:

```yaml
auth_service_3:
  build: .
  container_name: auth_3
  command: python auth_service.py
  environment:
    - SERVICE_PORT=9001
    - DB_HOST=mysql
  ports:
    - "9013:9001"
  depends_on:
    mysql:
      condition: service_healthy
  networks:
    - course_network
```

Và thêm vào `docker/haproxy_auth.cfg`:
```
server auth3 auth_service_3:9001 check inter 3s rise 2 fall 3
```

Sau đó:
```bash
docker-compose up -d --build
```

## 🎯 Demo cho thầy

1. **Khởi động**: `docker-compose up`
2. **Mở Stats**: http://localhost:8401/stats (thầy thấy 2 Auth servers màu xanh)
3. **Client đăng nhập**: Thành công
4. **Tắt Auth1**: `docker stop auth_1` (Stats thấy Auth1 màu đỏ)
5. **Client đăng nhập lại**: **Vẫn thành công!** (Failover)
6. **Bật lại Auth1**: `docker start auth_1` (Stats thấy cả 2 màu xanh)

→ Chứng minh **High Availability** và **Fault Tolerance**!

## 💡 Lợi ích Docker

✅ **Cross-platform**: Chạy được trên Windows/Mac/Linux  
✅ **Isolated**: Mỗi service 1 container riêng  
✅ **Reproducible**: Ai chạy cũng giống nhau  
✅ **Easy cleanup**: `docker-compose down` là xóa sạch  
✅ **Production-like**: Giống môi trường thật  

## 🔗 Ports Summary

| Service | Port | URL |
|---------|------|-----|
| API Gateway | 8888 | localhost:8888 |
| Auth HAProxy | 9001 | localhost:9001 |
| Course HAProxy | 9002 | localhost:9002 |
| Transaction HAProxy | 9003 | localhost:9003 |
| MySQL | 3306 | localhost:3306 |
| Auth Stats | 8401 | http://localhost:8401/stats |
| Course Stats | 8402 | http://localhost:8402/stats |
| Transaction Stats | 8403 | http://localhost:8403/stats |
