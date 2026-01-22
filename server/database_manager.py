import mysql.connector
import json

class DatabaseManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.cnx = None
        self.cursor = None

    def connect(self):
        """Establish connection to the database"""
        try:
            self.cnx = mysql.connector.connect(**self.db_config)
            self.cnx.autocommit = False # Handle transactions manually
            self.cursor = self.cnx.cursor(dictionary=True)
            return True
        except mysql.connector.Error as err:
            print(f"DB Connection Error: {err}")
            return False

    def close(self):
        """Close connection"""
        if self.cursor: self.cursor.close()
        if self.cnx: self.cnx.close()

    def login_user(self, username, password):
        """Check credentials"""
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        return self.cursor.fetchone()

    def get_all_courses(self):
        """Fetch full course list with joins"""
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
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_student_courses(self, username):
        """Get courses registered by a specific student"""
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
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()

    def get_section_details(self, section_id):
        """Get info and classmates for a section"""
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
        self.cursor.execute(query_info, (section_id,))
        info = self.cursor.fetchone()
        
        if not info: return None

        # Students
        query_students = "SELECT student_username FROM enrollments WHERE section_id = %s"
        self.cursor.execute(query_students, (section_id,))
        students = [row['student_username'] for row in self.cursor.fetchall()]

        return {"info": info, "students": students}

    def register_student(self, username, section_id):
        """
        Transactional registration logic with Locking
        Returns: (Success: bool, Message: str)
        """
        try:
            # Clean state
            self.cnx.rollback()
            self.cnx.start_transaction()

            # 1. Check existing enrollment
            check_enroll = "SELECT id FROM enrollments WHERE student_username = %s AND section_id = %s"
            self.cursor.execute(check_enroll, (username, section_id))
            if self.cursor.fetchone():
                self.cnx.rollback()
                return False, "Already Registered for this class"

            # 2. Lock and Check Slots
            verify_query = "SELECT current_enrolled, max_slots FROM sections WHERE id = %s FOR UPDATE"
            self.cursor.execute(verify_query, (section_id,))
            section = self.cursor.fetchone()

            if not section:
                self.cnx.rollback()
                return False, "Class not found"

            if section['current_enrolled'] >= section['max_slots']:
                self.cnx.rollback()
                return False, "Class is FULL"

            # 3. Update and Insert
            update_sec = "UPDATE sections SET current_enrolled = current_enrolled + 1 WHERE id = %s"
            self.cursor.execute(update_sec, (section_id,))

            insert_enroll = "INSERT INTO enrollments (student_username, section_id) VALUES (%s, %s)"
            self.cursor.execute(insert_enroll, (username, section_id))

            self.cnx.commit()
            return True, "Registration Successful"

        except mysql.connector.Error as err:
            self.cnx.rollback()
            return False, f"Database Error: {err}"
