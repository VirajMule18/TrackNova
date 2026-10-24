from flask import Flask, request, redirect, url_for, render_template_string, flash
import database
from datetime import date

app = Flask(__name__)
app.secret_key = "tracknova-secret-key"

# Make sure database tables exist
database.setup_database()


# =========================================================
# MAIN DASHBOARD
# =========================================================

@app.route("/")
def home():

    students = database.get_students()
    lectures = database.get_lectures()

    today = str(date.today())

    today_data = database.get_today_attendance(today)

    present = today_data["present"] if today_data else 0
    absent = today_data["absent"] if today_data else 0

    total_students = len(students)

    if total_students > 0:
        attendance_percentage = round(
            (present / (present + absent)) * 100, 1
        ) if (present + absent) > 0 else 0
    else:
        attendance_percentage = 0

    return render_template_string(
        DASHBOARD_HTML,
        students=students,
        lectures=lectures,
        present=present,
        absent=absent,
        total_students=total_students,
        attendance_percentage=attendance_percentage
    )


# =========================================================
# STUDENTS PAGE
# =========================================================

@app.route("/students")
def students_page():

    students = database.get_students()

    return render_template_string(
        STUDENTS_HTML,
        students=students
    )


# =========================================================
# ADD STUDENT
# =========================================================

@app.route("/add_student", methods=["POST"])
def add_student():

    roll = request.form.get("roll_number")
    name = request.form.get("name")

    if not roll or not name:
        flash("Please enter roll number and student name.")
        return redirect(url_for("students_page"))

    try:
        database.add_student(roll, name)
        flash("Student added successfully!")

    except Exception as e:
        flash("Could not add student. Roll number may already exist.")

    return redirect(url_for("students_page"))


# =========================================================
# DELETE STUDENT
# =========================================================

@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    database.delete_student(student_id)

    flash("Student deleted successfully.")

    return redirect(url_for("students_page"))


# =========================================================
# LECTURES PAGE
# =========================================================

@app.route("/lectures")
def lectures_page():

    lectures = database.get_lectures()

    return render_template_string(
        LECTURES_HTML,
        lectures=lectures
    )


# =========================================================
# ADD LECTURE
# =========================================================

@app.route("/add_lecture", methods=["POST"])
def add_lecture():

    lecture_date = request.form.get("lecture_date")
    lecture_number = request.form.get("lecture_number")
    subject = request.form.get("subject")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    if not all([
        lecture_date,
        lecture_number,
        subject,
        start_time,
        end_time
    ]):

        flash("Please fill all lecture details.")

        return redirect(url_for("lectures_page"))

    try:

        lecture_id = database.add_lecture(
            lecture_date,
            lecture_number,
            subject,
            start_time,
            end_time
        )

        flash("Lecture created successfully!")

        return redirect(
            url_for(
                "attendance_page",
                lecture_id=lecture_id
            )
        )

    except Exception as e:

        flash("Could not create lecture.")

        return redirect(url_for("lectures_page"))


# =========================================================
# ATTENDANCE PAGE
# =========================================================

@app.route("/attendance/<int:lecture_id>")
def attendance_page(lecture_id):

    lecture = database.get_lecture(lecture_id)

    if not lecture:
        flash("Lecture not found.")
        return redirect(url_for("lectures_page"))

    students = database.get_lecture_attendance(lecture_id)

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

    students = database.get_students()

    for student in students:

        status = request.form.get(
            f"student_{student['id']}"
        )

        if status not in ["Present", "Absent"]:
            status = "Absent"

        database.save_attendance(
            student["id"],
            lecture_id,
            status
        )

    flash("Attendance saved successfully!")

    return redirect(
        url_for(
            "attendance_page",
            lecture_id=lecture_id
        )
    )


# =========================================================
# REPORT
# =========================================================

@app.route("/reports")
def reports():

    students = database.get_student_attendance()

    return render_template_string(
        REPORT_HTML,
        students=students
    )


