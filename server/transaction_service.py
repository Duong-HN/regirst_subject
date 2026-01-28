import socket
import threading
import time
import os
from database_manager import DatabaseManager

HOST = '0.0.0.0'
PORT = 9003  # Transaction Service Port

DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': 'course_registration',
    'raise_on_warnings': True
}

# HÀNG CHỜ ĐĂNG KÝ - Chỉ cho phép 5 người cùng lúc
REGISTRATION_SEMAPHORE = threading.Semaphore(5)

def handle_client(client_sock, client_addr):
    """Xử lý yêu cầu đăng ký môn học"""
    db = DatabaseManager(DB_CONFIG)
    try:
        data = client_sock.recv(1024).decode('utf-8')
        if not data:
            return
        
        parts = data.strip().split('|')
        command = parts[0]
        args = parts[1:]
        
        response = "ERR|Unknown Request"

        if command == 'REGISTER' and len(args) == 2:
            username = args[0]
            try:
                section_id = int(args[1])
                
                # HÀNG CHỜ - Người thứ 6 sẽ chờ ở đây
                with REGISTRATION_SEMAPHORE:
                    print(f"[TRANSACTION] Processing registration for {username} -> Section {section_id}")
                    time.sleep(0.5)  # Simulate processing time
                    
                    success, msg = db.register_student(username, section_id)
                    status = "OK" if success else "ERR"
                    response = f"{status}|{msg}"
            except ValueError:
                response = "ERR|Invalid Section ID"
        
        client_sock.sendall(response.encode('utf-8'))
        
    except Exception as e:
        print(f"[TRANSACTION ERROR] {client_addr}: {e}")
    finally:
        client_sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"[*] TRANSACTION SERVICE running on {HOST}:{PORT}")
    print(f"[*] Registration Queue: Max 5 concurrent requests")

    while True:
        try:
            client, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client, addr))
            t.start()
        except KeyboardInterrupt:
            print("\n[TRANSACTION] Shutting down...")
            break

    server.close()

if __name__ == "__main__":
    main()
