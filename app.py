```python
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session,
    render_template_string
)

from functools import wraps
import database


app = Flask(__name__)

app.secret_key = "TRACKNOVA_SECRET_KEY_2026_CHANGE_THIS"


# =====================================================
# DESIGN
# =====================================================

STYLE = """

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background:
        linear-gradient(135deg,#eef2ff,#f8fafc);
    color: #172033;
}

.navbar {
    position: sticky;
    top: 0;
    z-index: 100;
    padding: 16px 6%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #0f172a;
    color: white;
    box-shadow: 0 5px 25px rgba(0,0,0,.15);
}

.logo {
    font-size: 28px;
    font-weight: bold;
}

.logo span {
    color: #60a5fa;
}

.navlinks {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}

.container {
    width: 90%;
    max-width: 1250px;
    margin: 35px auto;
}

.hero {
    padding: 50px 35px;
    border-radius: 28px;
    color: white;
    background:
        linear-gradient(
            135deg,
            #2563eb,
            #4f46e5,
            #7c3aed
        );
    box-shadow:
        0 25px 60px
        rgba(37,99,235,.25);
    animation: fadeUp .7s ease;
}

.hero h1 {
    font-size: 42px;
    margin: 0 0 10px;
}

.hero p {
    font-size: 18px;
    opacity: .9;
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit,minmax(210px,1fr));
    gap: 20px;
}

.card {
    background: white;
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 22px;
    box-shadow:
        0 12px 35px
        rgba(15,23,42,.08);
    animation: fadeUp .5s ease;
}

.stat {
    padding: 25px;
    border-radius: 20px;
    background: white;
    box-shadow:
        0 8px 25px
        rgba(15,23,42,.07);
    transition: .3s;
}

.stat:hover {
    transform: translateY(-6px);
}

.stat h3 {
    color: #64748b;
}

.stat strong {
    display: block;
    font-size: 35px;
    color: #2563eb;
}

input,
select {
    width: 100%;
    padding: 13px;
    margin: 7px 0 15px;
    border: 1px solid #d1d5db;
    border-radius: 12px;
    font-size: 15px;
}

input:focus,
select:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow:
        0 0 0 4px
        rgba(37,99,235,.1);
}

label {
    font-weight: bold;
}

button,
.btn {
    border: none;
    padding: 12px 18px;
    border-radius: 12px;
    background: #2563eb;
    color: white;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: .25s;
}

button:hover,
.btn:hover {
    transform: translateY(-2px);
    background: #1d4ed8;
}

.btn-purple {
    background: #7c3aed;
}

.btn-green {
    background: #16a34a;
}

.btn-red {
    background: #dc2626;
}

.btn-gray {
    background: #64748b;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 13px;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
}

th {
    background: #f8fafc;
}

.badge {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: bold;
}

.present {
    background: #dcfce7;
    color: #15803d;
}

.absent {
    background: #fee2e2;
    color: #b91c1c;
}

.notmarked {
    background: #fef3c7;
    color: #92400e;
}

.error {
    background: #fee2e2;
    color: #991b1b;
    padding: 13px;
    border-radius: 12px;
    margin-bottom: 15px;
}

.success {
    background: #dcfce7;
    color: #166534;
    padding: 13px;
    border-radius: 12px;
    margin-bottom: 15px;
}

.login-box {
    max-width: 450px;
    margin: 70px auto;
}

.center {
    text-align: center;
}

.icon {
    font-size: 45px;
}

.flex {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
}

.progress {
    width: 100%;
    height: 16px;
    background: #e5e7eb;
    border-radius: 30px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background:
        linear-gradient(
            90deg,
            #2563eb,
            #7c3aed
        );
    border-radius: 30px;
}

.footer {
    text-align: center;
    padding: 30px;
    color: #64748b;
}

@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media(max-width:700px) {

    .navbar {
        flex-direction: column;
        gap: 12px;
    }

    .hero h1 {
        font-size: 32px;
    }

    table {
        font-size: 12px;
    }

}

</style>
"""


# =====================================================
# LOGIN PROTECTION
# =====================================================

def teacher_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if session.get("role") != "teacher":
            return redirect(
                url_for("teacher_login")
            )

        return function(*args, **kwargs)

    return wrapper


def student_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if session.get("role") != "student":
            return redirect(
                url_for("student_login")
            )

        return function(*args, **kwargs)

    return wrapper


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<title>TrackNova</title>

{{ style|safe }}

</head>

<body>

<div class="navbar">

<div class="logo">
Track<span>Nova</span>
</div>

<div class="navlinks">

<a class="btn"
href="{{ url_for('teacher_login') }}">
👨‍🏫 Teacher
</a>

<a class="btn btn-purple"
href="{{ url_for('student_login') }}">
👨‍🎓 Student
</a>

</div>

</div>


<div class="container">

<div class="hero">

<h1>
TrackNova
</h1>

<p>
Smart College Attendance Management System
</p>

<div class="flex">

<a class="btn"
href="{{ url_for('teacher_login') }}">
Teacher Login
</a>

<a class="btn btn-purple"
href="{{ url_for('student_login') }}">
Student Login
</a>

</div>

</div>


<br>


<div class="grid">

<div class="card center">

<div class="icon">📊</div>

<h2>
Smart Dashboard
</h2>

<p>
Manage attendance easily.
</p>

</div>


<div class="card center">

<div class="icon">🔐</div>

<h2>
Secure Login
</h2>

<p>
Separate teacher and student accounts.
</p>

</div>


<div class="card center">

<div class="icon">📈</div>

<h2>
Attendance Analytics
</h2>

<p>
Automatic attendance percentage.
</p>

</div>


<div class="card center">

<div class="icon">📱</div>

<h2>
Mobile Friendly
</h2>

<p>
Works on mobile and computer.
</p>

</div>

</div>

</div>


<div class="footer">

TrackNova © 2026

</div>


</body>

</html>

""", style=STYLE)


# =====================================================
# FIRST TEACHER SETUP
# =====================================================

@app.route(
    "/setup-teacher",
    methods=["GET","POST"]
)
def setup_teacher():

    if database.teacher_exists():

        return redirect(
            url_for("teacher_login")
        )


    error = None


    if request.method == "POST":

        password = request.form.get(
            "password"
        )

        confirm = request.form.get(
            "confirm"
        )


        if len(password) < 6:

            error = (
                "Password must contain "
                "at least 6 characters."
            )

        elif password != confirm:

            error = "Passwords do not match."

        else:

            database.create_teacher(
                password
            )

            return redirect(
                url_for("teacher_login")
            )


    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<title>Create Teacher</title>

{{ style|safe }}

</head>

<body>

<div class="container">

<div class="login-box card">

<div class="center">

<div class="icon">
👨‍🏫
</div>

<h2>
Create Teacher Account
</h2>

<p>
Username: <b>teacher</b>
</p>

</div>


{% if error %}

<div class="error">
{{ error }}
</div>

{% endif %}


<form method="POST">

<label>
Create Password
</label>

<input
type="password"
name="password"
required
>

<label>
Confirm Password
</label>

<input
type="password"
name="confirm"
required
>

<button>
Create Account
</button>

</form>

</div>

</div>

</body>

</html>

""", style=STYLE)


# =====================================================
# TEACHER LOGIN
# =====================================================

@app.route(
    "/teacher-login",
    methods=["GET","POST"]
)
def teacher_login():

    if not database.teacher_exists():

        return redirect(
            url_for("setup_teacher")
        )


    error = None


    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )


        user = database.verify_login(
            username,
            password
        )


        if user and user["role"] == "teacher":

            session.clear()

            session["user_id"] = user["id"]

            session["role"] = "teacher"

            return redirect(
                url_for("teacher_dashboard")
            )


        error = "❌ Wrong username or password."


    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<title>Teacher Login</title>

{{ style|safe }}

</head>

<body>

<div class="container">

<div class="login-box card">

<div class="center">

<div class="icon">
👨‍🏫
</div>

<h2>
Teacher Login
</h2>

</div>


{% if error %}

<div class="error">
{{ error }}
</div>

{% endif %}


<form method="POST">

<label>
Username
</label>

<input
type="text"
name="username"
placeholder="teacher"
required
>

<label>
Password
</label>

<input
type="password"
name="password"
required
>

<button>
Login
</button>

</form>

<br>

<a
class="btn btn-gray"
href="{{ url_for('home') }}">
← Back
</a>

</div>

</div>

</body>

</html>

""", style=STYLE)


# =====================================================
# STUDENT LOGIN
# =====================================================

@app.route(
    "/student-login",
    methods=["GET","POST"]
)
def student_login():

    error = None


    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )


        user = database.verify_login(
            username,
            password
        )


        if user and user["role"] == "student":

            session.clear()

            session["user_id"] = user["id"]

            session["role"] = "student"

            session["student_id"] = (
                user["student_id"]
            )

            return redirect(
                url_for("student_dashboard")
            )


        error = (
            "❌ Wrong roll number or password."
        )


    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<title>Student Login</title>

{{ style|safe }}

</head>

<body>

<div class="container">

<div class="login-box card">

<div class="center">

<div class="icon">
👨‍🎓
</div>

<h2>
Student Login
</h2>

</div>


{% if error %}

<div class="error">
{{ error }}
</div>

{% endif %}


<form method="POST">

<label>
Roll Number
</label>

<input
type="text"
name="username"
placeholder="Enter roll number"
required
>

<label>
Password
</label>

<input
type="password"
name="password"
required
>

<button>
Login
</button>

</form>

<br>

<a
class="btn btn-gray"
href="{{ url_for('home') }}">
← Back
</a>

</div>

</div>

</body>

</html>

""", style=STYLE)


# =====================================================
# TEACHER DASHBOARD
# =====================================================

@app.route("/teacher")
@teacher_required
def teacher_dashboard():

    stats = database.get_dashboard_stats()

    students = database.get_students()

    lectures = database.get_lectures()

    reports = database.get_attendance_report()


    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<title>Teacher Dashboard</title>

{{ style|safe }}

</head>

<body>


<div class="navbar">

<div class="logo">
Track<span>Nova</span>
</div>

<div class="navlinks">

<span>
👨‍🏫 Teacher
</span>

<a
class="btn btn-red"
href="{{ url_for('logout') }}">
Logout
</a>

</div>

</div>


<div class="container">


<div class="hero">

<h1>
Teacher Dashboard
</h1>

<p>
Manage students, lectures and attendance.
</p>

</div>


<br>


<div class="grid">


<div class="stat">

<h3>
👨‍🎓 Students
</h3>

<strong>
{{ stats.students }}
</strong>

</div>


<div class="stat">

<h3>
📚 Lectures
</h3>

<strong>
{{ stats.lectures }}
</strong>

</div>


<div class="stat">

<h3>
✅ Present
</h3>

<strong>
{{ stats.present }}
</strong>

</div>


<div class="stat">

<h3>
❌ Absent
</h3>

<strong>
{{ stats.absent }}
</strong>

</div>

</div>


<br>


<!-- ADD STUDENT -->

<div class="card">

<h2>
➕ Add Student
</h2>

<form
method="POST"
action="{{ url_for('add_student') }}"
>

<div class="grid">

<div>

<label>
Roll Number
</label>

<input
type="number"
name="roll"
required
>

</div>


<div>

<label>
Student Name
</label>

<input
type="text"
name="name"
required
>

</div>


<div>

<label>
Student Password
</label>

<input
type="password"
name="password"
required
>

</div>

</div>


<button>
Add Student
</button>

</form>

</div>


<!-- CREATE LECTURE -->

<div class="card">

<h2>
📚 Create Lecture
</h2>

<form
method="POST"
action="{{ url_for('add_lecture') }}"
>

<div class="grid">

<div>

<label>
Date
</label>

<input
type="date"
name="lecture_date"
required
>

</div>


<div>

<label>
Lecture Number
</label>

<input
type="number"
name="lecture_number"
required
>

</div>


<div>

<label>
Subject
</label>

<input
type="text"
name="subject"
required
>

</div>


<div>

<label>
Start Time
</label>

<input
type="time"
name="start_time"
required
>

</div>


<div>

<label>
End Time
</label>

<input
type="time"
name="end_time"
required
>

</div>

</div>


<button>
Create Lecture
</button>

</form>

</div>


<!-- STUDENTS -->

<div class="card">

<h2>
👥 Students
</h2>


<table>

<tr>

<th>
Roll No.
</th>

<th>
Name
</th>

<th>
Action
</th>

</tr>


{% for s in students %}

<tr>

<td>
{{ s.roll_number }}
</td>

<td>
{{ s.name }}
</td>

<td>

<a
class="btn btn-red"
href="{{ url_for('delete_student', student_id=s.id) }}"
onclick="return confirm('Delete this student?')"
>
Delete
</a>

</td>

</tr>

{% endfor %}

</table>

</div>


<!-- LECTURES -->

<div class="card">

<h2>
📚 Lectures
</h2>


<table>

<tr>

<th>
Date
</th>

<th>
Lecture
</th>

<th>
Subject
</th>

<th>
Attendance
</th>

</tr>


{% for l in lectures %}

<tr>

<td>
{{ l.lecture_date }}
</td>

<td>
{{ l.lecture_number }}
</td>

<td>
{{ l.subject }}
</td>

<td>

<a
class="btn"
href="{{ url_for('mark_attendance', lecture_id=l.id) }}"
>
Mark Attendance
</a>

</td>

</tr>

{% endfor %}

</table>

</div>


<!-- REPORT -->

<div class="card">

<h2>
📊 Attendance Report
</h2>


<table>

<tr>

<th>
Roll
</th>

<th>
Name
</th>

<th>
Present
</th>

<th>
Total
</th>

<th>
Percentage
</th>

</tr>


{% for r in reports %}

{% set percentage =
(r.present * 100 / r.total)
if r.total else 0
%}


<tr>

<td>
{{ r.roll_number }}
</td>

<td>
{{ r.name }}
</td>

<td>
{{ r.present }}
</td>

<td>
{{ r.total }}
</td>

<td>

<b>
{{ "%.1f"|format(percentage) }}%
</b>

<br>

<div class="progress">

<div
class="progress-bar"
style="width: {{ percentage }}%">
</div>

</div>

</td>

</tr>


{% endfor %}

</table>

</div>


</div>


<div class="footer">

TrackNova Teacher Panel

</div>


</body>

</html>

""", style=STYLE)


# =====================================================
# ADD STUDENT
# =====================================================

@app.route(
    "/add-student",
    methods=["POST"]
)
@teacher_required
def add_student():

    roll = request.form.get("roll")

    name = request.form.get("name")

    password = request.form.get("password")


    if roll and name and password:

        database.add_student(
            roll,
            name,
            password
        )


    return redirect(
        url_for("teacher_dashboard")
    )


# =====================================================
# DELETE STUDENT
# =====================================================

@app.route(
    "/delete-student/<int:student_id>"
)
@teacher_required
def delete_student(student_id):

    database.delete_student(
        student_id
    )

    return redirect(
        url_for("teacher_dashboard")
    )


# =====================================================
# ADD LECTURE
# =====================================================

@app.route(
    "/add-lecture",
    methods=["POST"]
)
@teacher_required
def add_lecture():

    database.add_lecture(

        request.form.get(
            "lecture_date"
        ),

        request.form.get(
            "lecture_number"
        ),

        request.form.get(
            "subject"
        ),

        request.form.get(
            "start_time"
        ),

        request.form.get(
            "end_time"
        )
    )


    return redirect(
        url_for("teacher_dashboard")
    )


# =====================================================
# MARK ATTENDANCE
# =====================================================

@app.route(
    "/attendance/<int:lecture_id>",
    methods=["GET","POST"]
)
@teacher_required
def mark_attendance(lecture_id):

    lecture = database.get_lecture(
        lecture_id
    )

    students = database.get_lecture_attendance(
        lecture_id
    )


    if request.method == "POST":

        for student in students:

            status = request.form.get(
                f"status_{student['id']}"
            )

            if status in [
                "Present",
                "Absent"
            ]:

                database.save_attendance(
                    student["id"],
                    lecture_id,
                    status
                )


        return redirect(
            url_for(
                "mark_attendance",
                lecture_id=lecture_id
            )
        )


    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<title>Mark Attendance</title>

{{ style|safe }}

</head>

<body>


<div class="navbar">

<div class="logo">
Track<span>Nova</span>
</div>

<a
class="btn btn-gray"
href="{{ url_for('teacher_dashboard') }}">
← Dashboard
</a>

</div>


<div class="container">


<div class="hero">

<h1>
Mark Attendance
</h1>

<p>
{{ lecture.subject }}
|
{{ lecture.lecture_date }}
|
Lecture {{ lecture.lecture_number }}
</p>

</div>


<br>


<form method="POST">


<div class="card">


<table>

<tr>

<th>
Roll
</th>

<th>
Student
</th>

<th>
Status
</th>

</tr>


{% for s in students %}

<tr>

<td>
{{ s.roll_number }}
</td>

<td>
{{ s.name }}
</td>

<td>


<select
name="status_{{ s.id }}"
>

<option
value="Present"
{% if s.status == "Present" %}
selected
{% endif %}
>
Present
</option>


<option
value="Absent"
{% if s.status == "Absent" %}
selected
{% endif %}
>
Absent
</option>


</select>


</td>

</tr>

{% endfor %}

</table>


<br>


<button class="btn-green">
💾 Save Attendance
</button>


</div>


</form>


</div>


</body>

</html>

""", style=STYLE)


# =====================================================
# STUDENT DASHBOARD
# =====================================================

@app.route("/student")
@student_required
def student_dashboard():

    student_id = session.get(
        "student_id"
    )


    student = database.get_student(
        student_id
    )


    attendance = database.get_student_attendance(
        student_id
    )


    summary = database.get_student_summary(
        student_id
    )


    total = summary["total"]

    present = summary["present"]

    percentage = (
        present * 100 / total
        if total else 0
    )


    return render_template_string("""

<!DOCTYPE html>

<html>

<head>

<title>Student Dashboard</title>

{{ style|safe }}

</head>

<body>


<div class="navbar">

<div class="logo">
Track<span>Nova</span>
</div>

<div class="navlinks">

<span>
👨‍🎓 {{ student.name }}
</span>

<a
class="btn btn-red"
href="{{ url_for('logout') }}">
Logout
</a>

</div>

</div>


<div class="container">


<div class="hero">

<h1>
Hello, {{ student.name }} 👋
</h1>

<p>
Roll Number: {{ student.roll_number }}
</p>

</div>


<br>


<div class="grid">


<div class="stat">

<h3>
📚 Total Lectures
</h3>

<strong>
{{ total }}
</strong>

</div>


<div class="stat">

<h3>
✅ Present
</h3>

<strong>
{{ present }}
</strong>

</div>


<div class="stat">

<h3>
❌ Absent
</h3>

<strong>
{{ summary.absent }}
</strong>

</div>


<div class="stat">

<h3>
📊 Attendance
</h3>

<strong>
{{ "%.1f"|format(percentage) }}%
</strong>

</div>


</div>


<br>


<div class="card">

<h2>
📊 My Attendance
</h2>


<div class="progress">

<div
class="progress-bar"
style="width: {{ percentage }}%">
</div>

</div>


<br>


{% if percentage < 75 %}

<div class="error">

⚠️ Your attendance is below 75%.

</div>

{% else %}

<div class="success">

✅ Your attendance is above 75%.

</div>

{% endif %}


</div>


<div class="card">

<h2>
📅 Attendance History
</h2>


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
Status
</th>

</tr>


{% for a in attendance %}

<tr>

<td>
{{ a.lecture_date }}
</td>

<td>
{{ a.subject }}
</td>

<td>
{{ a.lecture_number }}
</td>

<td>


{% if a.status == "Present" %}

<span class="badge present">
Present
</span>


{% elif a.status == "Absent" %}

<span class="badge absent">
Absent
</span>


{% else %}

<span class="badge notmarked">
Not Marked
</span>

{% endif %}


</td>

</tr>

{% endfor %}

</table>


</div>


</div>


<div class="footer">

TrackNova Student Panel

</div>


</body>

</html>

""", style=STYLE)


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
```
