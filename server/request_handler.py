import threading
import json
from database_manager import DatabaseManager

# --- CONFIGURATION ---
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'course_registration',
    'raise_on_warnings': True
}

class ClientThread(threading.Thread):
    def __init__(self, client_sock, client_addr):
        super().__init__()
        self.client_sock = client_sock
        self.client_addr = client_addr
        self.db = DatabaseManager(DB_CONFIG) # Each thread gets its own DB connection
        self.current_user = None 

    def run(self):
        print(f"[NEW CONNECTION] {self.client_addr} connected.")
        if not self.db.connect():
            print(f"[ERROR] Could not connect to DB for {self.client_addr}")
            self.client_sock.close()
            return

        try:
            while True:
                data = self.client_sock.recv(1024).decode('utf-8')
                if not data:
                    break
                
                parts = data.strip().split('|')
                command = parts[0]
                args = parts[1:]

                response = "ERR|Unknown Command"

                if command == 'LOGIN':
                    response = self.handle_login(args)
                elif command == 'LOGOUT':
                    self.current_user = None
                    response = "OK|Logged out"
                elif not self.current_user:
                    response = "ERR|Authentication Required"
                elif command == 'LIST':
                    response = self.handle_list()
                elif command == 'REGISTER':
                    response = self.handle_register(args)
                elif command == 'MY_COURSES':
                    response = self.handle_my_courses()
                elif command == 'GET_DETAILS':
                    response = self.handle_get_details(args)
                
                self.client_sock.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"[ERROR] {self.client_addr}: {e}")
        finally:
            print(f"[DISCONNECTED] {self.client_addr}")
            self.db.close() # Close DB connection properly
            self.client_sock.close()

    def handle_login(self, args):
        if len(args) != 2: return "ERR|Invalid arguments"
        user = self.db.login_user(args[0], args[1])
        if user:
            self.current_user = args[0]
            return "OK|Success"
        return "ERR|Invalid Username or Password"

    def handle_list(self):
        courses = self.db.get_all_courses()
        return "OK|" + json.dumps(courses)

    def handle_register(self, args):
        if len(args) != 1: return "ERR|Invalid arguments"
        try:
            sec_id = int(args[0])
            success, msg = self.db.register_student(self.current_user, sec_id)
            status = "OK" if success else "ERR"
            return f"{status}|{msg}"
        except ValueError:
            return "ERR|Invalid Section ID"

    def handle_my_courses(self):
        courses = self.db.get_student_courses(self.current_user)
        return "OK|" + json.dumps(courses)

    def handle_get_details(self, args):
        if len(args) != 1: return "ERR|Invalid arguments"
        try:
            sec_id = int(args[0])
            details = self.db.get_section_details(sec_id)
            if details:
                return "OK|" + json.dumps(details)
            return "ERR|Section not found"
        except ValueError:
            return "ERR|Invalid Section ID"
