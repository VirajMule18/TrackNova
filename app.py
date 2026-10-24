from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from functools import wraps
from datetime import date

import database


app = Flask(__name__)

app.secret_key = "TRACKNOVA_SECRET_KEY_2026"


# =========================================================
# DESIGN
# =========================================================

CSS = """
<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

body {
    background:
        radial-gradient(circle at 20% 20%, rgba(0,255,140,.12), transparent 25%),
        radial-gradient(circle at 80% 80%, rgba(0,255,140,.08), transparent 25%),
        #050807;
    color: white;
    min-height: 100vh;
}

/* Animated diamond background */

body::before {
    content: "";
    position: fixed;
    width: 350px;
    height: 350px;
    border: 2px solid rgba(0,255,140,.25);
    transform: rotate(45deg);
    top: -150px;
    left: -100px;
    animation: diamond 8s infinite linear;
    pointer-events: none;
}

body::after {
    content: "";
    position: fixed;
    width: 250px;
    height: 250px;
    border: 2px solid rgba(0,255,140,.18);
    transform: rotate(45deg);
    right: -100px;
    bottom: -100px;
    animation: diamond 10s infinite linear reverse;
    pointer-events: none;
}

@keyframes diamond {

    0% {
        transform: rotate(45deg) scale(1);
    }

    50% {
        transform: rotate(225deg) scale(1.15);
    }

    100% {
        transform: rotate(405deg) scale(1);
    }
}

.navbar {
    width: 100%;
    padding: 18px 7%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(5,8,7,.85);
    border-bottom: 1px solid rgba(0,255,140,.25);
    position: sticky;
    top: 0;
    z-index: 10;
    backdrop-filter: blur(12px);
}

.logo {
    color: #00ff88;
    font-size: 25px;
    font-weight: bold;
}

.nav-links {
    display: flex;
    gap: 10px;
    align-items: center;
}

.nav-links a {
    color: white;
    text-decoration: none;
    padding: 9px 14px;
    border-radius: 10px;
    transition: .3s;
}

.nav-links a:hover {
    background: #00ff88;
    color: #001a0d;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 35px auto;
}

.hero {
    text-align: center;
    padding: 55px 20px;
}

.hero h1 {
    font-size: 55px;
    color: #00ff88;
    text-shadow: 0 0 25px rgba(0,255,136,.4);
}

.hero p {
    margin-top: 12px;
    color: #aaa;
    font-size: 18px;
}

.card {
    background: rgba(12,18,15,.88);
    border: 1px solid rgba(0,255,140,.2);
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,.35);
    animation: fadeUp .6s ease;
}

@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(15px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.card h2 {
    color: #00ff88;
    margin-bottom: 18px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 18px;
}

.stat {
    background: #0b120f;
    padding: 25px;
    border-radius: 16px;
    border: 1px solid rgba(0,255,140,.2);
    text-align: center;
    transition: .3s;
}

.stat:hover {
    transform: translateY(-6px);
    border-color: #00ff88;
    box-shadow: 0 0 25px rgba(0,255,136,.12);
}

.stat h3 {
    color: #00ff88;
    font-size: 35px;
}

.stat p {
    color: #aaa;
    margin-top: 5px;
}

form {
    display: grid;
    gap: 12px;
}

input,
select {
    width: 100%;
    padding: 13px;
    border-radius: 10px;
    border: 1px solid #244c38;
    background: #07100b;
    color: white;
    outline: none;
}

input:focus,
select:focus {
    border-color: #00ff88;
    box-shadow: 0 0 10px rgba(0,255,136,.12);
}

button,
.btn {
    display: inline-block;
    padding: 12px 18px;
    background: #00ff88;
    color: #001a0d;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;
    transition: .3s;
}

button:hover,
.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0,255,136,.3);
}

.btn-danger {
    background: #ff4040;
    color: white;
}

.btn-dark {
    background: #18231d;
    color: white;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 14px;
    border-bottom: 1px solid #1d3026;
    text-align: left;
}

th {
    color: #00ff88;
}

tr:hover {
    background: rgba(0,255,136,.04);
}

.badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
}

.present {
    background: rgba(0,255,136,.15);
    color: #00ff88;
}

.absent {
    background: rgba(255,60,60,.15);
    color: #ff5555;
}

.login-box {
    width: 420px;
    max-width: 92%;
    margin: 80px auto;
}

.login-logo {
    text-align: center;
    margin-bottom: 30px;
}

.login-logo h1 {
    color: #00ff88;
    font-size: 42px;
}

.alert {
    padding: 13px;
    border-radius: 10px;
    background: rgba(255,60,60,.12);
    border: 1px solid #ff4444;
    color: #ff7777;
    margin-bottom: 15px;
}

.success {
    background: rgba(0,255,136,.1);
    border-color: #00ff88;
    color: #00ff88;
}

.actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.empty {
    text-align: center;
    padding: 30px;
    color: #888;
}

.footer {
    text-align: center;
    color: #666;
    padding: 30px;
}

@media(max-width:800px) {

    .stats {
        grid-template-columns: repeat(2,1fr);
    }

    .hero h1 {
        font-size: 40px;
    }

    .navbar {
        flex-direction: column;
        gap: 12px;
    }

}

@media(max-width:500px) {

    .stats {
        grid-template-columns: 1fr;
    }

    table {
        font-size: 13px;
    }

    th,
    td {
        padding: 8px;
    }

}

</style>
"""


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(role=None):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                return redirect(url_for("login"))

            if role and session.get("role") != role:
                return redirect(url_for("dashboard"))

            return function(*args, **kwargs)

        return wrapper

    return decorator


