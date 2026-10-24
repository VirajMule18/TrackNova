import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "tracknova.db")


def get_connection():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def setup_database():

    with get_connection() as db:

        # USERS
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        # STUDENTS
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL
            )
        """)

        # LECTURES
        db.execute("""
            CREATE TABLE IF NOT EXISTS lectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lecture_date TEXT NOT NULL,
                lecture_number INTEGER NOT NULL,
                subject TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            )
        """)

        # ATTENDANCE
        db.execute("""
            CREATE TABLE IF NOT EXISTS lecture_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                student_id INTEGER NOT NULL,
                lecture_id INTEGER NOT NULL,

                status TEXT NOT NULL
                CHECK(status IN ('Present', 'Absent')),

                UNIQUE(student_id, lecture_id),

                FOREIGN KEY(student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,

                FOREIGN KEY(lecture_id)
                REFERENCES lectures(id)
                ON DELETE CASCADE
            )
        """)

        # Create default teacher
        teacher = db.execute("""
            SELECT id FROM users
            WHERE username = ?
        """, ("teacher",)).fetchone()

        if not teacher:
            db.execute("""
                INSERT INTO users
                (username, password, role)
                VALUES (?, ?, ?)
            """, (
                "teacher",
                generate_password_hash("teacher123"),
                "teacher"
            ))

        # Create default student
        student = db.execute("""
            SELECT id FROM users
            WHERE username = ?
        """, ("student",)).fetchone()

        if not student:
            db.execute("""
                INSERT INTO users
                (username, password, role)
                VALUES (?, ?, ?)
            """, (
                "student",
                generate_password_hash("student123"),
                "student"
            ))

        db.commit()


# =========================
# LOGIN
# =========================

def login_user(username, password):

    with get_connection() as db:

        user = db.execute("""
            SELECT *
            FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        if user and check_password_hash(user["password"], password):
            return user

        return None


# =========================
# STUDENTS
# =========================

def get_students():

    with get_connection() as db:

        return db.execute("""
            SELECT *
            FROM students
            ORDER BY roll_number ASC
        """).fetchall()


def add_student(roll, name):

    with get_connection() as db:

        db.execute("""
            INSERT INTO students
            (roll_number, name)
            VALUES (?, ?)
        """, (int(roll), name))

        db.commit()


def delete_student(student_id):

    with get_connection() as db:

        db.execute("""
            DELETE FROM students
            WHERE id = ?
        """, (student_id,))

        db.commit()


# =========================
# LECTURES
# =========================

def add_lecture(
    lecture_date,
    lecture_number,
    subject,
    start_time,
    end_time
):

    with get_connection() as db:

        cursor = db.execute("""
            INSERT INTO lectures
            (
                lecture_date,
                lecture_number,
                subject,
                start_time,
                end_time
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            lecture_date,
            int(lecture_number),
            subject,
            start_time,
            end_time
        ))

        db.commit()

        return cursor.lastrowid


def get_lectures():

    with get_connection() as db:

        return db.execute("""
            SELECT *
            FROM lectures
            ORDER BY lecture_date DESC, id DESC
        """).fetchall()


def get_lecture(lecture_id):

    with get_connection() as db:

        return db.execute("""
            SELECT *
            FROM lectures
            WHERE id = ?
        """, (lecture_id,)).fetchone()


# =========================
# ATTENDANCE
# =========================

def save_attendance(student_id, lecture_id, status):

    with get_connection() as db:

        existing = db.execute("""
            SELECT id
            FROM lecture_attendance
            WHERE student_id = ?
            AND lecture_id = ?
        """, (
            student_id,
            lecture_id
        )).fetchone()

        if existing:

            db.execute("""
                UPDATE lecture_attendance
                SET status = ?
                WHERE student_id = ?
                AND lecture_id = ?
            """, (
                status,
                student_id,
                lecture_id
            ))

        else:

            db.execute("""
                INSERT INTO lecture_attendance
                (
                    student_id,
                    lecture_id,
                    status
                )
                VALUES (?, ?, ?)
            """, (
                student_id,
                lecture_id,
                status
            ))

        db.commit()


def get_lecture_attendance(lecture_id):

    with get_connection() as db:

        return db.execute("""
            SELECT
                s.id,
                s.roll_number,
                s.name,
                COALESCE(la.status, 'Absent') AS status

            FROM students s

            LEFT JOIN lecture_attendance la

            ON s.id = la.student_id
            AND la.lecture_id = ?

            ORDER BY s.roll_number ASC

        """, (lecture_id,)).fetchall()


# =========================
# STUDENT REPORT
# =========================

def get_student_attendance():

    with get_connection() as db:

        return db.execute("""
            SELECT
                s.id,
                s.roll_number,
                s.name,

                COUNT(la.id) AS total,

                COALESCE(
                    SUM(
                        CASE
                            WHEN la.status = 'Present'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS present

            FROM students s

            LEFT JOIN lecture_attendance la
            ON s.id = la.student_id

            GROUP BY
                s.id,
                s.roll_number,
                s.name

            ORDER BY s.roll_number ASC

        """).fetchall()


# =========================
# DASHBOARD
# =========================

def get_dashboard_stats():

    with get_connection() as db:

        students = db.execute("""
            SELECT COUNT(*) AS count
            FROM students
        """).fetchone()["count"]

        lectures = db.execute("""
            SELECT COUNT(*) AS count
            FROM lectures
        """).fetchone()["count"]

        present = db.execute("""
            SELECT COUNT(*) AS count
            FROM lecture_attendance
            WHERE status = 'Present'
        """).fetchone()["count"]

        absent = db.execute("""
            SELECT COUNT(*) AS count
            FROM lecture_attendance
            WHERE status = 'Absent'
        """).fetchone()["count"]

        return {
            "students": students,
            "lectures": lectures,
            "present": present,
            "absent": absent
        }


setup_database()
