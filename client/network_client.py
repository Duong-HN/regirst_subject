import socket
import sys

# --- CẤU HÌNH ---
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8888

class NetworkClient:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Thiết lập kết nối đến server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            return True
        except ConnectionRefusedError:
            print(f"Error: Could not connect to server at {self.host}:{self.port}")
            return False
        except Exception as e:
            print(f"Connection Error: {e}")
            return False

    def send_request(self, request):
        """Gửi yêu cầu dạng chuỗi và chờ phản hồi dạng chuỗi"""
        if not self.sock:
            return "ERR|Not Connected"
        
        try:
            self.sock.sendall(request.encode('utf-8'))
            response = self.sock.recv(4096).decode('utf-8')
            return response
        except Exception as e:
            print(f"Transmission Error: {e}")
            self.close()
            sys.exit(1)

    def close(self):
        if self.sock:
            self.sock.close()