# =========================================================
# NAVBAR
# =========================================================

def navbar():

    if "user_id" not in session:
        return ""

    return f"""
    <div class="navbar">

        <div class="logo">
            ◆ TrackNova
        </div>

        <div class="nav-links">

            <a href="{url_for('dashboard')}">
                Dashboard
            </a>

            {"<a href='" + url_for("students") + "'>Students</a>" if session.get("role") == "teacher" else ""}

            {"<a href='" + url_for("lectures") + "'>Lectures</a>" if session.get("role") == "teacher" else ""}

            <a href="{url_for('attendance_report')}">
                Attendance
            </a>

            <a href="{url_for('logout')}">
                Logout
            </a>

        </div>

    </div>
    """


# =========================================================
# LOGIN
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = database.login_user(username, password)

        if user:

            session.clear()

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Wrong username or password.")

    return render_template_string(f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>TrackNova Login</title>

        {CSS}

    </head>

    <body>

        <div class="login-box">

            <div class="login-logo">

                <h1>◆ TrackNova</h1>

                <p style="color:#888;">
                    Smart Attendance Management System
                </p>

            </div>

            <div class="card">

                <h2>Login</h2>

                {{% with messages = get_flashed_messages() %}}

                    {{% for message in messages %}}

                        <div class="alert">
                            {{{{ message }}}}
                        </div>

                    {{% endfor %}}

                {{% endwith %}}

                <form method="POST">

                    <input
                        type="text"
                        name="username"
                        placeholder="Username"
                        required
                    >

                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        required
                    >

                    <button type="submit">
                        Login
                    </button>

                </form>

                <div style="margin-top:20px;color:#777;font-size:13px;">

                    <b>Teacher:</b> teacher / teacher123<br>

                    <b>Student:</b> student / student123

                </div>

            </div>

        </div>

    </body>

    </html>

    """)


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required()
def dashboard():

    stats = database.get_dashboard_stats()

    role = session.get("role")

    return render_template_string(f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>TrackNova Dashboard</title>

        {CSS}

    </head>

    <body>

        {navbar()}

        <div class="container">

            <div class="hero">

                <h1>TrackNova</h1>

                <p>
                    Smart Attendance Management System
                </p>

                <p style="color:#00ff88;margin-top:15px;">
                    Welcome, {session.get("username")} 👋
                </p>

            </div>

            <div class="stats">

                <div class="stat">

                    <h3>
                        {stats["students"]}
                    </h3>

                    <p>
                        Students
                    </p>

                </div>

                <div class="stat">

                    <h3>
                        {stats["lectures"]}
                    </h3>

                    <p>
                        Lectures
                    </p>

                </div>

                <div class="stat">

                    <h3>
                        {stats["present"]}
                    </h3>

                    <p>
                        Present
                    </p>

                </div>

                <div class="stat">

                    <h3>
                        {stats["absent"]}
                    </h3>

                    <p>
                        Absent
                    </p>

                </div>

            </div>

            <br>

            {"<div class='card'><h2>Teacher Control Panel</h2><div class='actions'><a class='btn' href='" + url_for("students") + "'>👥 Manage Students</a><a class='btn' href='" + url_for("lectures") + "'>📝 Manage Lectures</a><a class='btn' href='" + url_for("attendance_report") + "'>📊 Attendance Report</a></div></div>" if role == "teacher" else ""}

            {"<div class='card'><h2>Student Panel</h2><p style='color:#aaa;'>You have view-only access. You can see your attendance records but cannot modify attendance.</p><br><a class='btn' href='" + url_for("attendance_report") + "'>👀 View Attendance</a></div>" if role == "student" else ""}

        </div>

        <div class="footer">
            TrackNova © 2026
        </div>

    </body>

    </html>

    """)


# =========================================================
# STUDENTS
# =========================================================

@app.route("/students", methods=["GET", "POST"])
@login_required("teacher")
def students():

    if request.method == "POST":

        action = request.form.get("action")

        try:

            if action == "add":

                roll = request.form.get("roll")
                name = request.form.get("name")

                if roll and name:

                    database.add_student(roll, name)

                    flash("Student added successfully.")

            elif action == "delete":

                student_id = request.form.get("student_id")

                database.delete_student(student_id)

                flash("Student deleted.")

        except Exception as e:

            flash("Error: " + str(e))

        return redirect(url_for("students"))

    students_list = database.get_students()

    return render_template_string(f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>Students - TrackNova</title>

        {CSS}

    </head>

    <body>

        {navbar()}

        <div class="container">

            <div class="card">

                <h2>👥 Add Student</h2>

                {{% with messages = get_flashed_messages() %}}

                    {{% for message in messages %}}

                        <div class="alert success">
                            {{{{ message }}}}
                        </div>

                    {{% endfor %}}

                {{% endwith %}}

                <form method="POST">

                    <input type="hidden" name="action" value="add">

                    <input
                        type="number"
                        name="roll"
                        placeholder="Roll Number"
                        required
                    >

                    <input
                        type="text"
                        name="name"
                        placeholder="Student Name"
                        required
                    >

                    <button type="submit">
                        + Add Student
                    </button>

                </form>

            </div>

            <div class="card">

                <h2>Student List</h2>

                <table>

                    <tr>
                        <th>Roll No.</th>
                        <th>Name</th>
                        <th>Action</th>
                    </tr>

                    {"".join(f'''

                    <tr>

                        <td>{s["roll_number"]}</td>

                        <td>{s["name"]}</td>

                        <td>

                            <form method="POST">

                                <input
                                    type="hidden"
                                    name="action"
                                    value="delete"
                                >

                                <input
                                    type="hidden"
                                    name="student_id"
                                    value="{s["id"]}"
                                >

                                <button
                                    class="btn-danger"
                                    type="submit"
                                >
                                    Delete
                                </button>

                            </form>

                        </td>

                    </tr>

                    ''' for s in students_list) if students_list else "<tr><td colspan='3' class='empty'>No students added.</td></tr>"}

                </table>

            </div>

        </div>

    </body>

    </html>

    """)


# =========================================================
# LECTURES
# =========================================================

@app.route("/lectures", methods=["GET", "POST"])
@login_required("teacher")
def lectures():

    if request.method == "POST":

        try:

            database.add_lecture(
                request.form.get("lecture_date"),
                request.form.get("lecture_number"),
                request.form.get("subject"),
                request.form.get("start_time"),
                request.form.get("end_time")
            )

            flash("Lecture created successfully.")

        except Exception as e:

            flash("Error: " + str(e))

        return redirect(url_for("lectures"))

    lecture_list = database.get_lectures()

    return render_template_string(f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>Lectures - TrackNova</title>

        {CSS}

    </head>

    <body>

        {navbar()}

        <div class="container">

            <div class="card">

                <h2>📝 Create Lecture</h2>

                <form method="POST">

                    <input
                        type="date"
                        name="lecture_date"
                        value="{date.today()}"
                        required
                    >

                    <input
                        type="number"
                        name="lecture_number"
                        placeholder="Lecture Number"
                        min="1"
                        required
                    >

                    <input
                        type="text"
                        name="subject"
                        placeholder="Subject"
                        required
                    >

                    <input
                        type="time"
                        name="start_time"
                        required
                    >

                    <input
                        type="time"
                        name="end_time"
                        required
                    >

                    <button type="submit">
                        + Create Lecture
                    </button>

                </form>

            </div>

            <div class="card">

                <h2>Lectures</h2>

                <table>

                    <tr>
                        <th>Date</th>
                        <th>Lecture</th>
                        <th>Subject</th>
                        <th>Time</th>
                        <th>Action</th>
                    </tr>

                    {"".join(f'''

                    <tr>

                        <td>{l["lecture_date"]}</td>

                        <td>{l["lecture_number"]}</td>

                        <td>{l["subject"]}</td>

                        <td>
                            {l["start_time"]} -
                            {l["end_time"]}
                        </td>

                        <td>

                            <a
                                class="btn"
                                href="{url_for("take_attendance", lecture_id=l["id"])}"
                            >
                                Take Attendance
                            </a>

                        </td>

                    </tr>

                    ''' for l in lecture_list) if lecture_list else "<tr><td colspan='5' class='empty'>No lectures created.</td></tr>"}

                </table>

            </div>

        </div>

    </body>

    </html>

    """)


