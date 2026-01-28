# Nội Dung Chi Tiết Slide Báo Cáo Đồ Án
## Đề tài: Hệ thống Đăng Ký Học Phần Phân Tán (Distributed Course Registration System)

---

### Slide 1: Trang Chào (Title Slide)
*   **Tiêu đề lớn**: HỆ THỐNG ĐĂNG KÝ HỌC PHẦN PHÂN TÁN
*   **Tiêu đề phụ**: Giải pháp Microservices & Transaction Locking
*   **Hình ảnh**: Logo trường, Tên môn học (Ứng dụng phân tán).
*   **Thông tin**: Giảng viên hướng dẫn, Sinh viên thực hiện.

> **Lời thoại (Speaker Notes):**
> "Kính thưa thầy và các bạn. Hôm nay em xin trình bày về đồ án 'Hệ thống Đăng ký học phần Phân tán'. Đây là giải pháp nhằm giải quyết bài toán nghẽn mạng kinh điển mỗi mùa đăng ký tín chỉ, bằng cách áp dụng kiến trúc phân tán hiện đại."

---

### Slide 2: Vấn đề & Động lực (Problem & Motivation)
*   **Thực trạng**:
    *   Hệ thống cũ (Monolithic) thường quá tải ("sập") khi hàng ngàn sinh viên truy cập cùng lúc.
    *   Nút cổ chai (Bottleneck) tại xử lý máy chủ.
*   **Yêu cầu cốt lõi**:
    *   **Chịu tải cao**: Chia nhỏ công việc để xử lý.
    *   **Tin cậy**: Không được phép sai sót dữ liệu (đăng ký lố sĩ số).
    *   **Mở rộng**: Dễ dàng thêm server khi cần.

> **Lời thoại:**
> "Chúng ta đều từng trải qua nỗi ám ảnh 'sập web' khi đăng ký môn. Nguyên nhân thường do kiến trúc tập trung không chịu nổi tải đột biến. Đồ án này đi tìm lời giải bằng cách phân tán tải ra nhiều nơi, thay vì dồn vào một chỗ."

---

### Slide 3: Kiến trúc Tổng quan (System Architecture)
*   **Mô hình**: Microservices (Containerized).
*   **Thành phần chính**:
    1.  **Client**: TCP Client (Python).
    2.  **Gateway (Port 8888)**: Cửa ngõ duy nhất.
    3.  **Load Balancers (HAProxy)**: 3 cụm cân bằng tải.
    4.  **Microservices**: Auth (2), Course (2), Transaction (2).
    5.  **Database**: MySQL Server.
*   **Hình ảnh**: *Sơ đồ kiến trúc từ file architecture.md (Graph Mermaid)*.

> **Lời thoại:**
> "Đây là kiến trúc tổng thể. Thay vì 1 cục server khổng lồ, em chia nhỏ thành các 'tiểu đội' chuyên biệt: Đội xác thực (Auth), Đội tra cứu (Course), và Đội xử lý đăng ký (Transaction). Traffic đi qua Gateway, được HAProxy chia đều cho các nhân viên này xử lý song song."

---

### Slide 4: Tại sao gọi là "Phân tán"? (Distributed Characteristics)
*   **Dù chạy trên 1 máy (Physical), nhưng Phân tán về Logic**:
    *   **Phân tán Xử lý (Process Isolation)**: Mỗi service là 1 Process (PID) riêng biệt. OS tự chia 6 PID này vào các nhân CPU khác nhau.
    *   **Phân tán Bộ nhớ (Memory Isolation)**: RAM của Service A độc lập hoàn toàn với Service B.
    *   **Trong suốt vị trí (Transparency)**: Các service giao tiếp qua mạng (Socket TCP), không quan tâm đang ở cùng máy hay khác máy.

> **Lời thoại:**
> "Một câu hỏi thường gặp: 'Chạy trên 1 máy thì phân tán chỗ nào?'. Thưa thầy, phân tán nằm ở bản chất kiến trúc. Em tách biệt hoàn toàn Bộ nhớ và Tiến trình. Nếu Service A bị lỗi tràn RAM và chết, Service B vẫn sống khỏe. Đó là tính chịu lỗi mà hệ thống tập trung không có."

---

### Slide 5: Thách thức: Race Condition (Tranh chấp dữ liệu)
*   **Bài toán**: Lớp học chỉ còn **1 chỗ trống**.
*   **Tình huống**: 2 sinh viên (A và B) bấm nút "Đăng ký" cùng lúc (mili-giây).
*   **Rủi ro**:
    1.  Cả 2 request đến 2 server khác nhau.
    2.  Cả 2 server đều đọc thấy "Còn 1 chỗ".
    3.  Cả 2 đều cho phép ghi danh -> **Lớp bị thừa 1 người (Over-enrollment)**.

