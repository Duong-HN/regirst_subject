# Kiến trúc Microservices - Hệ thống Đăng ký Tín chỉ

## Cấu trúc thư mục

```
server/
├── server.py              ← [CŨ] Monolithic Server (Tất cả trong 1)
├── request_handler.py     ← [CŨ] Handler cho Monolithic
├── database_manager.py    ← [DÙNG CHUNG] Database utilities
│
├── auth_service.py        ← [MỚI] Service Đăng nhập (Port 9001)
├── course_service.py      ← [MỚI] Service Xem khóa học (Port 9002)
└── transaction_service.py ← [MỚI] Service Đăng ký (Port 9003)
```

## Kiến trúc Microservices với API Gateway

### 🚪 API Gateway (Port 8888)
**Chức năng**: Điểm vào duy nhất cho Client, routing request đến service phù hợp
- Nhận tất cả request từ Client
- Quản lý session (đăng nhập)
- Routing thông minh:
  - `LOGIN` → Auth Service (9001)
  - `LIST`, `MY_COURSES`, `GET_DETAILS` → Course Service (9002)
  - `REGISTER` → Transaction Service (9003)

### 🔐 Auth Service (Port 9001)
**Chức năng**: Xử lý đăng nhập
- `LOGIN|username|password` → Kiểm tra thông tin đăng nhập

### 📚 Course Service (Port 9002)
**Chức năng**: Xử lý xem thông tin khóa học
- `LIST` → Lấy danh sách tất cả môn học
- `MY_COURSES|username` → Lấy môn đã đăng ký
- `GET_DETAILS|section_id` → Xem chi tiết lớp học

### 💳 Transaction Service (Port 9003)
**Chức năng**: Xử lý đăng ký môn học
- `REGISTER|username|section_id` → Đăng ký môn
- **Có hàng chờ**: Tối đa 5 người đăng ký cùng lúc

## Cách chạy

### ⭐ Chạy với API Gateway (Khuyến nghị)

**Bước 1: Khởi động 3 Microservices (3 terminal)**

Terminal 1 - Auth Service:
```bash
cd server
python auth_service.py
```

Terminal 2 - Course Service:
```bash
cd server
python course_service.py
```

Terminal 3 - Transaction Service:
```bash
cd server
python transaction_service.py
```

**Bước 2: Khởi động API Gateway (terminal thứ 4)**
```bash
cd server
python api_gateway.py
```

**Bước 3: Chạy Client (terminal thứ 5)**
```bash
cd client
python client.py
# Nhập IP: localhost (hoặc Enter)
```

Client sẽ kết nối vào Gateway (8888), Gateway tự động routing!

### Chạy Monolithic (1 terminal)
```bash
cd server
python server.py
```

## So sánh

| Tiêu chí | Monolithic (server.py) | Microservices + Gateway |
|----------|------------------------|-------------------------|
| Số tiến trình | 1 | 4 (Gateway + 3 Services) |
| Client kết nối | 1 địa chỉ (8888) | 1 địa chỉ (8888 Gateway) |
| Triển khai | Phải deploy cả hệ thống | Deploy từng service riêng |
| Lỗi | 1 lỗi → Toàn bộ sập | 1 service lỗi → Gateway báo "Service Unavailable" |
| Scale | Phải scale toàn bộ | Scale riêng service cần thiết |
| Routing | Trong code | Gateway tự động routing |

## Ưu điểm Microservices

✅ **Độc lập**: Mỗi service chạy riêng, crash không ảnh hưởng nhau
✅ **Dễ scale**: Đăng ký đông → Chỉ cần thêm Transaction Service
✅ **Dễ maintain**: Sửa Auth không sợ ảnh hưởng Course
✅ **Công nghệ linh hoạt**: Mỗi service có thể dùng ngôn ngữ khác nhau
