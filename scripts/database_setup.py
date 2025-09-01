#!/usr/bin/env python3
"""
database setup for attendance system
creates tables and adds sample data
"""

import sys
from pathlib import Path
import sqlite3
from datetime import datetime, date

#add parent directory to path so we can import config
sys.path.append(str(Path(__file__).parent.parent))
from config import STUDENTS_DB, ATTENDANCE_DB

def create_students_table():
    """create the students table"""
    print("creating students table...")
    
    conn = sqlite3.connect(STUDENTS_DB)
    cursor = conn.cursor()
    
    #create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("students table created")

def create_attendance_table():
    """create the attendance table in the same database"""
    print("creating attendance table...")
    
    conn = sqlite3.connect(STUDENTS_DB)  #use same database
    cursor = conn.cursor()
    
    #create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_date DATE NOT NULL,
            check_in_time TIMESTAMP,
            status TEXT DEFAULT 'present',
            confidence REAL,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    #create classes table for future use
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            class_time TIME,
            class_days TEXT,
            teacher_name TEXT,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("attendance table created")

def add_student(student_id, first_name, last_name, email=None, photo_path=None):
    """add a new student"""
    conn = sqlite3.connect(STUDENTS_DB)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO students (student_id, first_name, last_name, email, photo_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, first_name, last_name, email, photo_path))
        
        conn.commit()
        print(f"added student: {first_name} {last_name} ({student_id})")
        return True
        
    except sqlite3.IntegrityError:
        print(f"student {student_id} already exists")
        return False
    except Exception as e:
        print(f"error adding student: {e}")
        return False
    finally:
        conn.close()

def list_students():
    """show all students"""
    conn = sqlite3.connect(STUDENTS_DB)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM students WHERE active = TRUE')
    students = cursor.fetchall()
    
    if not students:
        print("no students found")
    else:
        print("\ncurrent students:")
        print("-" * 60)
        for student in students:
            print(f"id: {student[1]} | {student[2]} {student[3]} | email: {student[4]}")
    
    conn.close()
    return students

def record_attendance(student_id, status='present', confidence=None):
    """record attendance for a student"""
    conn = sqlite3.connect(STUDENTS_DB)  #use same database
    cursor = conn.cursor()
    
    today = date.today()
    now = datetime.now()
    
    try:
        cursor.execute('''
            INSERT INTO attendance (student_id, class_date, check_in_time, status, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, today, now, status, confidence))
        
        conn.commit()
        print(f"recorded attendance for {student_id}: {status}")
        return True
        
    except Exception as e:
        print(f"error recording attendance: {e}")
        return False
    finally:
        conn.close()

def get_todays_attendance():
    """show today's attendance"""
    conn = sqlite3.connect(STUDENTS_DB)  #use same database
    cursor = conn.cursor()
    
    today = date.today()
    
    cursor.execute('''
        SELECT a.student_id, a.check_in_time, a.status, a.confidence,
               s.first_name, s.last_name
        FROM attendance a
        LEFT JOIN students s ON a.student_id = s.student_id
        WHERE a.class_date = ?
        ORDER BY a.check_in_time
    ''', (today,))
    
    attendance = cursor.fetchall()
    
    if not attendance:
        print(f"no attendance records for {today}")
    else:
        print(f"\nattendance for {today}:")
        print("-" * 70)
        for record in attendance:
            name = f"{record[4]} {record[5]}" if record[4] else "unknown"
            time_str = record[1][:19] if record[1] else "no time"
            print(f"{record[0]} | {name} | {time_str} | {record[2]}")
    
    conn.close()
    return attendance

def setup_sample_data():
    """add some sample students for testing"""
    print("\nadding sample students...")
    
    #add yourself as the first student
    your_id = input("enter your student id (or just press enter for 'student_001'): ").strip()
    if not your_id:
        your_id = "student_001"
    
    your_first = input("enter your first name: ").strip()
    your_last = input("enter your last name: ").strip()
    your_email = input("enter your email (optional): ").strip() or None
    
    add_student(your_id, your_first, your_last, your_email)
    
    #ask if they want more sample students
    add_more = input("\nadd more sample students? (y/n): ").lower().strip()
    if add_more == 'y':
        add_student("student_002", "john", "doe", "john.doe@example.com")
        add_student("student_003", "jane", "smith", "jane.smith@example.com")
        add_student("student_004", "mike", "johnson", "mike.johnson@example.com")
        print("added sample students")

def main():
    """setup database"""
    print("=== database setup ===")
    
    #create directories if needed
    STUDENTS_DB.parent.mkdir(parents=True, exist_ok=True)
    
    #create tables (both in same database now)
    create_students_table()
    create_attendance_table()
    
    #check if we have students
    existing_students = list_students()
    
    if not existing_students:
        setup_sample_data()
    else:
        add_new = input("\nadd new student? (y/n): ").lower().strip()
        if add_new == 'y':
            setup_sample_data()
    
    #show final student list
    list_students()
    
    #show today's attendance
    get_todays_attendance()
    
    print("\ndatabase setup complete!")
    print(f"main database: {STUDENTS_DB}")
    print("(all tables are in one database now)")

if __name__ == "__main__":
    main()