# =========================================================
# CSS
# =========================================================

CSS = """
<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f4f7fb;
    color: #172033;
}

.navbar {
    background: linear-gradient(
        135deg,
        #111827,
        #2563eb
    );

    color: white;
    padding: 18px 7%;

    display: flex;
    justify-content: space-between;
    align-items: center;

    position: sticky;
    top: 0;
    z-index: 100;
}

.logo {
    font-size: 25px;
    font-weight: bold;
}

.nav-links {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.nav-links a {
    color: white;
    text-decoration: none;
    padding: 9px 14px;
    border-radius: 10px;
    transition: 0.3s;
}

.nav-links a:hover {
    background: rgba(255,255,255,0.18);
    transform: translateY(-2px);
}

.container {
    width: 86%;
    max-width: 1200px;
    margin: 35px auto;
}

.hero {
    background: linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    );

    color: white;
    padding: 45px;
    border-radius: 25px;
    margin-bottom: 30px;

    animation: fadeUp 0.7s ease;
}

.hero h1 {
    font-size: 42px;
    margin: 0 0 10px;
}

.hero p {
    font-size: 18px;
    opacity: 0.9;
}

.cards {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));

    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 18px;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.07);

    transition: 0.3s;

    animation: fadeUp 0.6s ease;
}

.card:hover {
    transform: translateY(-7px);

    box-shadow:
        0 15px 35px rgba(0,0,0,0.12);
}

.card h3 {
    margin-top: 0;
    color: #64748b;
}

.number {
    font-size: 35px;
    font-weight: bold;
    color: #2563eb;
}

.section {
    background: white;
    padding: 28px;
    border-radius: 18px;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.06);

    margin-bottom: 25px;
}

.section h2 {
    margin-top: 0;
}

input,
select {
    width: 100%;
    padding: 13px;

    border: 1px solid #dbe2ea;
    border-radius: 10px;

    margin: 6px 0 15px;

    font-size: 15px;
}

button,
.btn {
    border: none;
    background: #2563eb;
    color: white;

    padding: 12px 18px;

    border-radius: 10px;

    cursor: pointer;

    text-decoration: none;

    display: inline-block;

    transition: 0.3s;
}

button:hover,
.btn:hover {
    background: #1d4ed8;
    transform: translateY(-2px);
}

.btn-green {
    background: #16a34a;
}

.btn-red {
    background: #dc2626;
}

.btn-purple {
    background: #7c3aed;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 14px;
    border-bottom: 1px solid #edf0f5;
    text-align: left;
}

th {
    background: #f8fafc;
}

tr:hover {
    background: #f8fbff;
}

.alert {
    padding: 14px 18px;
    background: #e0f2fe;
    border-left: 5px solid #0284c7;

    border-radius: 10px;

    margin-bottom: 20px;
}

.progress {
    height: 14px;
    background: #e5e7eb;
    border-radius: 20px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );

    transition: width 1s ease;
}

.present {
    color: #16a34a;
    font-weight: bold;
}

.absent {
    color: #dc2626;
    font-weight: bold;
}

.attendance-option {
    display: inline-flex;
    gap: 7px;
    align-items: center;
    margin-right: 10px;
}

.attendance-option input {
    width: auto;
}

.footer {
    text-align: center;
    padding: 35px;
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
        gap: 15px;
    }

    .hero h1 {
        font-size: 30px;
    }

    .container {
        width: 94%;
    }

    table {
        font-size: 13px;
    }

}

</style>
"""


# =========================================================
# DASHBOARD HTML
# =========================================================

DASHBOARD_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>TrackNova Dashboard</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>

<nav class="navbar">

<div class="logo">
🚀 TrackNova
</div>

<div class="nav-links">

<a href="/">Dashboard</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

</div>

</nav>


<div class="container">


<div class="hero">

<h1>
TrackNova Attendance
</h1>

<p>
Smart • Simple • Modern Attendance Management
</p>

