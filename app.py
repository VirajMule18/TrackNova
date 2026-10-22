from flask import Flask, request, redirect, url_for, render_template_string
from datetime import date
import sqlite3

from database import (
    get_connection,
    get_students,
    add_student,
    delete_student,
    add_lecture,
    get_lectures,
    get_lecture,
    save_attendance,
    get_lecture_attendance,
    get_student_attendance,
    get_today_attendance
)


app = Flask(__name__)


# =========================================================
# DESIGN
# =========================================================

STYLE = """
<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f1f5ff;
    color: #202b45;
}

header {
    background: linear-gradient(135deg, #2949a5, #4969ee);
    color: white;
    text-align: center;
    padding: 28px;
}

header h1 {
    margin: 0;
    font-size: 35px;
}

header p {
    margin: 8px 0 0;
}

nav {
    background: white;
    padding: 12px;
    text-align: center;
    box-shadow: 0 2px 8px #ddd;
}

nav a {
    display: inline-block;
    background: #4969ee;
    color: white;
    text-decoration: none;
    padding: 11px 16px;
    margin: 4px;
    border-radius: 8px;
}

nav a:hover {
    background: #2949a5;
}

main {
    max-width: 1150px;
    margin: 25px auto;
    padding: 15px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0 3px 12px #ddd;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}

.stat {
    background: white;
    padding: 20px;
    text-align: center;
    border-radius: 15px;
    box-shadow: 0 3px 12px #ddd;
}

.stat h2 {
    font-size: 30px;
    margin: 10px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 18px;
}

th {
    background: #2949a5;
    color: white;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: left;
}

input, select {
    padding: 10px;
    margin: 5px;
    border: 1px solid #ccd2e0;
    border-radius: 7px;
}

.btn {
    display: inline-block;
    background: #4969ee;
    color: white;
    border: none;
    padding: 11px 17px;
    margin: 5px;
    border-radius: 7px;
    cursor: pointer;
    text-decoration: none;
}

.btn:hover {
    background: #2949a5;
}

.delete {
    background: #d93636;
}

.edit {
    background: #f39c12;
}

.good {
    color: green;
    font-weight: bold;
}

.danger {
    color: red;
    font-weight: bold;
}

.success {
    background: #e5f8e9;
    padding: 12px;
    border-radius: 8px;
}

.warning {
    background: #fff3cd;
    padding: 12px;
    border-radius: 8px;
}

.search {
    width: 90%;
    max-width: 450px;
    padding: 13px;
}

@media(max-width: 800px) {

    .stats {
        grid-template-columns: repeat(2, 1fr);
    }

    table {
        display: block;
        overflow-x: auto;
    }
}

@media(max-width: 500px) {

    .stats {
        grid-template-columns: 1fr;
    }

}

</style>
"""


PAGE = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Track Nova</title>

""" + STYLE + """

</head>

<body>

<header>

<h1>✦ TRACK NOVA</h1>

<p>
Smart Student Attendance Management System
</p>

</header>

<nav>

<a href="/">🏠 Dashboard</a>

<a href="/students">👨‍🎓 Students</a>

<a href="/attendance">📋 Take Attendance</a>

<a href="/lectures">📚 Lecture History</a>

<a href="/reports">📊 Reports</a>

</nav>

<main>

{{ content|safe }}

</main>

</body>

</html>
"""


def page(content, **context):

    return render_template_string(
        PAGE,
        content=render_template_string(
            content,
            **context
        )
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def home():

    today = date.today().isoformat()

    with get_connection() as db:

        total = db.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

    today_data = get_today_attendance(today)

    present = today_data["present"] or 0
    absent = today_data["absent"] or 0

    marked = present + absent

    percentage = (
        round(present * 100 / marked, 1)
        if marked
        else 0
    )

    reports = get_student_attendance()

    low_students = []

    for student in reports:

        total_lectures = student["total"] or 0
        present_lectures = student["present"] or 0

        if total_lectures > 0:

            percent = round(
                present_lectures * 100 /
                total_lectures,
                1
            )

            if percent < 75:

                low_students.append({
                    "roll": student["roll_number"],
                    "name": student["name"],
                    "percentage": percent
                })

    content = """

<div class="card">

<h1>Welcome to Track Nova 👋</h1>

<p>
Today's Date:
<b>{{ today }}</b>
</p>

</div>


<div class="stats">

<div class="stat">
<p>Total Students</p>
<h2>{{ total }}</h2>
</div>

