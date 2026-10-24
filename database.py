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


# =========================================================
# DATABASE SETUP
# =========================================================

def setup_database():

    with get_connection() as db:

        # STUDENTS
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number INTEGER NOT NULL UNIQUE,
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

        # USERS
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL UNIQUE,

                password TEXT NOT NULL,

                role TEXT NOT NULL
                CHECK(role IN ('teacher', 'student')),

                student_id INTEGER UNIQUE,

                FOREIGN KEY(student_id)
                    REFERENCES students(id)
                    ON DELETE CASCADE
            )
        """)

        db.commit()

        # -------------------------------------------------
        # CREATE DEFAULT TEACHER
        # -------------------------------------------------

        teacher = db.execute("""
            SELECT id
            FROM users
            WHERE username = ?
        """, ("teacher",)).fetchone()

        if not teacher:

            db.execute("""
                INSERT INTO users
                (
                    username,
                    password,
                    role
                )
                VALUES (?, ?, ?)
            """, (
                "teacher",
                generate_password_hash("teacher123"),
                "teacher"
            ))

        db.commit()

        # -------------------------------------------------
        # CREATE LOGIN FOR EXISTING STUDENTS
        # -------------------------------------------------

        students = db.execute("""
            SELECT *
            FROM students
        """).fetchall()

        for student in students:

            username = str(student["roll_number"])

            existing = db.execute("""
                SELECT id
                FROM users
                WHERE student_id = ?
            """, (student["id"],)).fetchone()

            if not existing:

                db.execute("""
                    INSERT OR IGNORE INTO users
                    (
                        username,
                        password,
                        role,
                        student_id
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    username,
                    generate_password_hash("student123"),
                    "student",
                    student["id"]
                ))

        db.commit()


# =========================================================
# STUDENTS
# =========================================================

def get_students():

    with get_connection() as db:

        return db.execute("""
            SELECT *
            FROM students
            ORDER BY CAST(roll_number AS INTEGER) ASC
        """).fetchall()


def add_student(roll, name):

    with get_connection() as db:

        cursor = db.execute("""
            INSERT INTO students
            (
                roll_number,
                name
            )
            VALUES (?, ?)
        """, (
            int(roll),
            name
        ))

        student_id = cursor.lastrowid

        # Create student login
        db.execute("""
            INSERT INTO users
            (
                username,
                password,
                role,
                student_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            str(roll),
            generate_password_hash("student123"),
            "student",
            student_id
        ))

        db.commit()


def delete_student(student_id):

    with get_connection() as db:

        db.execute("""
            DELETE FROM students
            WHERE id = ?
        """, (student_id,))

        db.commit()


# =========================================================
# LOGIN
# =========================================================

def authenticate_user(username, password):

    with get_connection() as db:

        user = db.execute("""
            SELECT *
            FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        if not user:
            return None

        if check_password_hash(
            user["password"],
            password
        ):

            return user

        return None


# =========================================================
# LECTURES
# =========================================================

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


# =========================================================
# ATTENDANCE
# =========================================================

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
                la.status

            FROM students s

            LEFT JOIN lecture_attendance la

                ON s.id = la.student_id

                AND la.lecture_id = ?

            ORDER BY
                CAST(s.roll_number AS INTEGER) ASC

        """, (lecture_id,)).fetchall()


# =========================================================
# STUDENT ATTENDANCE REPORT
# =========================================================

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

            ORDER BY
                CAST(s.roll_number AS INTEGER) ASC

        """).fetchall()


# =========================================================
# SINGLE STUDENT REPORT
# =========================================================

def get_single_student_attendance(student_id):

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

            WHERE s.id = ?

            GROUP BY
                s.id,
                s.roll_number,
                s.name

        """, (student_id,)).fetchone()


# =========================================================
# STUDENT HISTORY
# =========================================================

def get_student_history(student_id):

    with get_connection() as db:

        return db.execute("""
            SELECT
                l.lecture_date,
                l.lecture_number,
                l.subject,
                l.start_time,
                l.end_time,
                la.status

            FROM lecture_attendance la

            INNER JOIN lectures l

                ON la.lecture_id = l.id

            WHERE la.student_id = ?

            ORDER BY
                l.lecture_date DESC,
                l.id DESC

        """, (student_id,)).fetchall()


# =========================================================
# TODAY ATTENDANCE
# =========================================================

def get_today_attendance(today):

    with get_connection() as db:

        return db.execute("""
            SELECT

                COALESCE(
                    SUM(
                        CASE
                            WHEN la.status = 'Present'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS present,

                COALESCE(
                    SUM(
                        CASE
                            WHEN la.status = 'Absent'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS absent

            FROM lecture_attendance la

            INNER JOIN lectures l

                ON la.lecture_id = l.id

            WHERE l.lecture_date = ?

        """, (today,)).fetchone()


# =========================================================
# START DATABASE
# =========================================================

setup_database()
