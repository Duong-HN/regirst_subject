import socket
import threading
import os
from database_manager import DatabaseManager

HOST = '0.0.0.0'
PORT = 9001  # Auth Service Port

DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': os.getenv('DB_HOST', 'localhost'),  # Docker: mysql, Local: localhost
    'database': 'course_registration',
    'raise_on_warnings': True
}

def handle_client(client_sock, client_addr):
    """Xử lý yêu cầu đăng nhập"""
    db = DatabaseManager(DB_CONFIG)
    try:
        data = client_sock.recv(1024).decode('utf-8')
        if not data: 
            return
        
        parts = data.strip().split('|')
        command = parts[0]
        
        response = "ERR|Unknown Request"

        if command == 'LOGIN' and len(parts) == 3:
            username = parts[1]
            password = parts[2]
            user = db.login_user(username, password)
            if user:
                response = "OK|Success"
            else:
                response = "ERR|Invalid Credentials"
        
        client_sock.sendall(response.encode('utf-8'))
        
    except Exception as e:
        print(f"[AUTH ERROR] {client_addr}: {e}")
    finally:
        client_sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] AUTH SERVICE running on {HOST}:{PORT}")

    while True:
        try:
            client, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client, addr))
            t.start()
        except KeyboardInterrupt:
            print("\n[AUTH] Shutting down...")
            break

    server.close()

if __name__ == "__main__":
    main()