<div class="stat">
<p>Present Today</p>
<h2>{{ present }}</h2>
</div>

<div class="stat">
<p>Absent Today</p>
<h2>{{ absent }}</h2>
</div>

<div class="stat">
<p>Today's Attendance</p>
<h2>{{ percentage }}%</h2>
</div>

</div>


<div class="card">

<h2>⚠️ Low Attendance Warning</h2>

<p>
Students below <b>75%</b> attendance:
</p>


{% if low_students %}

<table>

<tr>
<th>Roll No.</th>
<th>Name</th>
<th>Attendance</th>
</tr>

{% for s in low_students %}

<tr>

<td>{{ s.roll }}</td>

<td>{{ s.name }}</td>

<td class="danger">
{{ s.percentage }}% ⚠️
</td>

</tr>

{% endfor %}

</table>

{% else %}

<div class="success">
🎉 No student is below 75% attendance.
</div>

{% endif %}

</div>


<div class="card">

<h2>⚡ Quick Actions</h2>

<a class="btn" href="/attendance">
📋 Take Attendance
</a>

<a class="btn" href="/students">
👨‍🎓 Students
</a>

<a class="btn" href="/lectures">
📚 Lecture History
</a>

<a class="btn" href="/reports">
📊 Reports
</a>

</div>

"""

    return page(
        content,
        today=today,
        total=total,
        present=present,
        absent=absent,
        percentage=percentage,
        low_students=low_students
    )


# =========================================================
# STUDENTS
# =========================================================

@app.route("/students", methods=["GET", "POST"])
def students_page():

    message = ""

    if request.method == "POST":

        action = request.form.get("action")

        if action == "add":

            roll = request.form.get(
                "roll", ""
            ).strip()

            name = request.form.get(
                "name", ""
            ).strip()

            if roll and name:

                try:

                    add_student(
                        roll,
                        name
                    )

                    message = (
                        "Student added successfully!"
                    )

                except sqlite3.IntegrityError:

                    message = (
                        "This roll number already exists."
                    )

            else:

                message = (
                    "Please enter roll number and name."
                )

        elif action == "delete":

            student_id = request.form.get(
                "student_id"
            )

            try:

                delete_student(student_id)

                message = (
                    "Student deleted successfully."
                )

            except sqlite3.Error:

                message = (
                    "Could not delete student."
                )

    students = get_students()

    content = """

<div class="card">

<h1>👨‍🎓 Manage Students</h1>

{% if message %}

<div class="success">
{{ message }}
</div>

{% endif %}


<h3>Add Student</h3>

<form method="post">

<input
type="hidden"
name="action"
value="add"
>

<input
type="number"
name="roll"
placeholder="Roll Number"
required
>

<input
name="name"
placeholder="Student Full Name"
required
>

<button
class="btn"
type="submit"
>
+ Add Student
</button>

</form>


<p>
Total Students:
<b>{{ students|length }}</b>
</p>


<input
class="search"
id="search"
placeholder="🔍 Search student"
onkeyup="searchStudent()"
>


<table id="studentTable">

<tr>

<th>Roll No.</th>

<th>Name</th>

<th>Action</th>

</tr>


{% for s in students %}

<tr>

<td>
<b>{{ s["roll_number"] }}</b>
</td>

<td>
{{ s["name"] }}
</td>

<td>

<form
method="post"
onsubmit="return confirm('Delete this student?');"
>

<input
type="hidden"
name="action"
value="delete"
>

<input
type="hidden"
name="student_id"
value="{{ s['id'] }}"
>

<button
class="btn delete"
type="submit"
>
Delete
</button>

</form>

</td>

</tr>

{% endfor %}

</table>

</div>


<script>

function searchStudent() {

let text =
document.getElementById("search")
.value.toLowerCase();

let rows =
document.getElementById("studentTable")
.getElementsByTagName("tr");

for (let i = 1; i < rows.length; i++) {

rows[i].style.display =
rows[i].innerText
.toLowerCase()
.includes(text)
? ""
: "none";

}

}

</script>

