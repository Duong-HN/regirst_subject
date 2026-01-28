# Chứng minh tính Phân Tán của Hệ thống

Hệ thống này là một **Hệ thống Phân tán (Distributed System)** dựa trên 3 bằng chứng kỹ thuật cụ thể trong code:

## 1. Phân tán về Thành phần (Component Distribution)
*   **Chi tiết**: Hệ thống tách biệt hoàn toàn giữa **Client** (người dùng) và **Server** (xử lý).
*   **Code chứng minh**:
    *   `server.py`: Mở cổng mạng (`server.bind`) và lắng nghe (`listen`).
    *   `client.py`: Chủ động kết nối từ xa (`socket.connect`).
    *   Chúng giao tiếp qua **Giao thức mạng TCP/IP**, có thể chạy trên 2 máy tính khác nhau hoàn toàn.

## 2. Phân tán về Xử lý (Processing Distribution)
*   **Chi tiết**: Server không xử lý tuần tự (người này xong mới tới người kia) mà xử lý **song song** (Concurrent).
*   **Code chứng minh**:
    *   File `request_handler.py` (Class `ClientThread`).
    *   Mỗi khi có Client kết nối, Server tạo một `Thread` mới riêng biệt để phục vụ. Điều này cho phép tận dụng tài nguyên CPU để xử lý nhiều yêu cầu cùng lúc.

## 3. Quản lý Tranh chấp Dữ liệu (Distributed Concurrency Control)
*   **Chi tiết**: Đặc trưng quan trọng nhất của hệ phân tán là nhiều tiến trình cùng truy cập một tài nguyên (Database) và gây ra xung đột (Race Condition).
*   **Code chứng minh**:
    *   File `database_manager.py` (Hàm `register_student`).
    *   Sử dụng câu lệnh `... FOR UPDATE` để **Khóa (Lock)** dòng dữ liệu môn học.
    *   Đảm bảo tại một thời điểm, chỉ **duy nhất** một tiến trình phân tán được phép sửa đổi số lượng đăng ký, ngăn chặn việc đăng ký quá sĩ số.