> **Lời thoại:**
> "Thử thách lớn nhất của hệ phân tán là đồng bộ dữ liệu. Giả sử lớp còn đúng 1 chỗ, 2 bạn bấm cùng lúc. Nếu không khéo, hệ thống sẽ cho cả 2 vào, dẫn đến vỡ lớp. Đây là điều tối kỵ."

---

### Slide 6: Giải pháp Bảo vệ 3 Lớp (Deep Defense Strategy)
*   **Tầng 1 (App Layer): Semaphore Queue**
    *   Giới hạn **5 request/lúc** tại mỗi service.
    *   Tránh sập server do DDoS.
*   **Tầng 2 (DB Access): Connection Pool**
    *   Giới hạn **10 connection** tối đa.
    *   Tránh cạn kiệt tài nguyên Database.
*   **Tầng 3 (Data Layer): Transaction Locking (Quan trọng nhất)**
    *   Dùng `SELECT ... FOR UPDATE`.
    *   Khóa dòng dữ liệu ngay khi đọc.

> **Lời thoại:**
> "Để giải quyết, em dùng chiến thuật '3 Lớp Bảo Vệ'. Tầng 1 và 2 để bảo vệ Server không bị quá tải. Nhưng Tầng 3 mới là chốt chặn cuối cùng để bảo vệ dữ liệu."

---

### Slide 7: Cơ chế Transaction Locking (Chi tiết)
*   **Quy trình**:
    1.  Transaction 1: `BEGIN` -> `SELECT ... FOR UPDATE` (Khóa dòng).
    2.  Transaction 2: Muốn đọc dòng đó -> **Bị chặn (Blocked)** bởi MySQL.
    3.  Transaction 1: `UPDATE` -> `COMMIT` (Nhả khóa).
    4.  Transaction 2: Được phép chạy tiếp -> Đọc lại thấy "Hết chỗ" -> Báo lỗi.
*   **Kết quả**: Đảm bảo tính Nhất quán (Consistency) tuyệt đối.

> **Lời thoại:**
> "Cụ thể ở tầng 3, em dùng cơ chế Row Locking của MySQL. Ai đến trước thì khóa dòng dữ liệu môn học đó lại. Người đến sau bắt buộc phải đứng chờ cho đến khi người trước xong việc. Nhờ vậy, không bao giờ có chuyện 2 người cùng nhìn thấy 1 chỗ trống ảo."

---

### Slide 8: Công nghệ sử dụng
*   **Docker & Docker Compose**: Đóng gói môi trường, triển khai 1 lệnh (`up -d`).
*   **Python Socket**: Giao tiếp Low-level TCP, kiểm soát từng byte dữ liệu.
*   **HAProxy**: Load Balancer chuyên nghiệp, thuật toán Round Robin.
*   **MySQL**: Relational Database chuẩn ACID.

> **Lời thoại:**
> "Về công nghệ, em sử dụng Docker để giả lập môi trường phân tán thực tế. Python Socket được dùng để tối ưu hóa tốc độ truyền tải. HAProxy đóng vai trò điều phối viên thông minh."

---

### Slide 9: Demo Kịch bản (Demo Scenario)
*   **Bước 1**: Khởi động hệ thống (`docker-compose up`). Show 6 services đang chạy.
*   **Bước 2**: Đăng nhập bằng Client.
*   **Bước 3**: Xem danh sách môn học (Traffic chia đều qua 2 Course Services).
*   **Bước 4**: Thử nghiệm Đăng ký (Register) vào lớp gần đầy.
*   **Bước 5**: Kiểm tra Database để xác nhận dữ liệu đúng.

> **Lời thoại:**
> "Sau đây em xin demo. Em sẽ cho thấy request được chia đều cho các server như thế nào, và quan trọng nhất là dữ liệu cuối cùng trong Database hoàn toàn chính xác."

---

### Slide 10: Tổng kết & Hướng phát triển
*   **Đã làm được**:
    *   Hệ thống phân tán hoàn chỉnh, chạy ổn định trên Docker.
    *   Giải quyết triệt để bài toán Race Condition.
    *   Kiến trúc trong suốt, dễ mở rộng (Scale-out).
*   **Hạn chế**:
    *   Giao diện Console (CLI) chưa thân thiện.
*   **Hướng phát triển**:
    *   Xây dựng Web Client (React/Vue).
    *   Triển khai lên nhiều máy vật lý khác nhau (Cloud Deploy).

> **Lời thoại:**
> "Tổng kết lại, đồ án đã chứng minh được tính hiệu quả của kiến trúc Microservices trong việc xử lý tải cao và bảo vệ dữ liệu. Em xin cảm ơn thầy và các bạn đã lắng nghe."

---