"""

    return page(
        content,
        students=students,
        message=message
    )


# =========================================================
# TAKE ATTENDANCE
# =========================================================

@app.route(
    "/attendance",
    methods=["GET", "POST"]
)
def attendance_page():

    students = get_students()

    if request.method == "POST":

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

            return "Please fill all lecture details."

        try:

            lecture_number = int(
                lecture_number
            )

        except ValueError:

            return "Lecture number must be a number."

        lecture_id = add_lecture(
            lecture_date,
            lecture_number,
            subject,
            start_time,
            end_time
        )

        for student in students:

            status = request.form.get(
                "student_" +
                str(student["id"])
            )

            if status in [
                "Present",
                "Absent"
            ]:

                save_attendance(
                    student["id"],
                    lecture_id,
                    status
                )

        return redirect(
            url_for(
                "lecture_view",
                lecture_id=lecture_id
            )
        )

    content = """

<div class="card">

<h1>📋 Take Lecture Attendance</h1>

<form method="post">

<h3>Lecture Details</h3>


<label>
Lecture Date:
</label>

<input
type="date"
name="lecture_date"
value="{{ today }}"
required
>


<label>
Lecture Number:
</label>

<input
type="number"
name="lecture_number"
placeholder="Example: 1"
min="1"
required
>


<label>
Subject:
</label>

<input
type="text"
name="subject"
placeholder="Example: Data Structures"
required
>


<label>
Start Time:
</label>

<input
type="time"
name="start_time"
required
>


<label>
End Time:
</label>

<input
type="time"
name="end_time"
required
>


<h2>Student Attendance</h2>


<table>

<tr>

<th>Roll No.</th>

<th>Name</th>

<th>Status</th>

</tr>


{% for s in students %}

<tr>

<td>
<b>{{ s["roll_number"] }}</b>
</td>

<td>
{{ s["name"] }}
</td>

<td>


<label>

<input
type="radio"
name="student_{{ s['id'] }}"
value="Present"
required
>

🟢 Present

</label>


<label>

<input
type="radio"
name="student_{{ s['id'] }}"
value="Absent"
>

🔴 Absent

</label>


</td>

</tr>

{% endfor %}

</table>


<button
class="btn"
type="submit"
>
💾 Save Attendance
</button>


</form>

</div>

"""

    return page(
        content,
        students=students,
        today=date.today().isoformat()
    )


# =========================================================
# VIEW ONE LECTURE
# =========================================================

@app.route("/lecture/<int:lecture_id>")
def lecture_view(lecture_id):

    lecture = get_lecture(lecture_id)

    if lecture is None:

        return "Lecture not found."

    attendance = get_lecture_attendance(
        lecture_id
    )

    present = sum(
        1
        for s in attendance
        if s["status"] == "Present"
    )

    absent = sum(
        1
        for s in attendance
        if s["status"] == "Absent"
    )

    total = present + absent

    percentage = (
        round(
            present * 100 / total,
            1
        )
        if total
        else 0
    )

    content = """

<div class="card">

<h1>📚 Lecture Attendance</h1>


<h2>
{{ lecture["subject"] }}
</h2>


<p>
📅 Date:
<b>{{ lecture["lecture_date"] }}</b>
</p>


<p>
🔢 Lecture:
<b>{{ lecture["lecture_number"] }}</b>
</p>


<p>
🕐 Time:
<b>
{{ lecture["start_time"] }}
-
{{ lecture["end_time"] }}
</b>
</p>


<div class="stats">

<div class="stat">
<p>Present</p>
<h2>{{ present }}</h2>
</div>

<div class="stat">
<p>Absent</p>
<h2>{{ absent }}</h2>
</div>

<div class="stat">
<p>Total</p>
<h2>{{ total }}</h2>
</div>

<div class="stat">
<p>Attendance</p>
<h2>{{ percentage }}%</h2>
</div>

</div>


<table>

<tr>

<th>Roll No.</th>

<th>Name</th>

<th>Status</th>

</tr>


{% for s in attendance %}

<tr>

<td>
{{ s["roll_number"] }}
</td>

<td>
{{ s["name"] }}
</td>

<td>

{% if s["status"] == "Present" %}

<span class="good">
🟢 Present
</span>

{% elif s["status"] == "Absent" %}

<span class="danger">
🔴 Absent
</span>

{% else %}

⚪ Not Marked

{% endif %}

</td>

</tr>

{% endfor %}

</table>


<a
class="btn edit"
href="/edit/{{ lecture['id'] }}"
>
✏️ Edit Attendance
</a>


<a
class="btn"
href="/lectures"
>
← Back to Lectures
</a>

</div>

