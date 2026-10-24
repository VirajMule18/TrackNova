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
# MODERN DESIGN
# =========================================================

STYLE = """
<style>
:root{
    --primary:#4f46e5;
    --primary2:#2563eb;
    --dark:#172554;
    --text:#172033;
    --muted:#64748b;
    --card:rgba(255,255,255,.86);
    --border:#e2e8f0;
    --bg:#f5f7ff;
    --green:#16a34a;
    --red:#dc2626;
    --orange:#f59e0b;
}

*{box-sizing:border-box}

html{scroll-behavior:smooth}

body{
    margin:0;
    font-family:"Segoe UI",Arial,sans-serif;
    background:
      radial-gradient(circle at 10% 10%,rgba(99,102,241,.12),transparent 28%),
      radial-gradient(circle at 90% 20%,rgba(37,99,235,.10),transparent 28%),
      var(--bg);
    color:var(--text);
    min-height:100vh;
    transition:.3s;
}

body.dark{
    --text:#e5e7eb;
    --muted:#94a3b8;
    --card:rgba(30,41,59,.92);
    --border:#334155;
    --bg:#0f172a;
    background:
      radial-gradient(circle at 10% 10%,rgba(79,70,229,.18),transparent 28%),
      radial-gradient(circle at 90% 20%,rgba(37,99,235,.15),transparent 28%),
      #0f172a;
}

header{
    position:relative;
    overflow:hidden;
    background:linear-gradient(135deg,#172554,#3730a3,#2563eb);
    color:white;
    text-align:center;
    padding:58px 20px 52px;
    box-shadow:0 12px 35px rgba(37,99,235,.25);
}

header:before,header:after{
    content:"";
    position:absolute;
    width:220px;height:220px;
    border-radius:50%;
    background:rgba(255,255,255,.08);
    animation:float 7s ease-in-out infinite;
}
header:before{left:-70px;top:-80px}
header:after{right:-60px;bottom:-100px;animation-delay:2s}

header h1,header p{
    position:relative;
    z-index:2;
}
header h1{
    margin:0;
    font-size:46px;
    letter-spacing:2px;
    animation:fadeDown .8s ease;
}
header p{
    margin:12px 0 0;
    font-size:17px;
    opacity:.92;
    animation:fadeUp 1s ease;
}

.top-actions{
    position:absolute;
    top:18px;
    right:18px;
    z-index:5;
}

.theme-btn{
    border:1px solid rgba(255,255,255,.35);
    background:rgba(255,255,255,.14);
    color:white;
    padding:9px 13px;
    border-radius:12px;
    cursor:pointer;
    backdrop-filter:blur(8px);
}

nav{
    position:sticky;
    top:0;
    z-index:1000;
    background:rgba(255,255,255,.88);
    backdrop-filter:blur(14px);
    padding:12px;
    text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,.08);
}

.dark nav{
    background:rgba(15,23,42,.90);
}

nav a{
    display:inline-block;
    color:#263a8b;
    text-decoration:none;
    padding:11px 16px;
    margin:3px;
    border-radius:12px;
    font-weight:650;
    transition:.25s;
}
.dark nav a{color:#c7d2fe}

nav a:hover{
    color:white;
    background:linear-gradient(135deg,var(--primary),var(--primary2));
    transform:translateY(-3px);
    box-shadow:0 8px 20px rgba(37,99,235,.25);
}

main{
    max-width:1200px;
    margin:35px auto;
    padding:15px;
    animation:pageEnter .55s ease;
}

.card{
    background:var(--card);
    backdrop-filter:blur(12px);
    padding:28px;
    border-radius:22px;
    margin-bottom:24px;
    border:1px solid rgba(255,255,255,.55);
    box-shadow:0 10px 35px rgba(31,41,55,.08);
    transition:.3s;
}

.dark .card{border-color:#334155}

.card:hover{
    transform:translateY(-3px);
    box-shadow:0 16px 40px rgba(31,41,55,.14);
}

.card h1{margin-top:0;font-size:30px}
.card h2{color:#4f46e5}

.stats{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:18px;
    margin-bottom:24px;
}

.stat{
    position:relative;
    overflow:hidden;
    background:var(--card);
    padding:25px;
    text-align:center;
    border-radius:20px;
    box-shadow:0 8px 25px rgba(31,41,55,.08);
    transition:.3s;
    animation:cardEnter .7s ease both;
}

.stat:nth-child(2){animation-delay:.1s}
.stat:nth-child(3){animation-delay:.2s}
.stat:nth-child(4){animation-delay:.3s}

.stat:before{
    content:"";
    position:absolute;
    left:0;top:0;width:100%;height:4px;
    background:linear-gradient(90deg,var(--primary),var(--primary2));
}

.stat:hover{
    transform:translateY(-8px) scale(1.02);
    box-shadow:0 18px 35px rgba(37,99,235,.16);
}

.stat p{color:var(--muted);font-weight:650}
.stat h2{
    font-size:38px;
    margin:10px;
    color:#2563eb;
}

.progress{
    height:12px;
    background:#e2e8f0;
    border-radius:20px;
    overflow:hidden;
    margin:12px 0;
}
.dark .progress{background:#334155}

.progress-bar{
    height:100%;
    border-radius:20px;
    background:linear-gradient(90deg,#4f46e5,#06b6d4);
    width:0;
    animation:growBar 1.4s ease forwards;
}

.quick-grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:15px;
}

.quick{
    padding:22px;
    border-radius:18px;
    text-decoration:none;
    color:var(--text);
    background:var(--card);
    border:1px solid var(--border);
    transition:.25s;
}
.quick:hover{
    transform:translateY(-6px);
    border-color:#6366f1;
    box-shadow:0 12px 28px rgba(79,70,229,.15);
}
.quick-icon{font-size:30px}
.quick strong{display:block;margin-top:10px}

table{
    width:100%;
    border-collapse:separate;
    border-spacing:0 8px;
    margin-top:18px;
}

th{
    background:linear-gradient(135deg,#1e3a8a,#2563eb);
    color:white;
    padding:15px;
    text-align:left;
}
th:first-child{border-radius:10px 0 0 10px}
th:last-child{border-radius:0 10px 10px 0}

td{
    padding:15px;
    background:var(--card);
    border-bottom:1px solid var(--border);
}
tr{transition:.25s}
tr:hover td{background:rgba(99,102,241,.08)}
td:first-child{border-radius:10px 0 0 10px}
td:last-child{border-radius:0 10px 10px 0}

input,select{
    padding:13px 15px;
    margin:5px;
    border:2px solid var(--border);
    border-radius:11px;
    outline:none;
    background:var(--card);
    color:var(--text);
    transition:.25s;
    font-size:14px;
}
input:focus,select:focus{
    border-color:#4f46e5;
    box-shadow:0 0 0 4px rgba(79,70,229,.10);
}

.btn{
    display:inline-block;
    background:linear-gradient(135deg,#4f46e5,#2563eb);
    color:white;
    border:none;
    padding:12px 19px;
    margin:5px;
    border-radius:11px;
    cursor:pointer;
    text-decoration:none;
    font-weight:650;
    transition:.25s;
    box-shadow:0 5px 15px rgba(37,99,235,.20);
}
.btn:hover{
    transform:translateY(-3px);
    box-shadow:0 10px 22px rgba(37,99,235,.30);
}
.btn:active{transform:scale(.96)}
.delete{background:linear-gradient(135deg,#ef4444,#dc2626)}
.edit{background:linear-gradient(135deg,#f59e0b,#d97706)}

.good{color:#16a34a;font-weight:700}
.danger{color:#dc2626;font-weight:700}

.success{
    background:linear-gradient(135deg,#dcfce7,#f0fdf4);
    color:#166534;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #22c55e;
    animation:fadeUp .5s ease;
}

.warning{
    background:linear-gradient(135deg,#fef3c7,#fffbeb);
    color:#92400e;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #f59e0b;
    animation:fadeUp .5s ease;
}

.search{
    width:90%;
    max-width:450px;
    padding:14px 18px;
    border-radius:14px;
}

.badge{
    display:inline-block;
    padding:7px 11px;
    border-radius:999px;
    font-size:13px;
    font-weight:700;
}
.badge-good{background:#dcfce7;color:#166534}
.badge-low{background:#fee2e2;color:#991b1b}

.empty{
    text-align:center;
    padding:30px;
    color:var(--muted);
}

footer{
    text-align:center;
    padding:30px;
    color:var(--muted);
}

@keyframes fadeDown{
    from{opacity:0;transform:translateY(-25px)}
    to{opacity:1;transform:translateY(0)}
}
@keyframes fadeUp{
    from{opacity:0;transform:translateY(25px)}
    to{opacity:1;transform:translateY(0)}
}
@keyframes pageEnter{
    from{opacity:0;transform:translateY(15px)}
    to{opacity:1;transform:translateY(0)}
}
@keyframes cardEnter{
    from{opacity:0;transform:translateY(25px) scale(.97)}
    to{opacity:1;transform:translateY(0) scale(1)}
}
@keyframes float{
    0%,100%{transform:translateY(0) rotate(0)}
    50%{transform:translateY(-25px) rotate(8deg)}
}
@keyframes growBar{
    from{width:0}
    to{width:var(--width)}
}

@media(max-width:800px){
    header h1{font-size:34px}
    .stats{grid-template-columns:repeat(2,1fr)}
    .quick-grid{grid-template-columns:repeat(2,1fr)}
    table{display:block;overflow-x:auto}
}

@media(max-width:500px){
    .stats,.quick-grid{grid-template-columns:1fr}
    header{padding:45px 15px}
    header h1{font-size:28px}
    main{padding:10px}
    .card{padding:20px}
    nav a{font-size:12px;padding:8px 9px}
}
</style>
"""