<a class="btn"
href="/lectures">
+ Create Lecture
</a>

<a class="btn btn-purple"
href="/students">
Manage Students
</a>

</div>


<div class="cards">


<div class="card">

<h3>Total Students</h3>

<div class="number">
{{ total_students }}
</div>

</div>


<div class="card">

<h3>Present Today</h3>

<div class="number">
{{ present }}
</div>

</div>


<div class="card">

<h3>Absent Today</h3>

<div class="number">
{{ absent }}
</div>

</div>


<div class="card">

<h3>Attendance Rate</h3>

<div class="number">
{{ attendance_percentage }}%
</div>

<div class="progress">

<div class="progress-bar"
style="width: {{ attendance_percentage }}%">
</div>

</div>

</div>


</div>


<div class="section">

<h2>📊 Today's Overview</h2>

<p>
Track attendance and manage your lectures
from one simple dashboard.
</p>

</div>


<div class="section">

<h2>📚 Recent Lectures</h2>

{% if lectures %}

<table>

<tr>

<th>Date</th>

<th>Lecture</th>

<th>Subject</th>

<th>Time</th>

<th>Action</th>

</tr>


{% for lecture in lectures[:5] %}

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

<a class="btn"
href="/attendance/{{ lecture['id'] }}">

Take Attendance

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
<br>
Smart Attendance Management System

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

<title>TrackNova Students</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>

<nav class="navbar">

<div class="logo">
🚀 TrackNova
</div>

<div class="nav-links">

<a href="/">Dashboard</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

</div>

</nav>


<div class="container">


{% with messages = get_flashed_messages() %}

{% for message in messages %}

<div class="alert">
{{ message }}
</div>

{% endfor %}

{% endwith %}


<div class="section">

<h2>👨‍🎓 Add Student</h2>

<form method="POST"
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


<button type="submit">
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

<th>Roll Number</th>

<th>Name</th>

<th>Action</th>

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

<form method="POST"
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

<title>TrackNova Lectures</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>

<nav class="navbar">

<div class="logo">
🚀 TrackNova
</div>

<div class="nav-links">

<a href="/">Dashboard</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

</div>

</nav>


<div class="container">


{% with messages = get_flashed_messages() %}

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


<form method="POST"
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

Create Lecture & Take Attendance

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

<a class="btn"
href="/attendance/{{ lecture['id'] }}">

Attendance

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

<title>Take Attendance - TrackNova</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>

<nav class="navbar">

<div class="logo">
🚀 TrackNova
</div>

<div class="nav-links">

<a href="/">Dashboard</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

</div>

</nav>


<div class="container">


{% with messages = get_flashed_messages() %}

{% for message in messages %}

<div class="alert">
{{ message }}
</div>

{% endfor %}

{% endwith %}


<div class="hero">

<h1>
Take Attendance
</h1>

<p>

{{ lecture["subject"] }}

<br>

{{ lecture["lecture_date"] }}

|

Lecture {{ lecture["lecture_number"] }}

|

{{ lecture["start_time"] }}
-
{{ lecture["end_time"] }}

</p>

</div>


<div class="section">


<form method="POST"
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


<label class="attendance-option">

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


<label class="attendance-option">

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

<title>TrackNova Reports</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + CSS + """

</head>

<body>

<nav class="navbar">

<div class="logo">
🚀 TrackNova
</div>

<div class="nav-links">

<a href="/">Dashboard</a>

<a href="/students">
Students
</a>

<a href="/lectures">
Lectures
</a>

<a href="/reports">
Reports
</a>

</div>

</nav>


<div class="container">


<div class="hero">

<h1>
📊 Attendance Reports
</h1>

<p>
View overall student attendance performance.
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
Attendance %
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
(student["present"] / student["total"] * 100)
|round(1)
%}

<strong>
{{ percentage }}%
</strong>

<div class="progress">

<div class="progress-bar"
style="width: {{ percentage }}%">
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
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
