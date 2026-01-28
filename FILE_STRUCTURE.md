# 🗂️ Cấu trúc Thư mục Sau khi Dọn dẹp

## ✅ Files CẦN THIẾT (Giữ lại)

```
regist_subject/
├── client/                    ← Client code
│   ├── client.py
│   └── network_client.py
│
├── server/                    ← Microservices
│   ├── database_manager.py   ← Shared DB utilities
│   ├── auth_service.py       ← Auth microservice
│   ├── course_service.py     ← Course microservice
│   ├── transaction_service.py← Transaction microservice
│   └── api_gateway.py        ← API Gateway
│
├── docker/                    ← HAProxy configs
│   ├── haproxy_auth.cfg
│   ├── haproxy_course.cfg
│   └── haproxy_transaction.cfg
│
├── setup_database/            ← Database init scripts
│   ├── schema.sql
│   └── architecture.md
│
├── Dockerfile                 ← Docker build instructions
├── docker-compose.yml         ← Orchestration config
├── .dockerignore             ← Docker ignore rules
├── DOCKER_README.md          ← Main documentation
└── README.md                 ← Project overview
```

## ❌ Files ĐÃ XÓA (Không cần nữa)

- ❌ `microservices_system/` - Folder thừa, đã gộp vào server/
- ❌ `haproxy.cfg` - Config cũ, thay bằng docker/haproxy_*.cfg
- ❌ `HAPROXY_GUIDE.md` - Hướng dẫn cũ, thay bằng DOCKER_README.md
- ❌ `server/start_microservices.bat` - Không dùng nữa (dùng docker-compose)

## 📦 Files ĐỔI TÊN (Lưu trữ)

- 📦 `server/server.py` → `server_OLD_monolithic.py.bak`
- 📦 `server/request_handler.py` → `request_handler_OLD.py.bak`

(Giữ lại để tham khảo kiến trúc Monolithic cũ)

## 🎯 Kết quả

Thư mục giờ **SẠCH SẼ** và **DỄ HIỂU**:
- Tất cả microservices trong `server/`
- Tất cả Docker config ở root
- Tất cả HAProxy config trong `docker/`
- Chỉ 1 file hướng dẫn chính: `DOCKER_README.md`
