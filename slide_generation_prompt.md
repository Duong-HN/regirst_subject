# Prompt Script: Tạo Slide Báo Cáo Đồ Án Nhúng & Phân Tán

**Hướng dẫn sử dụng:**
Copy toàn bộ nội dung trong block code bên dưới và dán vào ChatGPT (GPT-4) hoặc Gemini Advanced để tạo nội dung chi tiết cho slide PowerPoint.

---

```markdown
**Vai trò:**
Bạn là một Chuyên gia Kiến trúc Phần mềm và Hệ thống Phân tán (Distributed Systems Architect). Nhiệm vụ của bạn là giúp tôi soạn thảo nội dung trình bày (slides) cho buổi bảo vệ đồ án môn học "Ứng dụng Phân tán".

**Dữ liệu đầu vào (Thông tin dự án):**

1.  **Tên đề tài**: Hệ thống Đăng Ký Học Phần Phân Tán (Distributed Course Registration System).
2.  **Mục tiêu**: Xây dựng một hệ thống đăng ký môn học chịu tải cao, đảm bảo tính toàn vẹn dữ liệu (không đăng ký quá sĩ số) và có khả năng mở rộng.
3.  **Công nghệ**: Python (Socket), Docker (Containerization), MySQL (Database), HAProxy (Load Balancing).
4.  **Kiến trúc**: Microservices.
    *   **Gateway**: API Gateway (Port 8888) nhận mọi request, quản lý session.
    *   **Load Balancers**: 3 HAProxy instances điều phối traffic cho Auth, Course, và Transaction services.
    *   **Compute Nodes**: 6 instances (2 Auth, 2 Course, 2 Transaction) chạy song song (Distributed Processing).
    *   **Storage**: MySQL Database với Connection Pool.
5.  **Điểm nhấn kỹ thuật (Key Selling Points)**:
    *   **Mô hình In-memory Processing**: Mỗi service chạy tiến trình riêng biệt (Process Isolation) và bộ nhớ riêng biệt (Memory Isolation).
    *   **Cơ chế chống Race Condition 3 lớp**:
        1.  Application Layer: SemaphoreQueue (Max 5 concurrent requests).
        2.  DB Access Layer: Connection Pool (Max 10 connections).
        3.  Data Layer: Transaction Locking (`SELECT ... FOR UPDATE`).
    *   **Transparency**: Hệ thống trong suốt về vị trí (Location Transparency), chạy 1 máy hay nhiều máy code không đổi.

**Yêu cầu đầu ra:**
Hãy tạo cấu trúc cho bài thuyết trình gồm 10-12 slides. Với mỗi slide, hãy cung cấp:
1.  **Tiêu đề Slide** (Ngắn gọn, ấn tượng).
2.  **Nội dung chính trên Slide** (Dạng bullet points, súc tích, keywords).
3.  **Mô tả hình ảnh/sơ đồ** (Gợi ý nên vẽ hình gì để tôi đưa vào).
4.  **Lời thoại cho người thuyết trình (Speaker Notes)**: Kịch bản chi tiết tôi sẽ nói, văn phong tự tin, mang tính kỹ thuật cao, nhấn mạnh vào các từ khóa phân tán.

**Cấu trúc bài thuyết trình mong muốn:**
*   **Slide 1-2**: Giới thiệu & Vấn đề (Tại sao cần phân tán? Tại sao web trường hay sập khi đăng ký?).
*   **Slide 3-4**: Kiến trúc tổng thể & Công nghệ (Show sơ đồ Microservices).
*   **Slide 5-6**: Giải thích "Tính Phân Tán" trong dự án (Dù chạy 1 máy nhưng phân tán về Process/RAM thế nào).
*   **Slide 7-8**: Thách thức Race Condition & Giải pháp 3 lớp bảo vệ (Trọng tâm).
*   **Slide 9**: Demo Flow (Luồng chạy của 1 request đăng ký).
*   **Slide 10**: Kết luận & Hướng phát triển.

**Lưu ý quan trọng**:
*   Tập trung giải thích tại sao kiến trúc này **tốt hơn Monolithic**.
*   Các ví dụ so sánh đời thường (ví dụ: Cửa một người đi vs Cửa nhiều làn xe) để dễ hiểu.
*   Sử dụng tiếng Việt, văn phong học thuật nhưng dễ hiểu.
```
