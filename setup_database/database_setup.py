import mysql.connector
from mysql.connector import errorcode

# --- CONFIGURATION ---
DB_CONFIG = {
    'user': 'root',
    'password': '',  # Default XAMPP password is empty
    'host': 'localhost',
    'raise_on_warnings': True
}
DB_NAME = 'course_registration'

TABLES = {}

# 1. USERS
TABLES['users'] = (
    "CREATE TABLE `users` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `username` varchar(50) NOT NULL UNIQUE,"
    "  `password` varchar(50) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

# 2. SUBJECTS
TABLES['subjects'] = (
    "CREATE TABLE `subjects` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `code` varchar(20) NOT NULL UNIQUE,"
    "  `name` varchar(100) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

# 3. TEACHERS
TABLES['teachers'] = (
    "CREATE TABLE `teachers` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `name` varchar(100) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

# 4. TIME SLOTS (Fully normalized)
TABLES['time_slots'] = (
    "CREATE TABLE `time_slots` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `name` varchar(100) NOT NULL UNIQUE,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

# 5. SECTIONS
TABLES['sections'] = (
    "CREATE TABLE `sections` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `subject_id` int(11) NOT NULL,"
    "  `teacher_id` int(11) NOT NULL,"
    "  `time_slot_id` int(11) NOT NULL,"
    "  `max_slots` int(11) NOT NULL,"
    "  `current_enrolled` int(11) DEFAULT 0,"
    "  PRIMARY KEY (`id`),"
    "  CONSTRAINT `fk_subject` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`),"
    "  CONSTRAINT `fk_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),"
    "  CONSTRAINT `fk_time_slot` FOREIGN KEY (`time_slot_id`) REFERENCES `time_slots` (`id`)"
    ") ENGINE=InnoDB")

# 6. ENROLLMENTS
TABLES['enrollments'] = (
    "CREATE TABLE `enrollments` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `student_username` varchar(50) NOT NULL,"
    "  `section_id` int(11) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  UNIQUE KEY `unique_enrollment` (`student_username`, `section_id`),"
    "  CONSTRAINT `fk_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

def create_database(cursor):
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"OK: Database '{DB_NAME}' created successfully.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def main():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()

        create_database(cursor)
        cursor.execute(f"USE {DB_NAME}")

        for table_name in TABLES:
            print(f"Creating table '{table_name}'...")
            cursor.execute(TABLES[table_name])

        # --- INSERT DUMMY DATA ---
        
        # 1. Users
        users = [('sv01', '123'), ('sv02', '123'), ('sv03', '123')]
        cursor.executemany("INSERT INTO users (username, password) VALUES (%s, %s)", users)

        # 2. Subjects
        subjects = [
            ('IT3080', 'Do An Co So'),
            ('IT4060', 'Ung Dung Phan Tan'),
            ('IT4490', 'Chuong Trinh Dich')
        ]
        cursor.executemany("INSERT INTO subjects (code, name) VALUES (%s, %s)", subjects)
        
        # 3. Teachers
        teachers = [('Thay Hung',), ('Co Lan',), ('Thay Bao',), ('Thay Tuan',), ('Co Mai',)]
        cursor.executemany("INSERT INTO teachers (name) VALUES (%s)", teachers)

        # 4. Time Slots (Mon to Sat, Sang/Chieu)
        time_slots = []
        days = ['Thu 2', 'Thu 3', 'Thu 4', 'Thu 5', 'Thu 6', 'Thu 7']
        for day in days:
            time_slots.append((f"Sang {day} (7h-11h)",))
            time_slots.append((f"Chieu {day} (13h-17h)",))
        cursor.executemany("INSERT INTO time_slots (name) VALUES (%s)", time_slots)

        # 5. Sections (4 sections per subject)
        # Assuming IDs: 
        # Subjects: 1: IT3080, 2: IT4060, 3: IT4490
        # Teachers: 1: Hung, 2: Lan, 3: Bao, 4: Tuan, 5: Mai
        # TimeSlots: 
        # Sang T2: 1, Chieu T2: 2
        # Sang T3: 3, Chieu T3: 4
        # Sang T4: 5, Chieu T4: 6
        # Sang T5: 7, Chieu T5: 8
        # Sang T6: 9, Chieu T6: 10
        # Sang T7: 11, Chieu T7: 12

        sections = [
            # DACS: Hung (1), Lan (2). Slots: 1, 4, 5, 8
            (1, 1, 1, 15), (1, 2, 4, 15), (1, 1, 5, 15), (1, 2, 8, 15),
            # UDPT: Bao (3), Tuan (4). Slots: 9, 12, 3, 2
            (2, 3, 9, 3), (2, 4, 12, 3), (2, 3, 3, 40), (2, 4, 2, 40),
            # CTD: Mai (5), Hung (1). Slots: 7, 6, 11, 10
            (3, 5, 7, 30), (3, 1, 6, 30), (3, 5, 11, 30), (3, 1, 10, 30),
        ]
        cursor.executemany("INSERT INTO sections (subject_id, teacher_id, time_slot_id, max_slots) VALUES (%s, %s, %s, %s)", sections)

        cnx.commit()
        print("Fully Normalized Setup completed successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals(): cnx.close()

if __name__ == "__main__":
    main()
