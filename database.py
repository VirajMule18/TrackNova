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

        # =========================
        # STUDENTS
        # =========================

        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL
            )
        """)

        # Add extra student columns to old database
        columns = [
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        ]

        if "class_id" not in columns:
            db.execute(
                "ALTER TABLE students ADD COLUMN class_id INTEGER"
            )

        if "email" not in columns:
            db.execute(
                "ALTER TABLE students ADD COLUMN email TEXT DEFAULT ''"
            )

        # =========================
        # CLASSES
        # =========================

        db.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                department TEXT NOT NULL,
                semester TEXT NOT NULL,
                division TEXT DEFAULT ''
            )
        """)

        # =========================
        # USERS
        # =========================

        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK(role IN ('admin','teacher','student')),
                student_id INTEGER,
                active INTEGER DEFAULT 1,

                FOREIGN KEY(student_id)
                    REFERENCES students(id)
                    ON DELETE SET NULL
            )
        """)

        # =========================
        # SUBJECTS
        # =========================

        db.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                subject_code TEXT DEFAULT '',
                class_id INTEGER,
                teacher_id INTEGER,

                FOREIGN KEY(class_id)
                    REFERENCES classes(id)
                    ON DELETE SET NULL,

                FOREIGN KEY(teacher_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL
            )
        """)

        # =========================
        # LECTURES
        # =========================

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

        lecture_columns = [
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(lectures)"
            ).fetchall()
        ]

        if "teacher_id" not in lecture_columns:
            db.execute(
                "ALTER TABLE lectures ADD COLUMN teacher_id INTEGER"
            )

        if "class_id" not in lecture_columns:
            db.execute(
                "ALTER TABLE lectures ADD COLUMN class_id INTEGER"
            )

        if "subject_id" not in lecture_columns:
            db.execute(
                "ALTER TABLE lectures ADD COLUMN subject_id INTEGER"
            )

        # =========================
        # ATTENDANCE
        # =========================

        db.execute("""
            CREATE TABLE IF NOT EXISTS lecture_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                student_id INTEGER NOT NULL,

                lecture_id INTEGER NOT NULL,

                status TEXT NOT NULL
                    CHECK(status IN ('Present','Absent')),

                UNIQUE(student_id, lecture_id),

                FOREIGN KEY(student_id)
                    REFERENCES students(id)
                    ON DELETE CASCADE,

                FOREIGN KEY(lecture_id)
                    REFERENCES lectures(id)
                    ON DELETE CASCADE
            )
        """)

        # =========================
        # DEFAULT ADMIN
        # =========================

        admin = db.execute("""
            SELECT id
            FROM users
            WHERE username = ?
        """, ("admin",)).fetchone()

        if not admin:

            db.execute("""
                INSERT INTO users
                (
                    username,
                    password_hash,
                    full_name,
                    role
                )
                VALUES (?, ?, ?, ?)
            """, (
                "admin",
                generate_password_hash("admin123"),
                "TrackNova Administrator",
                "admin"
            ))

        db.commit()


# =========================================================
# STUDENTS
# =========================================================

def get_students():

    with get_connection() as db:

        return db.execute("""
            SELECT
                s.*,
                c.class_name,
                c.department,
                c.semester,
                c.division

            FROM students s

            LEFT JOIN classes c
                ON s.class_id = c.id

            ORDER BY
                CAST(s.roll_number AS INTEGER) ASC

        """).fetchall()


