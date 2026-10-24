from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template_string,
    flash,
    session
)

import database
import os
from datetime import date


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "tracknova-secret-key-change-this"
)

database.setup_database()


# =========================================================
# LOGIN REQUIRED
# =========================================================

def teacher_required():

    return (
        session.get("logged_in") is True
        and session.get("role") == "teacher"
    )


def student_required():

    return (
        session.get("logged_in") is True
        and session.get("role") == "student"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = database.authenticate_user(
            username,
            password
        )

        if user:

            session.clear()

            session["logged_in"] = True

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            session["role"] = user["role"]

            if user["role"] == "student":

                session["student_id"] = user["student_id"]

                return redirect(
                    url_for("student_dashboard")
                )

            return redirect(
                url_for("home")
            )

        flash(
            "Invalid username or password."
        )

    return render_template_string(
        LOGIN_HTML
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# TEACHER DASHBOARD
# =========================================================

@app.route("/")
def home():

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    students = database.get_students()

    lectures = database.get_lectures()

    today = str(date.today())

    today_data = database.get_today_attendance(
        today
    )

    present = (
        today_data["present"]
        if today_data
        else 0
    )

    absent = (
        today_data["absent"]
        if today_data
        else 0
    )

    total_students = len(students)

    total_marked = present + absent

    if total_marked > 0:

        attendance_percentage = round(
            present / total_marked * 100,
            1
        )

    else:

        attendance_percentage = 0

    return render_template_string(
        DASHBOARD_HTML,

        students=students,

        lectures=lectures,

        present=present,

        absent=absent,

        total_students=total_students,

        attendance_percentage=
        attendance_percentage,

        username=session.get(
            "username"
        )
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/student")
def student_dashboard():

    if not student_required():

        return redirect(
            url_for("login")
        )

    student_id = session.get(
        "student_id"
    )

    student = database.get_single_student_attendance(
        student_id
    )

    history = database.get_student_history(
        student_id
    )

    total = (
        student["total"]
        if student
        else 0
    )

    present = (
        student["present"]
        if student
        else 0
    )

    if total > 0:

        percentage = round(
            present / total * 100,
            1
        )

    else:

        percentage = 0

    return render_template_string(
        STUDENT_HTML,

        student=student,

        history=history,

        total=total,

        present=present,

        percentage=percentage
    )


# =========================================================
# STUDENTS
# =========================================================

@app.route("/students")
def students_page():

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    students = database.get_students()

    return render_template_string(
        STUDENTS_HTML,
        students=students
    )


# =========================================================
# ADD STUDENT
# =========================================================

@app.route(
    "/add_student",
    methods=["POST"]
)
def add_student():

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    roll = request.form.get(
        "roll_number"
    )

    name = request.form.get(
        "name"
    )

    if not roll or not name:

        flash(
            "Please fill all fields."
        )

        return redirect(
            url_for("students_page")
        )

    try:

        database.add_student(
            roll,
            name
        )

        flash(
            "Student added successfully."
        )

    except Exception:

        flash(
            "Could not add student. "
            "Roll number may already exist."
        )

    return redirect(
        url_for("students_page")
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@app.route(
    "/delete_student/<int:student_id>",
    methods=["POST"]
)
def delete_student(student_id):

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    database.delete_student(
        student_id
    )

    flash(
        "Student deleted successfully."
    )

    return redirect(
        url_for("students_page")
    )


# =========================================================
# LECTURES
# =========================================================

@app.route("/lectures")
def lectures_page():

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    lectures = database.get_lectures()

    return render_template_string(
        LECTURES_HTML,
        lectures=lectures
    )


# =========================================================
# ADD LECTURE
# =========================================================

@app.route(
    "/add_lecture",
    methods=["POST"]
)
def add_lecture():

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    lecture_date = request.form.get(
        "lecture_date"
    )

    lecture_number = request.form.get(
        "lecture_number"
    )

    subject = request.form.get(
        "subject"
    )

    start_time = request.form.get(
        "start_time"
    )

    end_time = request.form.get(
        "end_time"
    )

    if not all([
        lecture_date,
        lecture_number,
        subject,
        start_time,
        end_time
    ]):

        flash(
            "Please fill all lecture details."
        )

        return redirect(
            url_for("lectures_page")
        )

    try:

        lecture_id = database.add_lecture(
            lecture_date,
            lecture_number,
            subject,
            start_time,
            end_time
        )

        return redirect(
            url_for(
                "attendance_page",
                lecture_id=lecture_id
            )
        )

    except Exception:

        flash(
            "Could not create lecture."
        )

        return redirect(
            url_for("lectures_page")
        )


# =========================================================
# ATTENDANCE
# =========================================================

@app.route(
    "/attendance/<int:lecture_id>"
)
def attendance_page(lecture_id):

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    lecture = database.get_lecture(
        lecture_id
    )

    if not lecture:

        flash(
            "Lecture not found."
        )

        return redirect(
            url_for("lectures_page")
        )

    students = database.get_lecture_attendance(
        lecture_id
    )

    return render_template_string(
        ATTENDANCE_HTML,

        lecture=lecture,

        students=students
    )


# =========================================================
# SAVE ATTENDANCE
# =========================================================

@app.route(
    "/save_attendance/<int:lecture_id>",
    methods=["POST"]
)
def save_attendance(lecture_id):

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    students = database.get_students()

    for student in students:

        status = request.form.get(
            f"student_{student['id']}"
        )

        if status not in [
            "Present",
            "Absent"
        ]:

            status = "Absent"

        database.save_attendance(
            student["id"],
            lecture_id,
            status
        )

    flash(
        "Attendance saved successfully!"
    )

    return redirect(
        url_for(
            "attendance_page",
            lecture_id=lecture_id
        )
    )


# =========================================================
# REPORTS
# =========================================================

@app.route("/reports")
def reports():

    if not teacher_required():

        return redirect(
            url_for("login")
        )

    students = database.get_student_attendance()

    return render_template_string(
        REPORT_HTML,
        students=students
    )


# =========================================================
# COMMON CSS
# =========================================================

CSS = """

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    font-family:
    Arial,
    Helvetica,
    sans-serif;

    background:
    linear-gradient(
        135deg,
        #eef2ff,
        #f8fafc
    );

    color: #172033;

    min-height: 100vh;
}

.navbar {

    background:
    linear-gradient(
        135deg,
        #111827,
        #2563eb
    );

    color: white;

    padding: 17px 7%;

    display: flex;

    justify-content:
    space-between;

    align-items: center;

    position: sticky;

    top: 0;

    z-index: 1000;

    box-shadow:
    0 5px 20px
    rgba(0,0,0,.12);
}

.logo {

    font-size: 25px;

    font-weight: bold;
}

.nav-links {

    display: flex;

    gap: 8px;

    flex-wrap: wrap;
}

.nav-links a {

    color: white;

    text-decoration: none;

    padding:
    9px 13px;

    border-radius: 10px;

    transition:
    .3s;
}

.nav-links a:hover {

    background:
    rgba(255,255,255,.2);

    transform:
    translateY(-2px);
}

.container {

    width: 86%;

    max-width: 1200px;

    margin:
    35px auto;
}

.hero {

    background:
    linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    );

    color: white;

    padding: 45px;

    border-radius: 25px;

    margin-bottom: 30px;

    box-shadow:
    0 15px 40px
    rgba(37,99,235,.2);

    animation:
    fadeUp .7s ease;
}

.hero h1 {

    font-size: 42px;

    margin:
    0 0 10px;
}

.hero p {

    font-size: 18px;

    opacity: .9;
}

.cards {

    display: grid;

    grid-template-columns:
    repeat(
        auto-fit,
        minmax(210px,1fr)
    );

    gap: 20px;

    margin-bottom: 30px;
}

.card {

    background: white;

    padding: 25px;

    border-radius: 18px;

    box-shadow:
    0 8px 25px
    rgba(0,0,0,.07);

    transition:
    .3s;

    animation:
    fadeUp .6s ease;
}

.card:hover {

    transform:
    translateY(-7px);

    box-shadow:
    0 15px 35px
    rgba(0,0,0,.12);
}

.card h3 {

    margin-top: 0;

    color:
    #64748b;
}

.number {

    font-size: 35px;

    font-weight: bold;

    color:
    #2563eb;
}

.section {

    background: white;

    padding: 28px;

    border-radius: 18px;

    box-shadow:
    0 8px 25px
    rgba(0,0,0,.06);

    margin-bottom: 25px;

    animation:
    fadeUp .5s ease;
}

.section h2 {

    margin-top: 0;
}

input,
select {

    width: 100%;

    padding: 13px;

    border:
    1px solid #dbe2ea;

    border-radius: 10px;

    margin:
    6px 0 15px;

    font-size: 15px;

    outline: none;
}

input:focus {

    border-color:
    #2563eb;

    box-shadow:
    0 0 0 3px
    rgba(37,99,235,.1);
}

button,
.btn {

    border: none;

    background:
    #2563eb;

    color: white;

    padding:
    12px 18px;

    border-radius: 10px;

    cursor: pointer;

    text-decoration: none;

    display: inline-block;

    transition:
    .3s;
}

button:hover,
.btn:hover {

    background:
    #1d4ed8;

    transform:
    translateY(-2px);
}

.btn-green {

    background:
    #16a34a;
}

.btn-red {

    background:
    #dc2626;
}

.btn-purple {

    background:
    #7c3aed;
}

.btn-dark {

    background:
    #111827;
}

table {

    width: 100%;

    border-collapse:
    collapse;
}

th,
td {

    padding: 14px;

    border-bottom:
    1px solid #edf0f5;

    text-align:
    left;
}

th {

    background:
    #f8fafc;
}

tr:hover {

    background:
    #f8fbff;
}

.alert {

    padding:
    14px 18px;

    background:
    #e0f2fe;

    border-left:
    5px solid #0284c7;

    border-radius:
    10px;

    margin-bottom:
    20px;
}

.progress {

    height:
    14px;

    background:
    #e5e7eb;

    border-radius:
    20px;

    overflow:
    hidden;
}

.progress-bar {

    height:
    100%;

    background:
    linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );

    transition:
    width 1s ease;
}

.present {

    color:
    #16a34a;

    font-weight:
    bold;
}

.absent {

    color:
    #dc2626;

    font-weight:
    bold;
}

.login-page {

    min-height:
    100vh;

    display:
    flex;

    align-items:
    center;

    justify-content:
    center;

    padding:
    20px;
}

.login-box {

    background:
    white;

    width:
    100%;

    max-width:
    430px;

    padding:
    40px;

    border-radius:
    25px;

    box-shadow:
    0 20px 60px
    rgba(0,0,0,.12);

    animation:
    fadeUp .7s ease;
}

.login-logo {

    text-align:
    center;

    font-size:
    32px;

    font-weight:
    bold;

    color:
    #2563eb;

    margin-bottom:
    10px;
}

.login-subtitle {

    text-align:
    center;

    color:
    #64748b;

    margin-bottom:
    30px;
}

.role-box {

    background:
    #eff6ff;

    border-radius:
    12px;

    padding:
    15px;

    margin-bottom:
    20px;

    text-align:
    center;

    color:
    #1d4ed8;
}

.footer {

    text-align:
    center;

    padding:
    35px;

    color:
    #64748b;
}

.badge {

    display:
    inline-block;

    padding:
    6px 10px;

    border-radius:
    20px;

    font-size:
    12px;

    font-weight:
    bold;
}

.badge-green {

    background:
    #dcfce7;

    color:
    #15803d;
}

.badge-red {

    background:
    #fee2e2;

    color:
    #b91c1c;
}

@keyframes fadeUp {

    from {

        opacity: 0;

        transform:
        translateY(20px);
    }

    to {

        opacity: 1;

        transform:
        translateY(0);
    }
}

@media(max-width:700px) {

    .navbar {

        flex-direction:
        column;

        gap:
        15px;
    }

    .hero h1 {

        font-size:
        30px;
    }

    .container {

        width:
        94%;
    }

    table {

        font-size:
        13px;
    }

}

</style>

"""


# =========================================================
# LOGIN HTML
# =========================================================

LOGIN_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>TrackNova Login</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>


<div class="login-page">


<div class="login-box">


<div class="login-logo">

🚀 TrackNova

</div>


<div class="login-subtitle">

Smart Attendance Management System

</div>


<div class="role-box">

🔐 Secure Login

</div>


{% with messages =
get_flashed_messages() %}

{% for message in messages %}

<div class="alert">

{{ message }}

</div>

{% endfor %}

{% endwith %}


<form method="POST">


<label>

Username / Roll Number

</label>


<input

type="text"

name="username"

placeholder="Enter username"

required>


<label>

Password

</label>


<input

type="password"

name="password"

placeholder="Enter password"

required>


<button
type="submit"
style="width:100%;">

Login

</button>


</form>


<br>


<div style="
text-align:center;
color:#64748b;
font-size:13px;
">

Teacher: <b>teacher</b>
/
<b>teacher123</b>

<br><br>

Student:
use your <b>Roll Number</b>
/
<b>student123</b>

</div>


</div>


</div>


</body>

</html>

"""


# =========================================================
# TEACHER DASHBOARD
# =========================================================

DASHBOARD_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>TrackNova Teacher Dashboard</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>


<nav class="navbar">


<div class="logo">

🚀 TrackNova

</div>


<div class="nav-links">

<a href="/">

Dashboard

</a>

<a href="/students">

Students

</a>

<a href="/lectures">

Lectures

</a>

<a href="/reports">

Reports

</a>

<a href="/logout">

Logout

</a>

</div>


</nav>


<div class="container">


<div class="hero">

<h1>

👨‍🏫 Teacher Dashboard

</h1>


<p>

Welcome, {{ username }}!

Manage students, lectures
and attendance from one place.

</p>


<a
class="btn"
href="/lectures">

+ Create Lecture

</a>


<a
class="btn btn-purple"
href="/students">

Manage Students

</a>

</div>


<div class="cards">


<div class="card">

<h3>
👨‍🎓 Total Students
</h3>

<div class="number">

{{ total_students }}

</div>

</div>


<div class="card">

<h3>
✅ Present Today
</h3>

<div class="number">

{{ present }}

</div>

</div>


<div class="card">

<h3>
❌ Absent Today
</h3>

<div class="number">

{{ absent }}

</div>

</div>


<div class="card">

<h3>
📊 Attendance
</h3>

<div class="number">

{{ attendance_percentage }}%

</div>


<div class="progress">

<div
class="progress-bar"
style="
width: {{ attendance_percentage }}%;
">

</div>

</div>


</div>


</div>


<div class="section">


<h2>
📚 Recent Lectures
</h2>


{% if lectures %}


<table>

<tr>

<th>Date</th>

<th>Lecture</th>

<th>Subject</th>

<th>Time</th>

<th>Action</th>

</tr>


{% for lecture in lectures[:7] %}


<tr>

<td>
{{ lecture["lecture_date"] }}
</td>

<td>
Lecture {{ lecture["lecture_number"] }}
</td>

<td>
{{ lecture["subject"] }}
</td>

<td>
{{ lecture["start_time"] }}
-
{{ lecture["end_time"] }}
</td>

<td>

<a
class="btn"
href="/attendance/{{ lecture['id'] }}">

Attendance

</a>

</td>

</tr>


{% endfor %}


</table>


{% else %}

<p>

No lectures created yet.

</p>

{% endif %}


</div>


</div>


<div class="footer">

TrackNova © 2026

</div>


</body>

</html>

"""


# =========================================================
# STUDENT PAGE
# =========================================================

STUDENT_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>My Attendance - TrackNova</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>


<nav class="navbar">


<div class="logo">

🚀 TrackNova

</div>


<div class="nav-links">

<a href="/student">

My Attendance

</a>

<a href="/logout">

Logout

</a>

</div>


</nav>


<div class="container">


<div class="hero">

<h1>

👨‍🎓 My Attendance

</h1>


<p>

{{ student["name"] }}

<br>

Roll Number:
{{ student["roll_number"] }}

</p>


</div>


<div class="cards">


<div class="card">

<h3>
Total Lectures
</h3>

<div class="number">

{{ total }}

</div>

</div>


<div class="card">

<h3>
Present
</h3>

<div class="number">

{{ present }}

</div>

</div>


<div class="card">

<h3>
Attendance
</h3>

<div class="number">

{{ percentage }}%

</div>


<div class="progress">

<div
class="progress-bar"
style="
width: {{ percentage }}%;
">

</div>

</div>

</div>


</div>


<div class="section">


<h2>

📊 Attendance Status

</h2>


{% if percentage >= 75 %}

<div class="badge badge-green">

Good Attendance ✓

</div>

<p>

Your attendance is above 75%.

</p>


{% else %}

<div class="badge badge-red">

Low Attendance ⚠

</div>

<p>

Your attendance is below 75%.
Please attend more lectures.

</p>

{% endif %}


</div>


<div class="section">


<h2>

📚 Attendance History

</h2>


{% if history %}


<table>


<tr>

<th>
Date
</th>

<th>
Subject
</th>

<th>
Lecture
</th>

<th>
Time
</th>

<th>
Status
</th>

</tr>


{% for item in history %}


<tr>

<td>

{{ item["lecture_date"] }}

</td>


<td>

{{ item["subject"] }}

</td>


<td>

Lecture
{{ item["lecture_number"] }}

</td>


<td>

{{ item["start_time"] }}
-
{{ item["end_time"] }}

</td>


<td>


{% if item["status"] == "Present" %}

<span class="badge badge-green">

Present

</span>

{% else %}

<span class="badge badge-red">

Absent

</span>

{% endif %}


</td>


</tr>


{% endfor %}


</table>


{% else %}


<p>

No attendance records available yet.

</p>


{% endif %}


</div>


</div>


<div class="footer">

TrackNova © 2026

</div>


</body>

</html>

"""


# =========================================================
# STUDENTS HTML
# =========================================================

STUDENTS_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>Students - TrackNova</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>


<nav class="navbar">


<div class="logo">
🚀 TrackNova
</div>


<div class="nav-links">

<a href="/">
Dashboard
</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

<a href="/logout">
Logout
</a>

</div>


</nav>


<div class="container">


{% with messages =
get_flashed_messages() %}


{% for message in messages %}


<div class="alert">

{{ message }}

</div>


{% endfor %}


{% endwith %}


<div class="section">


<h2>

👨‍🎓 Add Student

</h2>


<p style="color:#64748b;">

A student login will automatically
be created using the roll number.

</p>


<form
method="POST"
action="/add_student">


<label>

Roll Number

</label>


<input
type="number"
name="roll_number"
placeholder="Example: 101"
required>


<label>

Student Name

</label>


<input
type="text"
name="name"
placeholder="Enter student name"
required>


<button
type="submit">

+ Add Student

</button>


</form>


</div>


<div class="section">


<h2>

👥 Student List

</h2>


{% if students %}


<table>


<tr>

<th>
Roll Number
</th>

<th>
Name
</th>

<th>
Student Login
</th>

<th>
Action
</th>

</tr>


{% for student in students %}


<tr>


<td>

{{ student["roll_number"] }}

</td>


<td>

{{ student["name"] }}

</td>


<td>

Username:
<b>
{{ student["roll_number"] }}
</b>

<br>

Password:
<b>
student123
</b>

</td>


<td>


<form
method="POST"
action="/delete_student/{{ student['id'] }}">


<button
class="btn-red"
type="submit">

Delete

</button>


</form>


</td>


</tr>


{% endfor %}


</table>


{% else %}


<p>

No students added yet.

</p>


{% endif %}


</div>


</div>


<div class="footer">

TrackNova © 2026

</div>


</body>

</html>

"""


# =========================================================
# LECTURES HTML
# =========================================================

LECTURES_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>Lectures - TrackNova</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>


<nav class="navbar">


<div class="logo">

🚀 TrackNova

</div>


<div class="nav-links">

<a href="/">
Dashboard
</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

<a href="/logout">
Logout
</a>

</div>


</nav>


<div class="container">


{% with messages =
get_flashed_messages() %}


{% for message in messages %}

<div class="alert">

{{ message }}

</div>

{% endfor %}


{% endwith %}


<div class="section">


<h2>

📚 Create New Lecture

</h2>


<form
method="POST"
action="/add_lecture">


<label>
Date
</label>


<input
type="date"
name="lecture_date"
required>


<label>
Lecture Number
</label>


<input
type="number"
name="lecture_number"
min="1"
placeholder="Example: 1"
required>


<label>
Subject
</label>


<input
type="text"
name="subject"
placeholder="Example: Data Structures"
required>


<label>
Start Time
</label>


<input
type="time"
name="start_time"
required>


<label>
End Time
</label>


<input
type="time"
name="end_time"
required>


<button type="submit">

Create Lecture
& Take Attendance

</button>


</form>


</div>


<div class="section">


<h2>

📖 Previous Lectures

</h2>


{% if lectures %}


<table>


<tr>

<th>Date</th>

<th>No.</th>

<th>Subject</th>

<th>Time</th>

<th>Action</th>

</tr>


{% for lecture in lectures %}


<tr>


<td>
{{ lecture["lecture_date"] }}
</td>


<td>
{{ lecture["lecture_number"] }}
</td>


<td>
{{ lecture["subject"] }}
</td>


<td>

{{ lecture["start_time"] }}
-

{{ lecture["end_time"] }}

</td>


<td>


<a
class="btn"
href="/attendance/{{ lecture['id'] }}">

Take Attendance

</a>


</td>


</tr>


{% endfor %}


</table>


{% else %}


<p>
No lectures available.
</p>


{% endif %}


</div>


</div>


<div class="footer">

TrackNova © 2026

</div>


</body>

</html>

"""


# =========================================================
# ATTENDANCE HTML
# =========================================================

ATTENDANCE_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>
Take Attendance - TrackNova
</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>


<nav class="navbar">


<div class="logo">
🚀 TrackNova
</div>


<div class="nav-links">

<a href="/">
Dashboard
</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

<a href="/logout">
Logout
</a>

</div>


</nav>


<div class="container">


{% with messages =
get_flashed_messages() %}


{% for message in messages %}


<div class="alert">

{{ message }}

</div>


{% endfor %}


{% endwith %}


<div class="hero">


<h1>

✅ Take Attendance

</h1>


<p>

{{ lecture["subject"] }}

<br>

{{ lecture["lecture_date"] }}

|

Lecture
{{ lecture["lecture_number"] }}

|

{{ lecture["start_time"] }}
-
{{ lecture["end_time"] }}

</p>


</div>


<div class="section">


<form
method="POST"
action="/save_attendance/{{ lecture['id'] }}">


<table>


<tr>

<th>
Roll No.
</th>

<th>
Student Name
</th>

<th>
Attendance
</th>

</tr>


{% for student in students %}


<tr>


<td>

{{ student["roll_number"] }}

</td>


<td>

{{ student["name"] }}

</td>


<td>


<label>

<input
type="radio"
name="student_{{ student['id'] }}"
value="Present"
{% if student["status"] == "Present" %}
checked
{% endif %}
>

<span class="present">

Present

</span>

</label>


&nbsp;&nbsp;


<label>

<input
type="radio"
name="student_{{ student['id'] }}"
value="Absent"
{% if student["status"] == "Absent" %}
checked
{% endif %}
>

<span class="absent">

Absent

</span>

</label>


</td>


</tr>


{% endfor %}


</table>


<br>


<button type="submit">

💾 Save Attendance

</button>


</form>


</div>


</div>


<div class="footer">

TrackNova © 2026

</div>


</body>

</html>

"""


# =========================================================
# REPORT HTML
# =========================================================

REPORT_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>
Reports - TrackNova
</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>


<nav class="navbar">


<div class="logo">
🚀 TrackNova
</div>


<div class="nav-links">

<a href="/">
Dashboard
</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

<a href="/logout">
Logout
</a>

</div>


</nav>


<div class="container">


<div class="hero">

<h1>

📊 Attendance Reports

</h1>


<p>

Complete student attendance overview.

</p>

</div>


<div class="section">


<table>


<tr>

<th>
Roll No.
</th>

<th>
Student
</th>

<th>
Total Lectures
</th>

<th>
Present
</th>

<th>
Attendance
</th>

</tr>


{% for student in students %}


<tr>


<td>

{{ student["roll_number"] }}

</td>


<td>

{{ student["name"] }}

</td>


<td>

{{ student["total"] }}

</td>


<td class="present">

{{ student["present"] }}

</td>


<td>


{% if student["total"] > 0 %}


{% set percentage =
(student["present"] /
student["total"] * 100)
|round(1)
%}


<strong>

{{ percentage }}%

</strong>


<div class="progress">


<div
class="progress-bar"
style="
width: {{ percentage }}%;
">

</div>


</div>


{% else %}


No attendance


{% endif %}


</td>


</tr>


{% endfor %}


</table>


</div>


</div>


<div class="footer">

TrackNova © 2026

</div>


</body>

</html>

"""


# =========================================================
# START APP
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )
