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

CSS = r"""
<style>
*{box-sizing:border-box}
:root{
--p:#6366f1;--p2:#2563eb;--green:#16a34a;--red:#dc2626;
--orange:#f59e0b;--bg:#f5f7ff;--card:#fff;--text:#172033;
--muted:#64748b;--border:#e2e8f0
}
*{scroll-behavior:smooth}
body{
margin:0;font-family:Segoe UI,Arial,sans-serif;color:var(--text);
background:radial-gradient(circle at 10% 10%,#e0e7ff,transparent 30%),var(--bg);
min-height:100vh
}
header{
position:relative;overflow:hidden;text-align:center;color:#fff;
padding:50px 20px;background:linear-gradient(135deg,#172554,#4f46e5,#2563eb);
box-shadow:0 10px 30px #2563eb33
}
header:before,header:after{
content:"";position:absolute;width:180px;height:180px;border-radius:50%;
background:#ffffff18;animation:float 6s ease-in-out infinite
}
header:before{left:-60px;top:-90px}
header:after{right:-60px;bottom:-90px;animation-delay:2s}
.header-content{position:relative;z-index:2}
header h1{margin:0;font-size:46px;letter-spacing:2px;animation:down .7s}
header p{margin:10px 0 0;font-size:17px;animation:up .9s}
nav{
position:sticky;top:0;z-index:10;text-align:center;padding:12px;
background:#fffffff2;backdrop-filter:blur(12px);
box-shadow:0 4px 15px #0f172a12
}
nav a{
display:inline-block;text-decoration:none;color:#3346a3;padding:10px 15px;
margin:3px;border-radius:11px;font-weight:700;transition:.25s
}
nav a:hover{
color:#fff;background:linear-gradient(135deg,var(--p),var(--p2));
transform:translateY(-3px)
}
main{width:min(1150px,94%);margin:30px auto;animation:up .5s}
.card,.stat{
background:var(--card);border:1px solid var(--border);border-radius:20px;
box-shadow:0 12px 30px #0f172a0d
}
.card{padding:26px;margin-bottom:20px;transition:.3s}
.card:hover{transform:translateY(-2px)}
.hero{display:flex;align-items:center;justify-content:space-between;gap:20px}
.hero h2{font-size:32px;margin:7px 0}
.hero-icon{font-size:80px;animation:float 4s ease-in-out infinite}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.stat{text-align:center;padding:22px;position:relative;overflow:hidden;animation:card .6s both}
.stat:before{
content:"";position:absolute;left:0;right:0;top:0;height:4px;
background:linear-gradient(90deg,var(--p),var(--p2))
}
.stat:hover{transform:translateY(-7px);box-shadow:0 18px 35px #2563eb20}
.stat p{color:var(--muted);font-weight:700}
.stat h2{font-size:36px;color:var(--p2);margin:8px}
.quick-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.quick{
display:block;text-decoration:none;color:var(--text);padding:20px;
border:1px solid var(--border);border-radius:16px;transition:.25s
}
.quick:hover{transform:translateY(-6px);border-color:var(--p);box-shadow:0 12px 25px #6366f120}
.quick-icon{font-size:30px;display:block;margin-bottom:8px}
.quick small{display:block;color:var(--muted);margin-top:5px}
.progress{height:13px;background:#e2e8f0;border-radius:20px;overflow:hidden}
.bar{height:100%;background:linear-gradient(90deg,#6366f1,#06b6d4);animation:grow 1s}
table{width:100%;border-collapse:separate;border-spacing:0 7px}
th{padding:13px;text-align:left;color:#fff;background:linear-gradient(135deg,#1e3a8a,#2563eb)}
th:first-child{border-radius:9px 0 0 9px}
th:last-child{border-radius:0 9px 9px 0}
td{padding:13px;background:var(--card);border-bottom:1px solid var(--border)}
input,select{
padding:12px 14px;margin:5px;border:2px solid var(--border);border-radius:10px;
outline:none;background:#fff;font-size:14px
}
input:focus,select:focus{border-color:var(--p);box-shadow:0 0 0 4px #6366f11a}
.btn{
display:inline-block;border:0;text-decoration:none;cursor:pointer;color:#fff;
background:linear-gradient(135deg,#4f46e5,#2563eb);padding:11px 17px;
margin:5px;border-radius:10px;font-weight:700;transition:.25s
}
.btn:hover{transform:translateY(-3px);box-shadow:0 9px 20px #2563eb33}
.delete{background:linear-gradient(135deg,#ef4444,#dc2626)}
.edit{background:linear-gradient(135deg,#f59e0b,#d97706)}
.msg{padding:14px;border-radius:10px;margin:12px 0;background:#dcfce7;color:#166534;border-left:5px solid #22c55e}
.warn{padding:14px;border-radius:10px;margin:12px 0;background:#fef3c7;color:#92400e;border-left:5px solid #f59e0b}
.badge{display:inline-block;padding:7px 10px;border-radius:999px;font-size:12px;font-weight:800}
.good{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}
.circle{
width:170px;height:170px;border-radius:50%;display:flex;align-items:center;
justify-content:center;margin:auto;background:conic-gradient(#22c55e var(--pcent),#e2e8f0 var(--pcent))
}
.circle-in{
width:125px;height:125px;border-radius:50%;background:#fff;
display:flex;flex-direction:column;align-items:center;justify-content:center
}
.circle-in strong{font-size:27px;color:#16a34a}
.search{width:min(430px,90%)}
.empty{text-align:center;padding:30px;color:var(--muted)}
footer{text-align:center;padding:30px;color:var(--muted)}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-15px)}}
@keyframes down{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
@keyframes up{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes card{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes grow{from{width:0}}
@media(max-width:800px){.stats{grid-template-columns:repeat(2,1fr)}.quick-grid{grid-template-columns:repeat(2,1fr)}.hero{flex-direction:column;text-align:center}}
@media(max-width:520px){header h1{font-size:32px}.stats,.quick-grid{grid-template-columns:1fr}table{display:block;overflow-x:auto}}
</style>
"""

BASE = """<!doctype html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TrackNova - Smart Attendance</title>
""" + CSS + """
</head><body>
<header><div class="header-content"><h1>✦ TRACKNOVA</h1>
<p>Smart Student Attendance Management System</p></div></header>
<nav>
<a href="/">🏠 Dashboard</a>
<a href="/students">👨‍🎓 Students</a>
<a href="/attendance">📋 Attendance</a>
<a href="/lectures">📚 Lectures</a>
<a href="/reports">📊 Reports</a>
</nav>
<main>{{content|safe}}</main>
<footer>TRACKNOVA • Smart Attendance Management System</footer>
</body></html>"""

def page(template, **data):
    content = render_template_string(template, **data)
    return render_template_string(BASE, content=content)

@app.route("/")
def home():
    today = date.today().isoformat()
    with get_connection() as db:
        total = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    t = get_today_attendance(today)
    present = t["present"] or 0
    absent = t["absent"] or 0
    marked = present + absent
    percentage = round(present * 100 / marked, 1) if marked else 0
    reports = get_student_attendance()
    low = []
    for s in reports:
        total_l = s["total"] or 0
        present_l = s["present"] or 0
        if total_l:
            p = round(present_l * 100 / total_l, 1)
            if p < 75:
                low.append({"roll":s["roll_number"],"name":s["name"],"p":p})

    template = """
    <div class="card hero">
      <div><small style="color:#6366f1;font-weight:800">SMART ATTENDANCE</small>
      <h2>Welcome to TrackNova 👋</h2>
      <p>Manage students, lectures and attendance from one modern dashboard.</p>
      <b>📅 Today: {{today}}</b></div>
      <div class="hero-icon">🚀</div>
    </div>

    <div class="stats">
      <div class="stat"><p>👨‍🎓 Students</p><h2>{{total}}</h2><small>Registered</small></div>
      <div class="stat"><p>🟢 Present</p><h2>{{present}}</h2><small>Today</small></div>
      <div class="stat"><p>🔴 Absent</p><h2>{{absent}}</h2><small>Today</small></div>
      <div class="stat"><p>📈 Attendance</p><h2>{{percentage}}%</h2><small>Today</small></div>
    </div>

    <div class="card">
      <h2>📊 Today's Attendance</h2>
      <div style="display:grid;grid-template-columns:220px 1fr;gap:30px;align-items:center">
        <div class="circle" style="--pcent:{{percentage}}%">
          <div class="circle-in"><strong>{{percentage}}%</strong><small>Attendance</small></div>
        </div>
        <div>
          <p>🟢 Present: <b>{{present}}</b></p>
          <div class="progress"><div class="bar" style="width:{{(present/marked*100) if marked else 0}}%"></div></div>
          <p>🔴 Absent: <b>{{absent}}</b></p>
          <div class="progress"><div class="bar" style="width:{{(absent/marked*100) if marked else 0}}%;background:linear-gradient(90deg,#ef4444,#f97316)"></div></div>
        </div>
      </div>
    </div>

    <div class="card"><h2>⚡ Quick Actions</h2>
      <div class="quick-grid">
        <a class="quick" href="/attendance"><span class="quick-icon">📋</span><b>Take Attendance</b><small>Mark a lecture</small></a>
        <a class="quick" href="/students"><span class="quick-icon">👨‍🎓</span><b>Manage Students</b><small>Add or remove students</small></a>
        <a class="quick" href="/lectures"><span class="quick-icon">📚</span><b>Lecture History</b><small>View previous lectures</small></a>
        <a class="quick" href="/reports"><span class="quick-icon">📊</span><b>Reports</b><small>Check attendance</small></a>
      </div>
    </div>

    <div class="card"><h2>⚠️ Low Attendance</h2>
    {% if low %}
    <table><tr><th>Roll</th><th>Name</th><th>Attendance</th><th>Status</th></tr>
    {% for s in low %}<tr><td>{{s.roll}}</td><td>{{s.name}}</td><td>{{s.p}}%</td>
    <td><span class="badge bad">⚠ Low</span></td></tr>{% endfor %}</table>
    {% else %}<div class="msg">🎉 No student is below 75%.</div>{% endif %}
    </div>
    """
    return page(template,today=today,total=total,present=present,absent=absent,percentage=percentage,low=low)

@app.route("/students", methods=["GET","POST"])
def students_page():
    message = ""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            roll = request.form.get("roll","").strip()
            name = request.form.get("name","").strip()
            if not roll or not name:
                message = "Please enter roll number and name."
            else:
                try:
                    add_student(roll,name)
                    message = "Student added successfully! 🎉"
                except sqlite3.IntegrityError:
                    message = "This roll number already exists."
        elif action == "delete":
            delete_student(request.form.get("student_id"))
            message = "Student deleted successfully."
    students = get_students()
    template = """
    <div class="card"><h1>👨‍🎓 Manage Students</h1>
    {% if message %}<div class="msg">{{message}}</div>{% endif %}
    <h3>➕ Add Student</h3>
    <form method="post"><input type="hidden" name="action" value="add">
    <input type="number" name="roll" placeholder="Roll Number" required>
    <input type="text" name="name" placeholder="Student Name" required>
    <button class="btn">+ Add Student</button></form>
    <p>Total Students: <b>{{students|length}}</b></p>
    <input class="search" id="search" placeholder="🔍 Search student..." onkeyup="filterStudents()">
    {% if students %}
    <table id="studentTable"><tr><th>Roll No.</th><th>Name</th><th>Action</th></tr>
    {% for s in students %}<tr><td>{{s["roll_number"]}}</td><td>{{s["name"]}}</td><td>
    <form method="post" onsubmit="return confirm('Delete this student?')">
    <input type="hidden" name="action" value="delete"><input type="hidden" name="student_id" value="{{s['id']}}">
    <button class="btn delete">🗑 Delete</button></form></td></tr>{% endfor %}</table>
    {% else %}<div class="empty">No students added yet.</div>{% endif %}
    </div>
    <script>function filterStudents(){let x=document.getElementById('search').value.toLowerCase();document.querySelectorAll('#studentTable tr').forEach((r,i)=>{if(i)r.style.display=r.innerText.toLowerCase().includes(x)?'':'none'})}</script>
    """
    return page(template,students=students,message=message)

@app.route("/attendance", methods=["GET","POST"])
def attendance_page():
    students = get_students()
    if request.method == "POST":
        try:
            lecture_id = add_lecture(request.form["lecture_date"],request.form["lecture_number"],
                                     request.form["subject"],request.form["start_time"],request.form["end_time"])
        except Exception as e:
            return "Error creating lecture: " + str(e)
        for s in students:
            status = request.form.get("student_"+str(s["id"]))
            if status in ("Present","Absent"):
                save_attendance(s["id"],lecture_id,status)
        return redirect(url_for("lecture_view",lecture_id=lecture_id))

    template = """
    <div class="card"><h1>📋 Take Attendance</h1>
    <form method="post">
    <input type="date" name="lecture_date" value="{{today}}" required>
    <input type="number" name="lecture_number" placeholder="Lecture No." required>
    <input type="text" name="subject" placeholder="Subject" required>
    <input type="time" name="start_time" required><input type="time" name="end_time" required>
    {% if students %}<table><tr><th>Roll</th><th>Name</th><th>Status</th></tr>
    {% for s in students %}<tr><td>{{s["roll_number"]}}</td><td>{{s["name"]}}</td><td>
    <label><input type="radio" name="student_{{s['id']}}" value="Present" required> 🟢 Present</label>
    <label><input type="radio" name="student_{{s['id']}}" value="Absent"> 🔴 Absent</label>
    </td></tr>{% endfor %}</table>
    <button class="btn">💾 Save Attendance</button>
    {% else %}<div class="warn">⚠️ Add students first.</div><a class="btn" href="/students">Add Students</a>{% endif %}
    </form></div>
    """
    return page(template,students=students,today=date.today().isoformat())

@app.route("/lecture/<int:lecture_id>")
def lecture_view(lecture_id):
    lecture = get_lecture(lecture_id)
    if not lecture: return "Lecture not found."
    attendance = get_lecture_attendance(lecture_id)
    present = sum(1 for s in attendance if s["status"]=="Present")
    absent = sum(1 for s in attendance if s["status"]=="Absent")
    total = present + absent
    percentage = round(present*100/total,1) if total else 0
    template = """
    <div class="card"><h1>📚 {{lecture["subject"]}}</h1>
    <p>📅 {{lecture["lecture_date"]}} &nbsp; | &nbsp; Lecture {{lecture["lecture_number"]}} &nbsp; | &nbsp; {{lecture["start_time"]}} - {{lecture["end_time"]}}</p>
    <div class="stats">
    <div class="stat"><p>🟢 Present</p><h2>{{present}}</h2></div>
    <div class="stat"><p>🔴 Absent</p><h2>{{absent}}</h2></div>
    <div class="stat"><p>👥 Total</p><h2>{{total}}</h2></div>
    <div class="stat"><p>📈 Rate</p><h2>{{percentage}}%</h2></div></div>
    <table><tr><th>Roll</th><th>Name</th><th>Status</th></tr>
    {% for s in attendance %}<tr><td>{{s["roll_number"]}}</td><td>{{s["name"]}}</td><td>
    {% if s["status"]=="Present" %}<span class="badge good">🟢 Present</span>
    {% elif s["status"]=="Absent" %}<span class="badge bad">🔴 Absent</span>
    {% else %}⚪ Not Marked{% endif %}</td></tr>{% endfor %}</table>
    <a class="btn edit" href="/edit/{{lecture['id']}}">✏️ Edit</a>
    <a class="btn" href="/lectures">← Lectures</a></div>
    """
    return page(template,lecture=lecture,attendance=attendance,present=present,absent=absent,total=total,percentage=percentage)

@app.route("/edit/<int:lecture_id>", methods=["GET","POST"])
def edit_attendance(lecture_id):
    lecture = get_lecture(lecture_id)
    if not lecture: return "Lecture not found."
    students = get_lecture_attendance(lecture_id)
    if request.method == "POST":
        for s in students:
            status=request.form.get("student_"+str(s["id"]))
            if status in ("Present","Absent"): save_attendance(s["id"],lecture_id,status)
        return redirect(url_for("lecture_view",lecture_id=lecture_id))
    template = """
    <div class="card"><h1>✏️ Edit Attendance</h1><h2>{{lecture["subject"]}}</h2>
    <form method="post"><table><tr><th>Roll</th><th>Name</th><th>Status</th></tr>
    {% for s in students %}<tr><td>{{s["roll_number"]}}</td><td>{{s["name"]}}</td><td>
    <select name="student_{{s['id']}}">
    <option value="Present" {% if s["status"]=="Present" %}selected{% endif %}>🟢 Present</option>
    <option value="Absent" {% if s["status"]=="Absent" %}selected{% endif %}>🔴 Absent</option>
    </select></td></tr>{% endfor %}</table>
    <button class="btn">💾 Save Changes</button></form></div>
    """
    return page(template,lecture=lecture,students=students)

@app.route("/lectures")
def lectures_page():
    lectures=get_lectures()
    template="""
    <div class="card"><h1>📚 Lecture History</h1>
    {% if lectures %}<table><tr><th>Date</th><th>No.</th><th>Subject</th><th>Time</th><th>Action</th></tr>
    {% for l in lectures %}<tr><td>{{l["lecture_date"]}}</td><td>{{l["lecture_number"]}}</td><td><b>{{l["subject"]}}</b></td>
    <td>{{l["start_time"]}} - {{l["end_time"]}}</td><td><a class="btn" href="/lecture/{{l['id']}}">👁 View</a></td></tr>{% endfor %}
    </table>{% else %}<div class="empty">No lectures recorded yet.</div>{% endif %}</div>
    """
    return page(template,lectures=lectures)

@app.route("/reports")
def reports_page():
    reports=get_student_attendance()
    template="""
    <div class="card"><h1>📊 Attendance Reports</h1>
    {% if reports %}<table><tr><th>Roll</th><th>Name</th><th>Present</th><th>Total</th><th>Attendance</th></tr>
    {% for r in reports %}{% set total=r["total"] or 0 %}{% set present=r["present"] or 0 %}
    <tr><td>{{r["roll_number"]}}</td><td><b>{{r["name"]}}</b></td><td>{{present}}</td><td>{{total}}</td><td>
    {% if total %}{% set p=(present*100/total)|round(1) %}<div class="progress"><div class="bar" style="width:{{p}}%"></div></div>
    {% if p<75 %}<span class="badge bad">{{p}}% ⚠ LOW</span>{% else %}<span class="badge good">{{p}}% ✓ Good</span>{% endif %}
    {% else %}No attendance{% endif %}</td></tr>{% endfor %}</table>
    {% else %}<div class="empty">No reports available yet.</div>{% endif %}</div>
    """
    return page(template,reports=reports)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