def add_student(
    roll,
    name,
    class_id=None,
    email=""
):

    with get_connection() as db:

        db.execute("""
            INSERT INTO students
            (
                roll_number,
                name,
                class_id,
                email
            )
            VALUES (?, ?, ?, ?)
        """, (
            int(roll),
            name,
            class_id or None,
            email
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
# CLASSES
# =========================================================

def get_classes():

    with get_connection() as db:

        return db.execute("""
            SELECT *
            FROM classes

            ORDER BY
                department,
                class_name,
                division

        """).fetchall()


def add_class(
    class_name,
    department,
    semester,
    division=""
):

    with get_connection() as db:

        db.execute("""
            INSERT INTO classes
            (
                class_name,
                department,
                semester,
                division
            )
            VALUES (?, ?, ?, ?)
        """, (
            class_name,
            department,
            semester,
            division
        ))

        db.commit()


# =========================================================
# USERS
# =========================================================

def authenticate(
    username,
    password
):

    with get_connection() as db:

        user = db.execute("""
            SELECT *
            FROM users

            WHERE username = ?
            AND active = 1

        """, (username,)).fetchone()

    if user:

        try:

            if check_password_hash(
                user["password_hash"],
                password
            ):

                return user

        except Exception:

            return None

    return None


def get_users(role=None):

    with get_connection() as db:

        if role:

            return db.execute("""
                SELECT *
                FROM users

                WHERE role = ?

                ORDER BY full_name

            """, (role,)).fetchall()

        return db.execute("""
            SELECT *
            FROM users
            ORDER BY full_name
        """).fetchall()


def create_user(
    username,
    password,
    full_name,
    role,
    student_id=None
):

    with get_connection() as db:

        db.execute("""
            INSERT INTO users
            (
                username,
                password_hash,
                full_name,
                role,
                student_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            username,
            generate_password_hash(password),
            full_name,
            role,
            student_id
        ))

        db.commit()


# =========================================================
# SUBJECTS
# =========================================================

def get_subjects():

    with get_connection() as db:

        return db.execute("""
            SELECT
                sub.*,
                c.class_name,
                c.department,
                u.full_name AS teacher_name

            FROM subjects sub

            LEFT JOIN classes c
                ON sub.class_id = c.id

            LEFT JOIN users u
                ON sub.teacher_id = u.id

            ORDER BY sub.subject_name

        """).fetchall()


def add_subject(
    subject_name,
    subject_code="",
    class_id=None,
    teacher_id=None
):

    with get_connection() as db:

        db.execute("""
            INSERT INTO subjects
            (
                subject_name,
                subject_code,
                class_id,
                teacher_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            subject_name,
            subject_code,
            class_id or None,
            teacher_id or None
        ))

        db.commit()


# =========================================================
# LECTURES
# =========================================================

def add_lecture(
    lecture_date,
    lecture_number,
    subject,
    start_time,
    end_time,
    teacher_id=None,
    class_id=None,
    subject_id=None
):

    with get_connection() as db:

        cursor = db.execute("""
            INSERT INTO lectures
            (
                lecture_date,
                lecture_number,
                subject,
                start_time,
                end_time,
                teacher_id,
                class_id,
                subject_id
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        """, (
            lecture_date,
            int(lecture_number),
            subject,
            start_time,
            end_time,
            teacher_id,
            class_id,
            subject_id
        ))

        db.commit()

        return cursor.lastrowid


def get_lectures():

    with get_connection() as db:

        return db.execute("""
            SELECT
                l.*,
                u.full_name AS teacher_name,
                c.class_name

            FROM lectures l

            LEFT JOIN users u
                ON l.teacher_id = u.id

            LEFT JOIN classes c
                ON l.class_id = c.id

            ORDER BY
                l.lecture_date DESC,
                l.id DESC

        """).fetchall()


def get_lecture(lecture_id):

    with get_connection() as db:

        return db.execute("""
            SELECT
                l.*,
                u.full_name AS teacher_name,
                c.class_name

            FROM lectures l

            LEFT JOIN users u
                ON l.teacher_id = u.id

            LEFT JOIN classes c
                ON l.class_id = c.id

            WHERE l.id = ?

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


def get_lecture_attendance(
    lecture_id
):

    with get_connection() as db:

        return db.execute("""
            SELECT
                s.id,
                s.roll_number,
                s.name,
                s.email,
                la.status

            FROM students s

            LEFT JOIN lecture_attendance la

                ON s.id = la.student_id

                AND la.lecture_id = ?

            ORDER BY
                CAST(s.roll_number AS INTEGER)

        """, (
            lecture_id,
        )).fetchall()


# =========================================================
# REPORT
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
                CAST(s.roll_number AS INTEGER)

        """).fetchall()


# =========================================================
# TODAY
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
