import socket
import threading
import json
import os
from database_manager import DatabaseManager

HOST = '0.0.0.0'
PORT = 9002  # Course Info Service Port

DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': 'course_registration',
    'raise_on_warnings': True
}

def handle_client(client_sock, client_addr):
    """Xử lý yêu cầu xem thông tin khóa học"""
    db = DatabaseManager(DB_CONFIG)
    try:
        data = client_sock.recv(1024).decode('utf-8')
        if not data:
            return
        
        parts = data.strip().split('|')
        command = parts[0]
        args = parts[1:]
        
        response = "ERR|Unknown Request"

        if command == 'LIST':
            courses = db.get_all_courses()
            response = "OK|" + json.dumps(courses)
            
        elif command == 'MY_COURSES' and len(args) == 1:
            username = args[0]
            courses = db.get_student_courses(username)
            response = "OK|" + json.dumps(courses)
            
        elif command == 'GET_DETAILS' and len(args) == 1:
            try:
                section_id = int(args[0])
                details = db.get_section_details(section_id)
                if details:
                    response = "OK|" + json.dumps(details)
                else:
                    response = "ERR|Section not found"
            except ValueError:
                response = "ERR|Invalid Section ID"
        
        client_sock.sendall(response.encode('utf-8'))
        
    except Exception as e:
        print(f"[COURSE ERROR] {client_addr}: {e}")
    finally:
        client_sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] COURSE SERVICE running on {HOST}:{PORT}")

    while True:
        try:
            client, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client, addr))
            t.start()
        except KeyboardInterrupt:
            print("\n[COURSE] Shutting down...")
            break

    server.close()

if __name__ == "__main__":
    main()
