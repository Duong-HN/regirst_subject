# HỎI ĐÁP BẢO VỆ ĐỒ ÁN - HỆ THỐNG ĐĂNG KÝ HỌC PHẦN PHÂN TÁN

Tài liệu này tổng hợp các câu hỏi thầy cô có thể hỏi và cách trả lời dựa trên kiến trúc thực tế của dự án.

## 1. VỀ KIẾN TRÚC & DOCKER (Architecture)

**Q1: Em hãy trình bày tổng quan kiến trúc hệ thống?**
> **Trả lời:**
> Hệ thống được thiết kế theo mô hình **Microservices** (Dịch vụ nhỏ) triển khai trên **Docker**. Luồng đi như sau:
> 1.  **Client (Sinh viên)** kết nối Socket đến **API Gateway**.
> 2.  **API Gateway** điều hướng yêu cầu đến lớp **Load Balancer (HAProxy)**.
> 3.  **HAProxy** chia tải (Round Robin) cho các cụm Service con (**Auth**, **Course**, **Transaction**).
> 4.  Các Service xử lý logic và truy xuất dữ liệu từ **MySQL Database** chung.

**Q2: Tính chất "Phân tán" (Distributed) của hệ thống thể hiện cụ thể ở đâu?**
> **Trả lời:**
> Thưa thầy, theo kiến trúc này, tính phân tán thể hiện ở việc **phân chia độc lập tài nguyên máy tính (CPU, RAM)**:
> 1.  **Cách ly tài nguyên (Resource Isolation):** Mỗi Service (Auth, Transaction...) được cấp phát một lượng CPU và RAM riêng biệt trong Container. Nếu module "Đăng nhập" bị lỗi tràn RAM, nó chỉ làm chết container đó chứ không kéo sập cả hệ thống (Module "Đăng ký" vẫn chạy vì dùng phần RAM khác).
> 2.  **Mở rộng linh hoạt (Scalability):** Em có thể dồn nhiều CPU/RAM cho phần quan trọng (như Transaction) bằng cách chạy nhiều bản sao (Replicas) của nó, trong khi phần nhẹ hơn thì cấp ít tài nguyên hơn.
> 3.  **Sẵn sàng cho đa máy:** Các container hiện tại tuy chạy chung 1 máy để Demo, nhưng cơ chế mạng TCP/IP cho phép chúng nằm rải rác trên các máy vật lý khác nhau, tận dụng tổng lực CPU/RAM của cả một phòng máy chứ không bị giới hạn bởi 1 máy đơn lẻ.

**Q3: Tại sao lại dùng Docker?**
> **Trả lời:**
> 1.  **Đóng gói môi trường:** Đảm bảo code chạy trên máy em và máy thầy là y hệt nhau, không bị lỗi thiếu thư viện.
> 2.  **Giả lập phân tán:** Có thể chạy 11 containers (máy ảo nhỏ) trên cùng 1 máy tính để mô phỏng một hệ thống phân tán thực tế gồm nhiều server.

**Q4: Vai trò của HAProxy là gì? Tại sao cần nó?**
> **Trả lời:**
> HAProxy đóng vai trò là **Load Balancer** (Cân bằng tải).
> *   Ví dụ: Nếu có 2 Auth Service, HAProxy sẽ chia đều request: người thứ nhất vào server 1, người thứ hai vào server 2.
> *   **Tác dụng:** Giúp hệ thống không bị quá tải cục bộ ở một server nào đó và tăng khả năng chịu lỗi (nếu 1 server chết, HAProxy tự chuyển sang server còn lại).

**Q5: Nếu Server đăng nhập (Auth Service) bị chết 1 cái thì người dùng có bị văng ra không? Hệ thống xử lý thế nào? (High Availability)**
> **Trả lời:**
> **Không, người dùng không bị ảnh hưởng gì cả.**
> *   **Cơ chế:** HAProxy liên tục "điểm danh" (Health Check) các server con 3 giây/lần.
> *   Khi `Auth-1` bị chết (hoặc tắt), HAProxy phát hiện ra ngay lập tức.
> *   Nó sẽ **tự động chuyển** toàn bộ người dùng mới sang `Auth-2` (Server dự phòng).
> *   Người dùng vẫn đăng nhập bình thường mà không hề hay biết server kia đã chết. Đây chính là tính năng **Chịu lỗi (Fault Tolerance)** của hệ thống.

