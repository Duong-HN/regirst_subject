import socket
from request_handler import ClientThread

# --- CONFIGURATION ---
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8888

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5)
    print(f"[*] Server listening on {SERVER_HOST}:{SERVER_PORT}")
    print("[*] Waiting for clients...")

    while True:
        try:
            # Main Server Loop: Just accept and dispatch
            client_sock, client_addr = server.accept()
            
            # Delegate to Handler
            thread = ClientThread(client_sock, client_addr)
            thread.start()
            
        except KeyboardInterrupt:
            print("\nShutting down server...")
            break
        except Exception as e:
            print(f"Server Error: {e}")

    server.close()

if __name__ == "__main__":
    main()
