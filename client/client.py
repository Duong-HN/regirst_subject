import json
import sys
from network_client import NetworkClient

# --- CONFIGURATION ---
# To connect to a remote server, change this IP
SERVER_IP = 'localhost' 

def print_table(headers, data, col_widths):
    # Print Header
    header_row = "".join([h.ljust(w) for h, w in zip(headers, col_widths)])
    print("-" * len(header_row))
    print(header_row)
    print("-" * len(header_row))
    
    # Print Rows
    for row in data:
        print("".join([str(val).ljust(w) for val, w in zip(row, col_widths)]))
    print("-" * len(header_row))

def login_menu(net_client):
    while True:
        print("\n--- COURSE REGISTRATION SYSTEM ---")
        print("1. Login")
        print("2. Exit")
        choice = input("Select: ").strip()

        if choice == '1':
            user = input("Username: ").strip()
            pwd = input("Password: ").strip()
            # Use NetworkClient to send
            resp = net_client.send_request(f"LOGIN|{user}|{pwd}")
            if resp.startswith("OK"):
                print(f"Login Successful! Welcome {user}.")
                return True
            else:
                parts = resp.split('|')
                msg = parts[1] if len(parts) > 1 else "Unknown Error"
                print(f"Login Failed: {msg}")
        elif choice == '2':
            return False
        else:
            print("Invalid choice.")

def main_menu(net_client):
    while True:
        print("\n--- STUDENT MENU ---")
        print("1. List All Courses (Dang Ky Mon)")
        print("2. My Registered Courses (TKB ca nhan)")
        print("3. View Course Details & Classmates (Xem lop)")
        print("4. Logout")
        choice = input("Select: ").strip()

        if choice == '1':
            resp = net_client.send_request("LIST")
            if resp.startswith("OK"):
                courses = json.loads(resp.split('|')[1])
                print("\n[ AVAILABLE COURSES ]")
                # Table: ID | Code | Subject | Section | Teacher | Slots
                headers = ["ID", "Code", "Subject", "Time Slot", "Teacher", "Slots"]
                widths = [5, 10, 25, 25, 20, 10]
                
                table_data = []
                for c in courses:
                    slots = f"{c['current_enrolled']}/{c['max_slots']}"
                    table_data.append([c['section_id'], c['code'], c['subject_name'], c['time_slot'], c['teacher_name'], slots])
                
                print_table(headers, table_data, widths)
                
                reg_choice = input("\nEnter ID to Register (or Enter to skip): ").strip()
                if reg_choice:
                    reg_resp = net_client.send_request(f"REGISTER|{reg_choice}")
                    print(f"Server Response: {reg_resp.split('|')[1]}")

        elif choice == '2':
            resp = net_client.send_request("MY_COURSES")
            if resp.startswith("OK"):
                courses = json.loads(resp.split('|')[1])
                print("\n[ MY COURSES ]")
                headers = ["ID", "Code", "Subject", "Time Slot", "Teacher"]
                widths = [5, 10, 25, 25, 20]
                table_data = [[c['section_id'], c['code'], c['subject_name'], c['time_slot'], c['teacher_name']] for c in courses]
                print_table(headers, table_data, widths)
            else:
                print(f"Error: {resp}")

        elif choice == '3':
            c_id = input("Enter Course Section ID to view details: ").strip()
            if c_id:
                resp = net_client.send_request(f"GET_DETAILS|{c_id}")
                if resp.startswith("OK"):
                    data = json.loads(resp.split('|')[1])
                    info = data['info']
                    print(f"\n--- CLASS DETAILS: {info['subject_name']} ---")
                    print(f"Teacher: {info['teacher_name']}")
                    print(f"Time:    {info['time_slot']}")
                    print("\n[ CLASSMATES ]")
                    students = data['students']
                    if students:
                        print(", ".join(students))
                    else:
                        print("(No students enrolled yet)")
                    print("-----------------------------")
                else:
                    parts = resp.split('|')
                    msg = parts[1] if len(parts) > 1 else "Unknown Error"
                    print(f"Error: {msg}")

        elif choice == '4':
            net_client.send_request("LOGOUT")
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

def main():
    # Initialize Network Client
    client = NetworkClient(host=SERVER_IP)
    
    if client.connect():
        try:
            while True:
                if login_menu(client):
                    main_menu(client)
                else:
                    break
        finally:
            client.close()
            print("Disconnected.")

if __name__ == "__main__":
    main()
