import mysql.connector
from mysql.connector import pooling

class DatabaseManager:
    _pool = None # Singleton Pool

    def __init__(self, db_config):
        self.db_config = db_config
        self.cnx = None
        self.cursor = None
        
        # Khởi tạo Pool nếu chưa có (Chỉ 1 lần duy nhất cho toàn bộ Server)
        if not DatabaseManager._pool:
            try:
                DatabaseManager._pool = pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=10,  # "THẰNG NGĂN CHẶN": Chỉ cho phép tối đa 10 kết nối cùng lúc
                    pool_reset_session=True,
                    **db_config
                )
                print("[DATABASE] Connection Pool created with size 10")
            except Exception as err:
                print(f"[DATABASE] Pool Error: {err}")

    def _get_conn(self):
        """Helper để lấy kết nối từ pool"""
        return DatabaseManager._pool.get_connection()

    def login_user(self, username, password):
        """Kiểm tra thông tin đăng nhập"""
        cnx = self._get_conn()
        cursor = cnx.cursor(dictionary=True)
        try:
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            return cursor.fetchone()
        finally:
            cursor.close()
            cnx.close() # Trả về pool

    def get_all_courses(self):
        """Lấy danh sách đầy đủ các môn học"""
        cnx = self._get_conn()
        cursor = cnx.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    sec.id as section_id,
                    sub.code,
                    sub.name as subject_name,
                    t.name as teacher_name,
                    ts.name as time_slot,
                    sec.current_enrolled,
                    sec.max_slots
                FROM sections sec
                JOIN subjects sub ON sec.subject_id = sub.id
                JOIN teachers t ON sec.teacher_id = t.id
                JOIN time_slots ts ON sec.time_slot_id = ts.id
                ORDER BY sub.code
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            cnx.close()

    def get_student_courses(self, username):
        """Lấy các môn đã đăng ký bởi một sinh viên cụ thể"""
        cnx = self._get_conn()
        cursor = cnx.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    sec.id as section_id,
                    sub.code,
                    sub.name as subject_name,
                    t.name as teacher_name,
                    ts.name as time_slot
                FROM enrollments e
                JOIN sections sec ON e.section_id = sec.id
                JOIN subjects sub ON sec.subject_id = sub.id
                JOIN teachers t ON sec.teacher_id = t.id
                JOIN time_slots ts ON sec.time_slot_id = ts.id
                WHERE e.student_username = %s
            """
            cursor.execute(query, (username,))
            return cursor.fetchall()
        finally:
            cursor.close()
            cnx.close()

    def get_section_details(self, section_id):
        """Lấy thông tin và danh sách bạn học cho một lớp học phần"""
        cnx = self._get_conn()
        cursor = cnx.cursor(dictionary=True)
        try:
            # Info
            query_info = """
                SELECT 
                    sub.name as subject_name,
                    t.name as teacher_name,
                    ts.name as time_slot
                FROM sections sec
                JOIN subjects sub ON sec.subject_id = sub.id
                JOIN teachers t ON sec.teacher_id = t.id
                JOIN time_slots ts ON sec.time_slot_id = ts.id
                WHERE sec.id = %s
            """
            cursor.execute(query_info, (section_id,))
            info = cursor.fetchone()
            
            if not info: return None

            # Students
            query_students = "SELECT student_username FROM enrollments WHERE section_id = %s"
            cursor.execute(query_students, (section_id,))
            students = [row['student_username'] for row in cursor.fetchall()]

            return {"info": info, "students": students}
        finally:
            cursor.close()
            cnx.close()

    def register_student(self, username, section_id):
        """
        Logic đăng ký có giao dịch (Transactional) với Khóa (Locking)
        """
        cnx = self._get_conn()
        
        # QUAN TRỌNG: Tắt autocommit để quản lý transaction thủ công
        cnx.autocommit = False 
        cursor = cnx.cursor(dictionary=True)
        
        try:
            # Clean state
            # cnx.rollback() # Không cần rollback đầu tiên vì lấy conn mới

            cnx.start_transaction()

            # 1. Kiểm tra đã đăng ký chưa
            check_enroll = "SELECT id FROM enrollments WHERE student_username = %s AND section_id = %s"
            cursor.execute(check_enroll, (username, section_id))
            if cursor.fetchone():
                cnx.rollback()
                return False, "Already Registered for this class"

            # 2. Khóa và kiểm tra chỗ trống (SELECT ... FOR UPDATE)
            # Dòng này sẽ CHẶN nếu tiến trình khác đang giữ khóa (Queuing tại DB layer)
            verify_query = "SELECT current_enrolled, max_slots FROM sections WHERE id = %s FOR UPDATE"
            cursor.execute(verify_query, (section_id,))
            section = cursor.fetchone()

            if not section:
                cnx.rollback()
                return False, "Class not found"

            if section['current_enrolled'] >= section['max_slots']:
                cnx.rollback()
                return False, "Class is FULL"

            # 3. Cập nhật và Chèn dữ liệu
            update_sec = "UPDATE sections SET current_enrolled = current_enrolled + 1 WHERE id = %s"
            cursor.execute(update_sec, (section_id,))

            insert_enroll = "INSERT INTO enrollments (student_username, section_id) VALUES (%s, %s)"
            cursor.execute(insert_enroll, (username, section_id))

            cnx.commit()
            return True, "Registration Successful"

        except mysql.connector.Error as err:
            cnx.rollback()
            return False, f"Database Error: {err}"
        finally:
            cursor.close()
            cnx.close()