# =========================================================
# COMMON PAGE
# =========================================================

PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TrackNova | Smart Attendance</title>
""" + STYLE + """
</head>

<body>

<header>
    <div class="top-actions">
        <button class="theme-btn" onclick="toggleTheme()">🌙 Theme</button>
    </div>

    <h1>✦ TRACK NOVA</h1>
    <p>Smart Student Attendance Management System</p>
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

<footer>
    <b>TRACK NOVA</b> • Smart Attendance Management System
</footer>

<script>
function toggleTheme(){
    document.body.classList.toggle("dark");
    localStorage.setItem(
        "tracknova-theme",
        document.body.classList.contains("dark") ? "dark" : "light"
    );
}

if(localStorage.getItem("tracknova-theme") === "dark"){
    document.body.classList.add("dark");
}

function animateCounters(){
    document.querySelectorAll(".counter").forEach(function(el){
        let target = parseFloat(el.dataset.target || "0");
        let decimals = String(target).includes(".") ? 1 : 0;
        let start = 0;
        let duration = 900;
        let startTime = null;

        function step(timestamp){
            if(!startTime) startTime = timestamp;
            let progress = Math.min((timestamp-startTime)/duration,1);
            let value = start + (target-start)*progress;
            el.textContent = value.toFixed(decimals);
            if(progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    });
}

document.addEventListener("DOMContentLoaded", animateCounters);
</script>

</body>
</html>
"""

def page(content, **context):
    return render_template_string(
        PAGE,
        content=render_template_string(content, **context)
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
        if marked else 0
    )

    reports = get_student_attendance()
    low_students = []

    for student in reports:
        total_lectures = student["total"] or 0
        present_lectures = student["present"] or 0

        if total_lectures > 0:
            percent = round(
                present_lectures * 100 / total_lectures, 1
            )

            if percent < 75:
                low_students.append({
                    "roll": student["roll_number"],
                    "name": student["name"],
                    "percentage": percent
                })

    content = """
    <div class="card">
        <h1>Welcome to TrackNova 👋</h1>
        <p>Manage students, lectures and attendance from one place.</p>
        <p>📅 Today's Date: <b>{{ today }}</b></p>
    </div>

    <div class="stats">

        <div class="stat">
            <p>👨‍🎓 Total Students</p>
            <h2><span class="counter" data-target="{{ total }}">0</span></h2>
        </div>

        <div class="stat">
            <p>🟢 Present Today</p>
            <h2><span class="counter" data-target="{{ present }}">0</span></h2>
        </div>

        <div class="stat">
            <p>🔴 Absent Today</p>
            <h2><span class="counter" data-target="{{ absent }}">0</span></h2>
        </div>

        <div class="stat">
            <p>📈 Today's Attendance</p>
            <h2><span class="counter" data-target="{{ percentage }}">0</span>%</h2>
        </div>

    </div>

    <div class="card">
        <h2>📊 Today's Attendance</h2>
        <div class="progress">
            <div class="progress-bar"
                 style="--width: {{ percentage }}%;"></div>
        </div>
        <p><b>{{ percentage }}%</b> attendance recorded today.</p>
    </div>

    <div class="card">
        <h2>⚠️ Low Attendance Warning</h2>
        <p>Students below <b>75%</b> attendance:</p>

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
                <td class="danger">{{ s.percentage }}% ⚠️</td>
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

        <div class="quick-grid">

            <a class="quick" href="/attendance">
                <span class="quick-icon">📋</span>
                <strong>Take Attendance</strong>
                <small>Mark today's lecture</small>
            </a>

            <a class="quick" href="/students">
                <span class="quick-icon">👨‍🎓</span>
                <strong>Students</strong>
                <small>Manage student records</small>
            </a>

            <a class="quick" href="/lectures">
                <span class="quick-icon">📚</span>
                <strong>Lectures</strong>
                <small>View lecture history</small>
            </a>

            <a class="quick" href="/reports">
                <span class="quick-icon">📊</span>
                <strong>Reports</strong>
                <small>View attendance reports</small>
            </a>

        </div>
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

            roll = request.form.get("roll", "").strip()
            name = request.form.get("name", "").strip()

            if roll and name:
                try:
                    add_student(roll, name)
                    message = "Student added successfully!"
                except sqlite3.IntegrityError:
                    message = "This roll number already exists."
            else:
                message = "Please enter roll number and name."

        elif action == "delete":

            student_id = request.form.get("student_id")

            try:
                delete_student(student_id)
                message = "Student deleted successfully."
            except sqlite3.Error:
                message = "Could not delete student."

    students = get_students()

    content = """
    <div class="card">

        <h1>👨‍🎓 Manage Students</h1>

        {% if message %}
        <div class="success">{{ message }}</div>
        {% endif %}

        <h3>➕ Add New Student</h3>

        <form method="post">

            <input type="hidden"
                   name="action"
                   value="add">

            <input type="number"
                   name="roll"
                   placeholder="Roll Number"
                   required>

            <input name="name"
                   placeholder="Student Full Name"
                   required>

            <button class="btn" type="submit">
                + Add Student
            </button>

        </form>

        <p>
            Total Students:
            <b>{{ students|length }}</b>
        </p>

        <input class="search"
               id="search"
               placeholder="🔍 Search student"
               onkeyup="searchStudent()">

        {% if students %}

        <table id="studentTable">

            <tr>
                <th>Roll No.</th>
                <th>Name</th>
                <th>Action</th>
            </tr>

            {% for s in students %}

            <tr>
                <td><b>{{ s["roll_number"] }}</b></td>

                <td>{{ s["name"] }}</td>

                <td>
                    <form method="post"
                          onsubmit="return confirm('Delete this student?');">

                        <input type="hidden"
                               name="action"
                               value="delete">

                        <input type="hidden"
                               name="student_id"
                               value="{{ s['id'] }}">

                        <button class="btn delete"
                                type="submit">
                            🗑 Delete
                        </button>

                    </form>
                </td>
            </tr>

            {% endfor %}

        </table>

        {% else %}

        <div class="empty">
            👨‍🎓 No students added yet.
        </div>

        {% endif %}

    </div>

    <script>
    function searchStudent(){

        let text = document
            .getElementById("search")
            .value
            .toLowerCase();

        let rows = document
            .getElementById("studentTable")
            .getElementsByTagName("tr");

        for(let i=1;i<rows.length;i++){

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

@app.route("/attendance", methods=["GET", "POST"])
def attendance_page():

    students = get_students()

    if request.method == "POST":

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
            return "Please fill all lecture details."

        try:
            lecture_number = int(lecture_number)
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
                "student_" + str(student["id"])
            )

            if status in ["Present", "Absent"]:
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

            <h3>📚 Lecture Details</h3>

            <input type="date"
                   name="lecture_date"
                   value="{{ today }}"
                   required>

            <input type="number"
                   name="lecture_number"
                   placeholder="Lecture Number"
                   min="1"
                   required>

            <input type="text"
                   name="subject"
                   placeholder="Subject"
                   required>

            <input type="time"
                   name="start_time"
                   required>

            <input type="time"
                   name="end_time"
                   required>

            <h2>👨‍🎓 Student Attendance</h2>

            {% if students %}

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

                    <td>{{ s["name"] }}</td>

                    <td>

                        <label>
                            <input type="radio"
                                   name="student_{{ s['id'] }}"
                                   value="Present"
                                   required>
                            🟢 Present
                        </label>

                        <label>
                            <input type="radio"
                                   name="student_{{ s['id'] }}"
                                   value="Absent">
                            🔴 Absent
                        </label>

                    </td>

                </tr>

                {% endfor %}

            </table>

            <button class="btn" type="submit">
                💾 Save Attendance
            </button>

            {% else %}

            <div class="warning">
                ⚠️ Add students first before taking attendance.
            </div>

            <a class="btn" href="/students">
                👨‍🎓 Add Students
            </a>

            {% endif %}

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

    attendance = get_lecture_attendance(lecture_id)

    present = sum(
        1 for s in attendance
        if s["status"] == "Present"
    )

    absent = sum(
        1 for s in attendance
        if s["status"] == "Absent"
    )

    total = present + absent

    percentage = (
        round(present * 100 / total, 1)
        if total else 0
    )

    content = """
    <div class="card">

        <h1>📚 Lecture Attendance</h1>

        <h2>{{ lecture["subject"] }}</h2>

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
            <b>{{ lecture["start_time"] }}
            -
            {{ lecture["end_time"] }}</b>
        </p>

        <div class="stats">

            <div class="stat">
                <p>🟢 Present</p>
                <h2>{{ present }}</h2>
            </div>

            <div class="stat">
                <p>🔴 Absent</p>
                <h2>{{ absent }}</h2>
            </div>

            <div class="stat">
                <p>👥 Total</p>
                <h2>{{ total }}</h2>
            </div>

            <div class="stat">
                <p>📈 Attendance</p>
                <h2>{{ percentage }}%</h2>
            </div>

        </div>

        <div class="progress">
            <div class="progress-bar"
                 style="--width: {{ percentage }}%;">
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

                <td>{{ s["roll_number"] }}</td>

                <td>{{ s["name"] }}</td>

                <td>

                    {% if s["status"] == "Present" %}

                    <span class="badge badge-good">
                        🟢 Present
                    </span>

                    {% elif s["status"] == "Absent" %}

                    <span class="badge badge-low">
                        🔴 Absent
                    </span>

                    {% else %}

                    ⚪ Not Marked

                    {% endif %}

                </td>

            </tr>

            {% endfor %}

        </table>

        <a class="btn edit"
           href="/edit/{{ lecture['id'] }}">
            ✏️ Edit Attendance
        </a>

        <a class="btn"
           href="/lectures">
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

@app.route("/edit/<int:lecture_id>", methods=["GET", "POST"])
def edit_attendance(lecture_id):

    lecture = get_lecture(lecture_id)

    if lecture is None:
        return "Lecture not found."

    students = get_lecture_attendance(lecture_id)

    if request.method == "POST":

        for student in students:

            status = request.form.get(
                "student_" + str(student["id"])
            )

            if status in ["Present", "Absent"]:

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

        <h2>{{ lecture["subject"] }}</h2>

        <p>📅 {{ lecture["lecture_date"] }}</p>

        <p>🔢 Lecture {{ lecture["lecture_number"] }}</p>

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

                    <td>{{ s["roll_number"] }}</td>

                    <td>{{ s["name"] }}</td>

                    <td>

                        <select name="student_{{ s['id'] }}">

                            <option value="Present"
                            {% if s["status"] == "Present" %}
                            selected
                            {% endif %}>
                            🟢 Present
                            </option>

                            <option value="Absent"
                            {% if s["status"] == "Absent" %}
                            selected
                            {% endif %}>
                            🔴 Absent
                            </option>

                        </select>

                    </td>

                </tr>

                {% endfor %}

            </table>

            <button class="btn" type="submit">
                💾 Save Changes
            </button>

            <a class="btn"
               href="/lecture/{{ lecture['id'] }}">
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

                <td>{{ l["lecture_date"] }}</td>

                <td>{{ l["lecture_number"] }}</td>

                <td><b>{{ l["subject"] }}</b></td>

                <td>
                    {{ l["start_time"] }}
                    -
                    {{ l["end_time"] }}
                </td>

                <td>

                    <a class="btn"
                       href="/lecture/{{ l['id'] }}">
                        👁 View
                    </a>

                    <a class="btn edit"
                       href="/edit/{{ l['id'] }}">
                        ✏️ Edit
                    </a>

                </td>

            </tr>

            {% endfor %}

        </table>

        {% else %}

        <div class="warning">
            📚 No lectures recorded yet.
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
            <b>LOW attendance</b>.
        </p>

        {% if reports %}

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

                <td>{{ r["roll_number"] }}</td>

                <td><b>{{ r["name"] }}</b></td>

                <td>{{ present }}</td>

                <td>{{ total }}</td>

                <td>

                    {% if total == 0 %}

                        <span class="badge">
                            No Data
                        </span>

                    {% else %}

                        {% set percent =
                            (present * 100 / total)|round(1)
                        %}

                        <div style="min-width:150px">

                            <div class="progress">
                                <div class="progress-bar"
                                     style="--width: {{ percent }}%;">
                                </div>
                            </div>

                            {% if percent < 75 %}

                            <span class="badge badge-low">
                                {{ percent }}% ⚠️ LOW
                            </span>

                            {% else %}

                            <span class="badge badge-good">
                                {{ percent }}% ✓ Good
                            </span>

                            {% endif %}

                        </div>

                    {% endif %}

                </td>

            </tr>

            {% endfor %}

        </table>

        {% else %}

        <div class="empty">
            📊 No attendance reports available yet.
        </div>

        {% endif %}

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
        host="0.0.0.0",
        port=5000,
        debug=True
    )