"""

    return page(
        content,
        lecture=lecture,
        attendance=attendance,
        present=present,
        absent=absent,
        total=total,
        percentage=percentage
    )


# =========================================================
# EDIT ATTENDANCE
# =========================================================

@app.route(
    "/edit/<int:lecture_id>",
    methods=["GET", "POST"]
)
def edit_attendance(lecture_id):

    lecture = get_lecture(lecture_id)

    if lecture is None:

        return "Lecture not found."

    students = get_lecture_attendance(
        lecture_id
    )

    if request.method == "POST":

        for student in students:

            status = request.form.get(
                "student_" +
                str(student["id"])
            )

            if status in [
                "Present",
                "Absent"
            ]:

                save_attendance(
                    student["id"],
                    lecture_id,
                    status
                )

        return redirect(
            url_for(
                "lecture_view",
                lecture_id=lecture_id
            )
        )

    content = """

<div class="card">

<h1>✏️ Edit Attendance</h1>


<h2>
{{ lecture["subject"] }}
</h2>


<p>
📅 {{ lecture["lecture_date"] }}
</p>


<p>
🔢 Lecture {{ lecture["lecture_number"] }}
</p>


<p>
🕐 {{ lecture["start_time"] }}
-
{{ lecture["end_time"] }}
</p>


<form method="post">

<table>

<tr>

<th>Roll No.</th>

<th>Name</th>

<th>Status</th>

</tr>


{% for s in students %}

<tr>

<td>
{{ s["roll_number"] }}
</td>

<td>
{{ s["name"] }}
</td>

<td>


<select
name="student_{{ s['id'] }}"
>

<option
value="Present"

{% if s["status"] == "Present" %}
selected
{% endif %}
>
🟢 Present
</option>


<option
value="Absent"

{% if s["status"] == "Absent" %}
selected
{% endif %}
>
🔴 Absent
</option>

</select>


</td>

</tr>

{% endfor %}

</table>


<button
class="btn"
type="submit"
>
💾 Save Changes
</button>


<a
class="btn"
href="/lecture/{{ lecture['id'] }}"
>
Cancel
</a>


</form>

</div>

"""

    return page(
        content,
        lecture=lecture,
        students=students
    )


# =========================================================
# LECTURE HISTORY
# =========================================================

@app.route("/lectures")
def lectures_page():

    lectures = get_lectures()

    content = """

<div class="card">

<h1>📚 Lecture History</h1>


{% if lectures %}

<table>

<tr>

<th>Date</th>

<th>Lecture</th>

<th>Subject</th>

<th>Time</th>

<th>Action</th>

</tr>


{% for l in lectures %}

<tr>

<td>
{{ l["lecture_date"] }}
</td>

<td>
{{ l["lecture_number"] }}
</td>

<td>
{{ l["subject"] }}
</td>

<td>
{{ l["start_time"] }}
-
{{ l["end_time"] }}
</td>

<td>


<a
class="btn"
href="/lecture/{{ l['id'] }}"
>
View
</a>


<a
class="btn edit"
href="/edit/{{ l['id'] }}"
>
Edit
</a>


</td>

</tr>

{% endfor %}

</table>

{% else %}

<div class="warning">

No lectures recorded yet.

</div>

{% endif %}

</div>

"""

    return page(
        content,
        lectures=lectures
    )


# =========================================================
# REPORTS
# =========================================================

@app.route("/reports")
def reports_page():

    reports = get_student_attendance()

    content = """

<div class="card">

<h1>📊 Attendance Reports</h1>


<p>
Students below <b>75%</b> are marked as
LOW attendance.
</p>


<table>

<tr>

<th>Roll No.</th>

<th>Name</th>

<th>Present</th>

<th>Total Lectures</th>

<th>Attendance</th>

</tr>


{% for r in reports %}

{% set total = r["total"] or 0 %}

{% set present = r["present"] or 0 %}


<tr>

<td>
{{ r["roll_number"] }}
</td>

<td>
{{ r["name"] }}
</td>

<td>
{{ present }}
</td>

<td>
{{ total }}
</td>

<td>


{% if total == 0 %}

No Data

{% else %}

{% set percent =
(present * 100 / total)|round(1)
%}


{% if percent < 75 %}

<span class="danger">
{{ percent }}% ⚠️ LOW
</span>

{% else %}

<span class="good">
{{ percent }}%
</span>

{% endif %}

{% endif %}


</td>

</tr>

{% endfor %}

</table>

</div>

"""

    return page(
        content,
        reports=reports
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )