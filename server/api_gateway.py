import socket
import threading
import os

# Cấu hình Gateway
GATEWAY_HOST = '0.0.0.0'
GATEWAY_PORT = 8888

# Địa chỉ các Microservices
AUTH_SERVICE = (os.getenv('AUTH_HOST', 'localhost'), 9001)
COURSE_SERVICE = (os.getenv('COURSE_HOST', 'localhost'), 9002)
TRANSACTION_SERVICE = (os.getenv('TRANSACTION_HOST', 'localhost'), 9003)

class ClientSession(threading.Thread):
    """Xử lý session của một client"""
    def __init__(self, client_sock, client_addr):
        super().__init__()
        self.client_sock = client_sock
        self.client_addr = client_addr
        self.current_user = None  # Lưu trạng thái đăng nhập
        
    def forward_to_service(self, service_addr, request):
        """Chuyển tiếp request đến service và nhận response"""
        try:
            # Tạo kết nối đến service
            service_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            service_sock.connect(service_addr)
            
            # Gửi request
            service_sock.sendall(request.encode('utf-8'))
            
            # Nhận response
            response = service_sock.recv(4096).decode('utf-8')
            
            service_sock.close()
            
            # Nếu response rỗng (service đóng kết nối), trả về lỗi
            if not response:
                return "ERR|Service Closed Connection"
                
            return response
        except Exception as e:
            print(f"[GATEWAY ERROR] Failed to connect to {service_addr}: {e}")
            return f"ERR|Service Unavailable"
    
    def route_request(self, request):
        """Định tuyến request đến service phù hợp"""
        parts = request.strip().split('|')
        if not parts:
            return "ERR|Invalid Request"
        
        command = parts[0]
        
        # ROUTING LOGIC
        if command == 'LOGIN':
            # Gửi đến Auth Service
            response = self.forward_to_service(AUTH_SERVICE, request)
            # Nếu login thành công, lưu username
            if response.startswith("OK") and len(parts) >= 2:
                self.current_user = parts[1]
            return response
            
        elif command == 'LOGOUT':
            self.current_user = None
            return "OK|Logged out"
            
        elif not self.current_user:
            # Chưa đăng nhập
            return "ERR|Authentication Required"
            
        elif command in ['LIST', 'MY_COURSES', 'GET_DETAILS']:
            # Gửi đến Course Service
            # Thêm username vào request nếu cần
            if command == 'MY_COURSES':
                request = f"{command}|{self.current_user}"
            return self.forward_to_service(COURSE_SERVICE, request)
            
        elif command == 'REGISTER':
            # Gửi đến Transaction Service
            # Thêm username vào request
            if len(parts) >= 2:
                section_id = parts[1]
                request = f"REGISTER|{self.current_user}|{section_id}"
            return self.forward_to_service(TRANSACTION_SERVICE, request)
            
        else:
            return "ERR|Unknown Command"
    
    def run(self):
        """Vòng lặp xử lý request từ client"""
        print(f"[GATEWAY] New client connected: {self.client_addr}")
        
        try:
            while True:
                # Nhận request từ client
                data = self.client_sock.recv(1024).decode('utf-8')
                if not data:
                    break
                
                print(f"[GATEWAY] Request from {self.client_addr}: {data.strip()}")
                
                # Định tuyến và xử lý
                response = self.route_request(data)
                
                print(f"[GATEWAY] Response to {self.client_addr}: {response.strip()}")
                
                # Gửi response về client
                self.client_sock.sendall(response.encode('utf-8'))
                
        except Exception as e:
            print(f"[GATEWAY ERROR] {self.client_addr}: {e}")
        finally:
            print(f"[GATEWAY] Client disconnected: {self.client_addr}")
            self.client_sock.close()

def main():
    """Khởi động API Gateway"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((GATEWAY_HOST, GATEWAY_PORT))
    except OSError as e:
        print(f"[ERROR] Cannot bind to port {GATEWAY_PORT}: {e}")
        print("Make sure no other service is using this port.")
        return
    
    server.listen(10)
    
    print("=" * 60)
    print(f"[*] API GATEWAY running on {GATEWAY_HOST}:{GATEWAY_PORT}")
    print("=" * 60)
    print("[*] Routing Configuration:")
    print(f"    LOGIN           -> Auth Service      {AUTH_SERVICE}")
    print(f"    LIST/MY_COURSES -> Course Service    {COURSE_SERVICE}")
    print(f"    REGISTER        -> Transaction Service {TRANSACTION_SERVICE}")
    print("=" * 60)
    print("[*] Waiting for clients...")
    print()
    
    while True:
        try:
            client_sock, client_addr = server.accept()
            
            # Tạo session mới cho client
            session = ClientSession(client_sock, client_addr)
            session.start()
            
        except KeyboardInterrupt:
            print("\n[GATEWAY] Shutting down...")
            break
        except Exception as e:
            print(f"[GATEWAY ERROR] {e}")
    
    server.close()

if __name__ == "__main__":
    main()
