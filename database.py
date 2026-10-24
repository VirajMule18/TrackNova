```python
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

        # Students
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL
            )
        """)

        # Login accounts
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                student_id INTEGER,
                FOREIGN KEY(student_id)
                    REFERENCES students(id)
                    ON DELETE CASCADE
            )
        """)

        # Lectures
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

        # Attendance
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

        db.commit()


# =====================================================
# LOGIN
# =====================================================

def teacher_exists():

    with get_connection() as db:
        result = db.execute("""
            SELECT id
            FROM users
            WHERE role = 'teacher'
            LIMIT 1
        """).fetchone()

        return result is not None


def create_teacher(password):

    with get_connection() as db:

        hashed = generate_password_hash(password)

        db.execute("""
            INSERT INTO users
            (username, password, role)
            VALUES (?, ?, ?)
        """, (
            "teacher",
            hashed,
            "teacher"
        ))

        db.commit()


def verify_login(username, password):

    with get_connection() as db:

        user = db.execute("""
            SELECT *
            FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        if user is None:
            return None

        if check_password_hash(
            user["password"],
            password
        ):
            return user

        return None


# =====================================================
# STUDENTS
# =====================================================

def get_students():

    with get_connection() as db:

        return db.execute("""
            SELECT *
            FROM students
            ORDER BY CAST(roll_number AS INTEGER)
        """).fetchall()


def get_student(student_id):

    with get_connection() as db:

        return db.execute("""
            SELECT *
            FROM students
            WHERE id = ?
        """, (student_id,)).fetchone()


def add_student(roll, name, password):

    with get_connection() as db:

        existing = db.execute("""
            SELECT id
            FROM students
            WHERE roll_number = ?
        """, (int(roll),)).fetchone()

        if existing:
            return False

        cursor = db.execute("""
            INSERT INTO students
            (roll_number, name)
            VALUES (?, ?)
        """, (
            int(roll),
            name.strip()
        ))

        student_id = cursor.lastrowid

        hashed = generate_password_hash(password)

        db.execute("""
            INSERT INTO users
            (username, password, role, student_id)
            VALUES (?, ?, ?, ?)
        """, (
            str(roll),
            hashed,
            "student",
            student_id
        ))

        db.commit()

        return True


def delete_student(student_id):

    with get_connection() as db:

        db.execute("""
            DELETE FROM students
            WHERE id = ?
        """, (student_id,))

        db.commit()


# =====================================================
# LECTURES
# =====================================================

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
            subject.strip(),
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


def delete_lecture(lecture_id):

    with get_connection() as db:

        db.execute("""
            DELETE FROM lectures
            WHERE id = ?
        """, (lecture_id,))

        db.commit()


# =====================================================
# ATTENDANCE
# =====================================================

def save_attendance(
    student_id,
    lecture_id,
    status
):

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
                COALESCE(
                    la.status,
                    'Not Marked'
                ) AS status

            FROM students s

            LEFT JOIN lecture_attendance la
            ON s.id = la.student_id
            AND la.lecture_id = ?

            ORDER BY CAST(s.roll_number AS INTEGER)
        """, (lecture_id,)).fetchall()


# =====================================================
# STUDENT ATTENDANCE
# =====================================================

def get_student_attendance(student_id):

    with get_connection() as db:

        return db.execute("""
            SELECT
                l.id,
                l.lecture_date,
                l.lecture_number,
                l.subject,
                l.start_time,
                l.end_time,
                COALESCE(
                    la.status,
                    'Not Marked'
                ) AS status

            FROM lectures l

            LEFT JOIN lecture_attendance la
            ON l.id = la.lecture_id
            AND la.student_id = ?

            ORDER BY
                l.lecture_date DESC,
                l.id DESC
        """, (student_id,)).fetchall()


def get_student_summary(student_id):

    with get_connection() as db:

        return db.execute("""
            SELECT
                COUNT(l.id) AS total,

                COALESCE(
                    SUM(
                        CASE
                            WHEN la.status = 'Present'
                            THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS present,

                COALESCE(
                    SUM(
                        CASE
                            WHEN la.status = 'Absent'
                            THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS absent

            FROM lectures l

            LEFT JOIN lecture_attendance la
            ON l.id = la.lecture_id
            AND la.student_id = ?
        """, (student_id,)).fetchone()


# =====================================================
# DASHBOARD
# =====================================================

def get_dashboard_stats():

    with get_connection() as db:

        students = db.execute("""
            SELECT COUNT(*) AS total
            FROM students
        """).fetchone()["total"]

        lectures = db.execute("""
            SELECT COUNT(*) AS total
            FROM lectures
        """).fetchone()["total"]

        present = db.execute("""
            SELECT COUNT(*) AS total
            FROM lecture_attendance
            WHERE status = 'Present'
        """).fetchone()["total"]

        absent = db.execute("""
            SELECT COUNT(*) AS total
            FROM lecture_attendance
            WHERE status = 'Absent'
        """).fetchone()["total"]

        return {
            "students": students,
            "lectures": lectures,
            "present": present,
            "absent": absent
        }


# =====================================================
# REPORT
# =====================================================

def get_attendance_report():

    with get_connection() as db:

        return db.execute("""
            SELECT
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
                    ), 0
                ) AS present,

                COALESCE(
                    SUM(
                        CASE
                            WHEN la.status = 'Absent'
                            THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS absent

            FROM students s

            LEFT JOIN lecture_attendance la
            ON s.id = la.student_id

            GROUP BY
                s.id,
                s.roll_number,
                s.name

            ORDER BY
                CAST(s.roll_number AS INTEGER)
        """).fetchall()


# =====================================================
# SUBJECT REPORT
# =====================================================

def get_subject_report():

    with get_connection() as db:

        return db.execute("""
            SELECT
                l.subject,
                COUNT(la.id) AS total,

                COALESCE(
                    SUM(
                        CASE
                            WHEN la.status = 'Present'
                            THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS present

            FROM lectures l

            LEFT JOIN lecture_attendance la
            ON l.id = la.lecture_id

            GROUP BY l.subject

            ORDER BY l.subject
        """).fetchall()


# Start database
setup_database()
```