---

## 2. VỀ KẾT NỐI & MẠNG (Networking)

**Q6: Làm sao Client từ máy khác kết nối được vào Server của em?**
> **Trả lời:**
> Client kết nối thông qua giao thức **TCP/IP**.
> *   Trên máy Server, Docker mở cổng **8888** ra ngoài mạng LAN.
> *   Máy Client chỉ cần nhập đúng **địa chỉ IPv4** của máy Server. Hệ thống mạng sẽ định tuyến gói tin đến đúng cổng 8888 đó.

**Q7: Tại sao Server trong Docker lại không gọi được `localhost`? (Liên quan đến lỗi Service Unavailable)**
> **Trả lời:**
> Trong môi trường Docker, `localhost` của container nào là chỉ chính container đó.
> *   API Gateway gọi `localhost:9001` nghĩa là nó tự gọi chính nó (mà nó không có cổng 9001).
> *   **Giải pháp:** Phải gọi bằng **Tên Service** (Service Name) được định nghĩa trong `docker-compose.yml` (ví dụ: `haproxy_auth`). Docker có sẵn DNS nội bộ để giải mã tên này thành IP đúng.

---

## 3. VỀ CHỊU TẢI & ĐỒNG BỘ (Concurrency & Consistency) - **Điểm nhấn**

**Q8: Nếu 1000 sinh viên cùng bấm "Đăng ký" một lúc thì hệ thống xử lý thế nào?**
> **Trả lời:**
> Hệ thống lọc và chặn tải qua 3 lớp phòng vệ:
> 1.  **Lớp 1 - Chia tải (HAProxy):** 1000 request được chia nhỏ ra cho nhiều Transaction Service xử lý song song.
> 2.  **Lớp 2 - Hàng chờ (Semaphore):** Tại mỗi Transaction Service, em dùng `Semaphore(5)`. Nghĩa là chỉ cho phép tối đa **5 luồng xử lý cùng lúc**. Những người còn lại phải xếp hàng chờ. Việc này tránh cho Server bị treo.
> 3.  **Lớp 3 - Khóa dữ liệu (Database Locking):** Cuối cùng khi ghi vào DB, em dùng lệnh `SELECT ... FOR UPDATE`.

**Q9: Nếu lớp chỉ còn 1 chỗ, mà 2 người cùng bấm đăng ký thì sao? (Race Condition)**
> **Trả lời:**
> Nhờ vào cơ chế **Row Locking (Khóa dòng)** của MySQL (`SELECT ... FOR UPDATE`):
> *   Khi người A đọc số chỗ trống, dòng dữ liệu đó bị KHÓA lại.
> *   Người B cũng muốn đọc nhưng phải **CHỜ** đến khi người A đăng ký xong và nhả khóa.
> *   Lúc người B đọc được thì số chỗ đã giảm đi 1 (hết chỗ) -> Người B sẽ nhận thông báo "Lớp đã đầy".
> -> **Đảm bảo tính toàn vẹn dữ liệu tuyệt đối.**

---

## 4. VẬN HÀNH & DEMO

**Q10: Làm sao để kiểm tra hệ thống đang chạy ổn định?**
> **Trả lời:**
> 1.  Dùng lệnh `docker-compose ps` để xem trạng thái các container (phải là Up).
> 2.  Truy cập trang thống kê của HAProxy (ví dụ: `localhost:8401/stats`) để thấy các chấm xanh (Server đang sống).
> 3.  Xem log thời gian thực bằng `docker-compose logs -f`.

**Q11: Nếu muốn thêm sức mạnh cho hệ thống thì làm thế nào? (Scaling)**
> **Trả lời:**
> Em chỉ cần sửa file `docker-compose.yml`, copy thêm `auth_service_3`, `auth_service_4`... và thêm vào config của HAProxy. Kiến trúc này cho phép mở rộng chiều ngang (Horizontal Scaling) rất dễ dàng.