# =========================================================
# TAKE ATTENDANCE
# =========================================================

@app.route("/attendance/<int:lecture_id>", methods=["GET", "POST"])
@login_required("teacher")
def take_attendance(lecture_id):

    lecture = database.get_lecture(lecture_id)

    if not lecture:
        return "Lecture not found", 404

    students_list = database.get_lecture_attendance(lecture_id)

    if request.method == "POST":

        for student in students_list:

            status = request.form.get(
                f"status_{student['id']}"
            )

            if status not in ["Present", "Absent"]:
                status = "Absent"

            database.save_attendance(
                student["id"],
                lecture_id,
                status
            )

        flash("Attendance saved successfully.")

        return redirect(
            url_for(
                "take_attendance",
                lecture_id=lecture_id
            )
        )

    return render_template_string(f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>Take Attendance - TrackNova</title>

        {CSS}

    </head>

    <body>

        {navbar()}

        <div class="container">

            <div class="card">

                <h2>
                    📋 {lecture["subject"]}
                </h2>

                <p style="color:#aaa;">

                    Date: {lecture["lecture_date"]}
                    |
                    Lecture: {lecture["lecture_number"]}
                    |
                    {lecture["start_time"]} -
                    {lecture["end_time"]}

                </p>

            </div>

            {{% with messages = get_flashed_messages() %}}

                {{% for message in messages %}}

                    <div class="alert success">
                        {{{{ message }}}}
                    </div>

                {{% endfor %}}

            {{% endwith %}}

            <div class="card">

                <form method="POST">

                    <table>

                        <tr>

                            <th>Roll</th>

                            <th>Name</th>

                            <th>Status</th>

                        </tr>

                        {"".join(f'''

                        <tr>

                            <td>
                                {s["roll_number"]}
                            </td>

                            <td>
                                {s["name"]}
                            </td>

                            <td>

                                <select
                                    name="status_{s["id"]}"
                                >

                                    <option
                                        value="Present"
                                        {"selected" if s["status"] == "Present" else ""}
                                    >
                                        Present
                                    </option>

                                    <option
                                        value="Absent"
                                        {"selected" if s["status"] == "Absent" else ""}
                                    >
                                        Absent
                                    </option>

                                </select>

                            </td>

                        </tr>

                        ''' for s in students_list)}

                    </table>

                    <br>

                    <button type="submit">
                        ✓ Save Attendance
                    </button>

                </form>

            </div>

        </div>

    </body>

    </html>

    """)


# =========================================================
# ATTENDANCE REPORT
# =========================================================

@app.route("/attendance")
@login_required()
def attendance_report():

    report = database.get_student_attendance()

    return render_template_string(f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>Attendance - TrackNova</title>

        {CSS}

    </head>

    <body>

        {navbar()}

        <div class="container">

            <div class="card">

                <h2>📊 Attendance Report</h2>

                <table>

                    <tr>

                        <th>Roll No.</th>

                        <th>Name</th>

                        <th>Total Lectures</th>

                        <th>Present</th>

                        <th>Percentage</th>

                    </tr>

                    {"".join(f'''

                    <tr>

                        <td>
                            {s["roll_number"]}
                        </td>

                        <td>
                            {s["name"]}
                        </td>

                        <td>
                            {s["total"]}
                        </td>

                        <td>
                            {s["present"]}
                        </td>

                        <td>

                            {
                                round(
                                    (s["present"] / s["total"]) * 100,
                                    1
                                )
                                if s["total"] else 0
                            }%

                        </td>

                    </tr>

                    ''' for s in report) if report else "<tr><td colspan='5' class='empty'>No attendance data available.</td></tr>"}

                </table>

            </div>

        </div>

    </body>

    </html>

    """)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
