# Giải đáp: Phân tán ở đâu? Ram & Tài nguyên phân tán thế nào?

Bạn hỏi rất đúng trọng tâm. Khi chạy 3 server trên 1 máy tính để demo, thầy cô thường sẽ vặn hỏi: "Chung 1 cục CPU, 1 thanh RAM thì phân tán chỗ nào?". Đây là câu trả lời để bạn bảo vệ đồ án:

## 1. Phân tán về Xử lý (Distributed Processing)
*   **Khái niệm**: Thay vì 1 "bộ não" (Process) xử lý 1000 việc, ta chia cho 3 "bộ não" xử lý mỗi người 333 việc.
*   **Chứng minh trong dự án**:
    *   Chúng ta chia hệ thống thành **3 Tiến trình Server (Server Processes)** riêng biệt (Node 1, Node 2, Node 3).
    *   Trong Hệ điều hành (Windows), mỗi tiến trình này được cấp một **PID (Process ID)** khác nhau.
    *   Việc điều phối CPU cho PID nào chạy là việc của Hệ điều hành. Nếu máy bạn có 4 nhân CPU, OS sẽ tự động chia: Process 1 chạy nhân A, Process 2 chạy nhân B... -> **Đó là phân tán tài nguyên tính toán.**

## 2. Phân tán về RAM (Memory Isolation) - *Cực kỳ quan trọng*
*   **Câu hỏi**: "RAM chung mà?"
*   **Trả lời**: "RAM vật lý là chung, nhưng **Không gian địa chỉ bộ nhớ (Memory Address Space)** là riêng biệt và phân tán."
*   **Tại sao quan trọng?**:
    *   Nếu Server 1 bị lỗi lập trình (ví dụ: vòng lặp vô tận, rò rỉ bộ nhớ) -> Nó chỉ ăn hết phần RAM của nó và bị OS giết (Crash).
    *   Server 2 và Server 3 **không hề bị ảnh hưởng**. RAM của chúng vẫn an toàn.
    *   -> Đây là tính chất **Chịu lỗi (Fault Tolerance)** của hệ phân tán. Nếu là hệ tập trung (1 server), server chết là TOÀN BỘ hệ thống dừng hoạt động.

## 3. Tính "Trong suốt" (Transparency)
*   Đây là lập luận mạnh nhất: "Hệ thống của em được thiết kế để **không phụ thuộc vị trí vật lý**."
*   Minh chứng: 
    *   Hiện tại 3 server chạy 3 port trên `localhost`.
    *   Nhưng nếu em có 3 máy tính, em chỉ cần đổi IP config, copy code sang. Code **không cần sửa một dấu chấm phẩy nào** mà vẫn chạy được.
    *   -> Điều đó chứng minh kiến trúc phần mềm đã đạt chuẩn phân tán, việc chạy trên 1 máy chỉ là do hạn chế thiết bị demo.

## Kết luận
Phân tán không nhất thiết phải là "đặt máy ở Hà Nội và Sài Gòn". Phân tán bắt đầu từ việc **tách rời các thành phần xử lý (Decoupling)** để chúng không chết chùm, và có thể gánh tải cho nhau.
