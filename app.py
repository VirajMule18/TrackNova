from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template_string,
    session,
    Response
)

from datetime import date
import sqlite3
import csv
import io
from functools import wraps

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
    get_today_attendance,
    authenticate,
    get_users,
    create_user,
    get_classes,
    add_class,
    get_subjects,
    add_subject
)


# =========================================================
# APP
# =========================================================

app = Flask(__name__)

# Change this later to a random secret
app.secret_key = "tracknova-super-secret-key-2026"


# =========================================================
# DESIGN
# =========================================================

CSS = """

<style>

*{
    box-sizing:border-box;
}

body{

    margin:0;

    font-family:
    Arial,
    Helvetica,
    sans-serif;

    color:#172033;

    background:
    linear-gradient(
        135deg,
        #eef2ff,
        #f8fafc,
        #eff6ff
    );

    min-height:100vh;
}


header{

    color:white;

    text-align:center;

    padding:55px 20px;

    background:
    linear-gradient(
        135deg,
        #111827,
        #3730a3,
        #2563eb
    );

    position:relative;

    overflow:hidden;
}


header:before{

    content:"";

    position:absolute;

    width:250px;

    height:250px;

    border-radius:50%;

    background:#ffffff15;

    top:-100px;

    left:-50px;

    animation:float 5s infinite ease-in-out;
}


header:after{

    content:"";

    position:absolute;

    width:200px;

    height:200px;

    border-radius:50%;

    background:#ffffff12;

    bottom:-100px;

    right:-30px;

    animation:float 6s infinite ease-in-out;
}


.header-content{

    position:relative;

    z-index:2;
}


header h1{

    margin:0;

    font-size:45px;

    letter-spacing:3px;

}


header p{

    margin:10px 0 0;

    opacity:.9;

}


nav{

    position:sticky;

    top:0;

    z-index:100;

    background:#ffffffee;

    backdrop-filter:blur(12px);

    padding:10px;

    text-align:center;

    box-shadow:
    0 4px 20px #00000012;
}


nav a{

    display:inline-block;

    text-decoration:none;

    color:#334155;

    padding:11px 15px;

    margin:3px;

    border-radius:12px;

    font-weight:bold;

    transition:.25s;
}


nav a:hover{

    color:white;

    background:
    linear-gradient(
        135deg,
        #6366f1,
        #2563eb
    );

    transform:
    translateY(-2px);

}


main{

    width:min(
        1150px,
        94%
    );

    margin:
    30px auto;

}


.card{

    background:white;

    border:
    1px solid #e2e8f0;

    border-radius:22px;

    padding:25px;

    margin-bottom:20px;

    box-shadow:
    0 15px 40px #0f172a0c;

    animation:
    slideUp .5s ease;

}


.stats{

    display:grid;

    grid-template-columns:
    repeat(4,1fr);

    gap:18px;

    margin-bottom:20px;

}


.stat{

    background:white;

    padding:23px;

    text-align:center;

    border-radius:20px;

    border:
    1px solid #e2e8f0;

    box-shadow:
    0 12px 30px #0f172a0c;

    transition:.3s;

}


.stat:hover{

    transform:
    translateY(-6px);

    box-shadow:
    0 20px 40px #6366f133;

}


.stat p{

    color:#64748b;

    font-weight:bold;

}


.stat h2{

    color:#2563eb;

    font-size:32px;

    margin:8px;
}


.grid{

    display:grid;

    grid-template-columns:
    repeat(2,1fr);

    gap:18px;

}


.quick{

    display:block;

    padding:25px;

    border:
    1px solid #e2e8f0;

    border-radius:18px;

    color:#172033;

    text-decoration:none;

    transition:.3s;

    background:
    linear-gradient(
        135deg,
        #ffffff,
        #f8fafc
    );

}


.quick:hover{

    transform:
    translateY(-5px);

    border-color:#6366f1;

    box-shadow:
    0 15px 35px #6366f126;

}


input,
select{

    padding:12px 14px;

    margin:5px;

    border:
    2px solid #e2e8f0;

    border-radius:12px;

    font-size:14px;

    background:white;

}


input:focus,
select:focus{

    outline:none;

    border-color:#6366f1;

}


.btn{

    display:inline-block;

    border:0;

    cursor:pointer;

    color:white;

    background:
    linear-gradient(
        135deg,
        #6366f1,
        #2563eb
    );

    padding:12px 18px;

    margin:5px;

    border-radius:12px;

    font-weight:bold;

    text-decoration:none;

    transition:.25s;

}


.btn:hover{

    transform:
    translateY(-3px);

    box-shadow:
    0 10px 25px #2563eb44;

}


.delete{

    background:
    linear-gradient(
        135deg,
        #ef4444,
        #dc2626
    );

}


table{

    width:100%;

    border-collapse:
    separate;

    border-spacing:
    0 7px;

}


th{

    background:#2563eb;

    color:white;

    padding:13px;

    text-align:left;

}


td{

    background:white;

    padding:13px;

    border-bottom:
    1px solid #e2e8f0;

}


.badge{

    display:inline-block;

    padding:7px 12px;

    border-radius:50px;

    font-size:12px;

    font-weight:bold;

}


.good{

    background:#dcfce7;

    color:#166534;

}


.bad{

    background:#fee2e2;

    color:#991b1b;

}


.msg{

    background:#dcfce7;

    color:#166534;

    padding:14px;

    border-radius:12px;

    margin:12px 0;

}


.warn{

    background:#fef3c7;

    color:#92400e;

    padding:14px;

    border-radius:12px;

    margin:12px 0;

}


.progress{

    height:14px;

    background:#e2e8f0;

    border-radius:30px;

    overflow:hidden;

}


.bar{

    height:100%;

    background:
    linear-gradient(
        90deg,
        #6366f1,
        #06b6d4
    );

    border-radius:30px;

    transition:
    width 1s ease;

}


.login{

    max-width:430px;

    margin:
    70px auto;

}


.login h1{

    text-align:center;

}


.search{

    width:min(
        400px,
        90%
    );

}


.empty{

    text-align:center;

    padding:40px;

    color:#64748b;

}


footer{

    text-align:center;

    padding:35px;

    color:#64748b;

}


@keyframes float{

    0%{
        transform:translateY(0);
    }

    50%{
        transform:translateY(-15px);
    }

    100%{
        transform:translateY(0);
    }

}


@keyframes slideUp{

    from{

        opacity:0;

        transform:
        translateY(20px);

    }

    to{

        opacity:1;

        transform:
        translateY(0);

    }

}


@media(max-width:800px){

    .stats{

        grid-template-columns:
        repeat(2,1fr);

    }

    .grid{

        grid-template-columns:1fr;

    }

}


@media(max-width:550px){

    header h1{

        font-size:32px;

    }

    .stats{

        grid-template-columns:1fr;

    }

    table{

        display:block;

        overflow-x:auto;

    }

}

</style>

"""


# =========================================================
# BASE PAGE
# =========================================================

BASE = """

<!DOCTYPE html>

<html>

<head>

<meta
name="viewport"
content="width=device-width, initial-scale=1"
>

<title>
TrackNova
</title>

"""

+ CSS +

"""

</head>


<body>


<header>

<div class="header-content">

<h1>
✦ TRACKNOVA
</h1>

<p>
Smart College Attendance Management System
</p>

</div>

</header>


<nav>

<a href="/">
🏠 Dashboard
</a>


{% if session.get("user_id") %}


<a href="/students">
👨‍🎓 Students
</a>


<a href="/attendance">
📋 Attendance
</a>


<a href="/lectures">
📚 History
</a>


<a href="/reports">
📊 Reports
</a>


{% if session.get("role") in ["admin","teacher"] %}

<a href="/manage">
⚙️ Manage
</a>

{% endif %}


{% if session.get("role") == "student" %}

<a href="/student">
👤 My Attendance
</a>

{% endif %}


<a href="/logout">
🚪 Logout
</a>


{% else %}


<a href="/login">
🔐 Login
</a>


{% endif %}


</nav>


<main>

{{ content|safe }}

</main>


<footer>

TRACKNOVA

<br>

Smart Attendance • Better Education • Digital Campus

</footer>


</body>

</html>

"""


# =========================================================
# PAGE HELPER
# =========================================================

def page(template, **data):

    return render_template_string(

        BASE,

        content=
        render_template_string(
            template,
            **data
        )

    )


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(function):

    @wraps(function)

    def wrapper(
        *args,
        **kwargs
    ):

        if not session.get(
            "user_id"
        ):

            return redirect(
                url_for(
                    "login"
                )
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# STAFF ONLY
# =========================================================

def staff_required(function):

    @wraps(function)

    def wrapper(
        *args,
        **kwargs
    ):

        if not session.get(
            "user_id"
        ):

            return redirect(
                url_for(
                    "login"
                )
            )


        if session.get(
            "role"
        ) not in [
            "admin",
            "teacher"
        ]:

            return "Access denied.", 403


        return function(
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST"
    ]
)

def login():

    error = ""


    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()


        password = request.form.get(
            "password",
            ""
        )


        user = authenticate(
            username,
            password
        )


        if user:

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            session["full_name"] = user["full_name"]

            session["role"] = user["role"]


            if user["role"] == "student":

                return redirect(
                    url_for(
                        "student_portal"
                    )
                )


            return redirect(
                url_for(
                    "home"
                )
            )


        error = (
            "Invalid username or password."
        )


    template = """

<div class="card login">

<h1>
🔐 TrackNova Login
</h1>


<p style="
text-align:center;
color:#64748b;
">

Secure College Attendance Portal

</p>


{% if error %}

<div class="warn">

{{ error }}

</div>

{% endif %}


<form method="post">

<input
style="width:95%"
name="username"
placeholder="👤 Username"
required
>


<input
style="width:95%"
type="password"
name="password"
placeholder="🔒 Password"
required
>


<button
class="btn"
style="width:95%"
>

Login

</button>


</form>


<div class="warn">

<b>Default Admin</b>

<br>

Username:
<b>admin</b>

<br>

Password:
<b>admin123</b>

</div>


</div>

"""


    return page(
        template,
        error=error
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/logout"
)

def logout():

    session.clear()

    return redirect(
        url_for(
            "login"
        )
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
@login_required

def home():

    today = date.today().isoformat()


    with get_connection() as db:

        total = db.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]


    today_data = get_today_attendance(
        today
    )


    present = (
        today_data["present"]
        or 0
    )


    absent = (
        today_data["absent"]
        or 0
    )


    marked = present + absent


    percentage = (
        round(
            present * 100 / marked,
            1
        )
        if marked
        else 0
    )


    template = """

<div class="card">

<h2>

Welcome,
{{ session["full_name"] }}
👋

</h2>


<p>

Role:

<b>
{{ session["role"]|upper }}
</b>

&nbsp; • &nbsp;

{{ today }}

</p>

</div>


<div class="stats">


<div class="stat">

<p>
👨‍🎓 Total Students
</p>

<h2>
{{ total }}
</h2>

</div>


<div class="stat">

<p>
🟢 Present Today
</p>

<h2>
{{ present }}
</h2>

</div>


<div class="stat">

<p>
🔴 Absent Today
</p>

<h2>
{{ absent }}
</h2>

</div>


<div class="stat">

<p>
📈 Attendance
</p>

<h2>
{{ percentage }}%
</h2>

</div>


</div>


<div class="card">

<h2>
⚡ Quick Actions
</h2>


<div class="grid">


<a
class="quick"
href="/attendance"
>

📋

<b>
Take Attendance
</b>

<br>

<small>
Mark today's attendance
</small>

</a>


<a
class="quick"
href="/students"
>

👨‍🎓

<b>
Students
</b>

<br>

<small>
Manage students
</small>

</a>


<a
class="quick"
href="/reports"
>

📊

<b>
Reports
</b>

<br>

<small>
View attendance analytics
</small>

</a>


<a
class="quick"
href="/lectures"
>

📚

<b>
Lecture History
</b>

<br>

<small>
Previous attendance
</small>

</a>


</div>

</div>


<div class="card">

<h2>
🎯 TrackNova Features
</h2>

<div class="grid">

<div class="quick">
🔐 Secure Login
</div>

<div class="quick">
📱 Mobile Friendly
</div>

<div class="quick">
📊 Smart Reports
</div>

<div class="quick">
⚡ Fast Attendance
</div>

</div>

</div>

"""


    return page(
        template,
        total=total,
        present=present,
        absent=absent,
        percentage=percentage,
        today=today
    )


# =========================================================
# STUDENT PORTAL
# =========================================================

@app.route(
    "/student"
)

@login_required

def student_portal():

    if session.get(
        "role"
    ) != "student":

        return redirect(
            url_for(
                "home"
            )
        )


    with get_connection() as db:

        student = db.execute("""

SELECT *

FROM students

WHERE id = (

SELECT student_id

FROM users

WHERE id = ?

)

""", (
            session["user_id"],
        )).fetchone()


    if not student:

        return "Student profile not linked."


    with get_connection() as db:

        result = db.execute("""

SELECT

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

FROM lecture_attendance la

WHERE la.student_id = ?

""", (
            student["id"],
        )).fetchone()


    total = (
        result["total"]
        or 0
    )


    present = (
        result["present"]
        or 0
    )


    absent = total - present


    percentage = (

        round(
            present * 100 / total,
            1
        )

        if total

        else 0

    )


    template = """

<div class="card">

<h1>
👨‍🎓 My Attendance
</h1>


<p>

<b>
{{ student["name"] }}
</b>

<br>

Roll Number:
{{ student["roll_number"] }}

</p>


</div>


<div class="stats">


<div class="stat">

<p>
📚 Total
</p>

<h2>
{{ total }}
</h2>

</div>


<div class="stat">

<p>
🟢 Present
</p>

<h2>
{{ present }}
</h2>

</div>


<div class="stat">

<p>
🔴 Absent
</p>

<h2>
{{ absent }}
</h2>

</div>


<div class="stat">

<p>
📈 Percentage
</p>

<h2>
{{ percentage }}%
</h2>

</div>


</div>


<div class="card">

<h2>
Attendance Progress
</h2>


<div class="progress">

<div
class="bar"
style="width:{{ percentage }}%"
>

</div>

</div>


{% if percentage < 75 %}

<div class="warn">

⚠️ Your attendance is below 75%.

Please attend more lectures.

</div>


{% else %}

<div class="msg">

✅ Excellent!

Your attendance is above 75%.

</div>

{% endif %}


</div>

"""


    return page(
        template,
        student=student,
        total=total,
        present=present,
        absent=absent,
        percentage=percentage
    )


# =========================================================
# STUDENTS
# =========================================================

@app.route(
    "/students",
    methods=[
        "GET",
        "POST"
    ]
)

@staff_required

def students_page():

    message = ""


    if request.method == "POST":

        action = request.form.get(
            "action"
        )


        if action == "add":

            try:

                add_student(

                    request.form["roll"],

                    request.form["name"]

                )


                message = (
                    "Student added successfully! 🎉"
                )


            except sqlite3.IntegrityError:

                message = (
                    "This roll number already exists."
                )


        elif action == "delete":

            delete_student(
                request.form["student_id"]
            )


            message = (
                "Student deleted."
            )


    students = get_students()


    template = """

<div class="card">

<h1>
👨‍🎓 Student Management
</h1>


<p style="color:#64748b">

Manage your college students.

</p>


{% if message %}

<div class="msg">
{{ message }}
</div>

{% endif %}


<form method="post">

<input
type="hidden"
name="action"
value="add"
>


<input
type="number"
name="roll"
placeholder="🔢 Roll Number"
required
>


<input
name="name"
placeholder="👤 Student Name"
required
>


<button class="btn">

+ Add Student

</button>


</form>


<input

class="search"

id="studentSearch"

placeholder="🔍 Search student..."

onkeyup="searchStudents()"

>


</div>


<div class="card">

<h2>
📋 Student List
</h2>


{% if students %}


<table id="studentTable">


<tr>

<th>
Roll Number
</th>

<th>
Student
</th>

<th>
Class
</th>

<th>
Action
</th>

</tr>


{% for student in students %}


<tr>


<td>

<b>
#{{ student["roll_number"] }}
</b>

</td>


<td>

👤

{{ student["name"] }}

</td>


<td>

{{ student["class_name"] or "Not assigned" }}

</td>


<td>


<form
method="post"
style="display:inline"
onsubmit="
return confirm(
'Delete this student?'
)
"
>


<input
type="hidden"
name="action"
value="delete"
>


<input
type="hidden"
name="student_id"
value="{{ student['id'] }}"
>


<button
class="btn delete"
>

🗑 Delete

</button>


</form>


</td>


</tr>


{% endfor %}


</table>


{% else %}


<div class="empty">

<h2>
👨‍🎓
</h2>

<h3>
No students yet
</h3>

<p>
Add your first student above.
</p>

</div>


{% endif %}


</div>


<script>

function searchStudents(){

let value =
document
.getElementById(
"studentSearch"
)
.value
.toLowerCase();


let rows =
document
.querySelectorAll(
"#studentTable tr"
);


rows.forEach(
function(row,index){

if(index === 0)
return;


row.style.display =

row.innerText
.toLowerCase()
.includes(value)

? ""

: "none";

});

}

</script>

"""


    return page(
        template,
        students=students,
        message=message
    )


# =========================================================
# ATTENDANCE
# =========================================================

@app.route(
    "/attendance",
    methods=[
        "GET",
        "POST"
    ]
)

@staff_required

def attendance_page():

    students = get_students()


    if request.method == "POST":

        lecture_id = add_lecture(

            request.form[
                "lecture_date"
            ],

            request.form[
                "lecture_number"
            ],

            request.form[
                "subject"
            ],

            request.form[
                "start_time"
            ],

            request.form[
                "end_time"
            ],

            session[
                "user_id"
            ]

        )


        for student in students:

            status = request.form.get(

                "student_"
                + str(
                    student["id"]
                )

            )


            if status in (
                "Present",
                "Absent"
            ):

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


    template = """

<div class="card">

<h1>
📋 Take Attendance
</h1>


<p>
Mark attendance quickly.
</p>


</div>


{% if students %}


<form method="post">


<div class="card">


<h2>
📚 Lecture Details
</h2>


<input
type="date"
name="lecture_date"
value="{{ today }}"
required
>


<input
type="number"
name="lecture_number"
placeholder="📖 Lecture Number"
min="1"
required
>


<input
type="text"
name="subject"
placeholder="📚 Subject"
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


</div>


<div class="card">


<div style="
display:flex;
justify-content:space-between;
align-items:center;
flex-wrap:wrap;
">


<h2>
👨‍🎓 Students
</h2>


<div>


<button
type="button"
class="btn"
onclick="markAll('Present')"
>

🟢 All Present

</button>


<button
type="button"
class="btn delete"
onclick="markAll('Absent')"
>

🔴 All Absent

</button>


</div>


</div>


<table>


<tr>

<th>
Roll
</th>

<th>
Name
</th>

<th>
Status
</th>

</tr>


{% for student in students %}


<tr>


<td>

#{{ student["roll_number"] }}

</td>


<td>

👤

{{ student["name"] }}

</td>


<td>


<label>

<input

type="radio"

name="student_{{ student['id'] }}"

value="Present"

required

>

🟢 Present

</label>


<label style="margin-left:15px">


<input

type="radio"

name="student_{{ student['id'] }}"

value="Absent"

>

🔴 Absent

</label>


</td>


</tr>


{% endfor %}


</table>


<br>


<button
class="btn"
style="
font-size:17px;
padding:15px 30px;
"
>

💾 Save Attendance

</button>


</div>


</form>


{% else %}


<div class="card">

<div class="empty">

<h2>
👨‍🎓
</h2>

<h3>
No Students
</h3>

<p>
Add students before taking attendance.
</p>


<a
class="btn"
href="/students"
>

+ Add Students

</a>


</div>

</div>


{% endif %}


<script>

function markAll(status){

let buttons =
document.querySelectorAll(
'input[type="radio"]'
);


buttons.forEach(
function(button){

if(
button.value === status
){

button.checked =
true;

}

});

}

</script>

"""


    return page(

        template,

        students=students,

        today=date.today().isoformat()

    )


# =========================================================
# LECTURE VIEW
# =========================================================

@app.route(
    "/lecture/<int:lecture_id>"
)

@staff_required

def lecture_view(
    lecture_id
):

    lecture = get_lecture(
        lecture_id
    )


    attendance =
        get_lecture_attendance(
            lecture_id
        )


    if not lecture:

        return (
            "Lecture not found."
        )


    template = """

<div class="card">

<h1>
📚 {{ lecture["subject"] }}
</h1>


<p>

📅
{{ lecture["lecture_date"] }}

&nbsp; • &nbsp;

Lecture
{{ lecture["lecture_number"] }}

&nbsp; • &nbsp;

⏰
{{ lecture["start_time"] }}

-

{{ lecture["end_time"] }}

</p>


</div>


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


{% for student in attendance %}


<tr>


<td>

#{{ student["roll_number"] }}

</td>


<td>

{{ student["name"] }}

</td>


<td>


{% if student["status"] == "Present" %}


<span class="badge good">

🟢 Present

</span>


{% elif student["status"] == "Absent" %}


<span class="badge bad">

🔴 Absent

</span>


{% else %}


Not marked


{% endif %}


</td>


</tr>


{% endfor %}


</table>


</div>

"""


    return page(

        template,

        lecture=lecture,

        attendance=attendance

    )


# =========================================================
# LECTURE HISTORY
# =========================================================

@app.route(
    "/lectures"
)

@staff_required

def lectures_page():

    lectures =
        get_lectures()


    template = """

<div class="card">

<h1>
📚 Lecture History
</h1>


<p>
All previous attendance sessions.
</p>


{% if lectures %}


<table>


<tr>

<th>
Date
</th>

<th>
Subject
</th>

<th>
Teacher
</th>

<th>
View
</th>

</tr>


{% for lecture in lectures %}


<tr>


<td>

{{ lecture["lecture_date"] }}

</td>


<td>

{{ lecture["subject"] }}

</td>


<td>

{{ lecture["teacher_name"] or "-" }}

</td>


<td>


<a

class="btn"

href="/lecture/{{ lecture['id'] }}"

>

View

</a>


</td>


</tr>


{% endfor %}


</table>


{% else %}


<div class="empty">

<h2>
📚
</h2>

<p>
No lectures recorded yet.
</p>

</div>


{% endif %}


</div>

"""


    return page(

        template,

        lectures=lectures

    )


# =========================================================
# REPORTS
# =========================================================

@app.route(
    "/reports"
)

@login_required

def reports_page():

    reports =
        get_student_attendance()


    template = """

<div class="card">

<h1>
📊 Attendance Reports
</h1>


<p>
Complete student attendance analytics.
</p>


<a
class="btn"
href="/export.csv"
>

📥 Download CSV

</a>


<button
class="btn"
onclick="window.print()"
>

🖨 Print / Save PDF

</button>


</div>


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
Present
</th>

<th>
Total
</th>

<th>
Attendance
</th>

</tr>


{% for student in reports %}


{% set total =
student["total"] or 0
%}


{% set present =
student["present"] or 0
%}


<tr>


<td>

#{{ student["roll_number"] }}

</td>


<td>

{{ student["name"] }}

</td>


<td>

{{ present }}

</td>


<td>

{{ total }}

</td>


<td>


{% if total %}


{% set percentage =
(present * 100 / total)
|round(1)
%}


<div class="progress">


<div

class="bar"

style="
width:{{ percentage }}%;
"

>

</div>


</div>


<br>


{% if percentage < 75 %}


<span class="badge bad">

{{ percentage }}%

LOW

</span>


{% else %}


<span class="badge good">

{{ percentage }}%

GOOD

</span>


{% endif %}


{% else %}


No attendance


{% endif %}


</td>


</tr>


{% endfor %}


</table>


</div>

"""


    return page(

        template,

        reports=reports

    )


# =========================================================
# CSV EXPORT
# =========================================================

@app.route(
    "/export.csv"
)

@login_required

def export_csv():

    reports =
        get_student_attendance()


    output =
        io.StringIO()


    writer =
        csv.writer(
            output
        )


    writer.writerow([

        "Roll Number",

        "Student Name",

        "Present",

        "Total Lectures",

        "Attendance %"

    ])


    for student in reports:

        total =
            student["total"] or 0


        present =
            student["present"] or 0


        percentage = (

            round(
                present * 100 / total,
                1
            )

            if total

            else 0

        )


        writer.writerow([

            student[
                "roll_number"
            ],

            student[
                "name"
            ],

            present,

            total,

            percentage

        ])


    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={

            "Content-Disposition":

            "attachment; "
            "filename=tracknova_attendance.csv"

        }

    )


# =========================================================
# MANAGEMENT
# =========================================================

@app.route(
    "/manage",
    methods=[
        "GET",
        "POST"
    ]
)

@staff_required

def manage():

    message = ""


    if request.method == "POST":

        action =
            request.form.get(
                "action"
            )


        try:

            if action == "class":

                add_class(

                    request.form[
                        "class_name"
                    ],

                    request.form[
                        "department"
                    ],

                    request.form[
                        "semester"
                    ],

                    request.form.get(
                        "division",
                        ""
                    )

                )


                message =
                    "Class added successfully."


            elif action == "teacher":

                create_user(

                    request.form[
                        "username"
                    ],

                    request.form[
                        "password"
                    ],

                    request.form[
                        "full_name"
                    ],

                    "teacher"

                )


                message =
                    "Teacher account created."


            elif action == "subject":

                add_subject(

                    request.form[
                        "subject_name"
                    ],

                    request.form.get(
                        "subject_code",
                        ""
                    ),

                    request.form.get(
                        "class_id"
                    ),

                    request.form.get(
                        "teacher_id"
                    )

                )


                message =
                    "Subject added successfully."


        except sqlite3.IntegrityError:

            message =
                "This information already exists."


    classes =
        get_classes()


    teachers =
        get_users(
            "teacher"
        )


    subjects =
        get_subjects()


    template = """

<div class="card">

<h1>
⚙️ College Management
</h1>


{% if message %}


<div class="msg">

{{ message }}

</div>


{% endif %}


</div>


<div class="grid">


<div class="card">


<h2>
🏫 Add Class
</h2>


<form method="post">


<input
type="hidden"
name="action"
value="class"
>


<input
name="class_name"
placeholder="Example: SY CSE"
required
>


<input
name="department"
placeholder="Department"
required
>


<input
name="semester"
placeholder="Semester"
required
>


<input
name="division"
placeholder="Division"
>


<button class="btn">

Add Class

</button>


</form>


</div>


<div class="card">


<h2>
👨‍🏫 Add Teacher
</h2>


<form method="post">


<input
type="hidden"
name="action"
value="teacher"
>


<input
name="full_name"
placeholder="Teacher Name"
required
>


<input
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


<button class="btn">

Create Teacher

</button>


</form>


</div>


</div>


<div class="card">


<h2>
📚 Add Subject
</h2>


<form method="post">


<input
type="hidden"
name="action"
value="subject"
>


<input
name="subject_name"
placeholder="Subject Name"
required
>


<input
name="subject_code"
placeholder="Subject Code"
>


<select
name="class_id"
>


<option value="">

Select Class

</option>


{% for c in classes %}


<option
value="{{ c['id'] }}"
>


{{ c["class_name"] }}

-

{{ c["department"] }}


</option>


{% endfor %}


</select>


<select
name="teacher_id"
>


<option value="">

Select Teacher

</option>


{% for teacher in teachers %}


<option
value="{{ teacher['id'] }}"
>


{{ teacher["full_name"] }}


</option>


{% endfor %}


</select>


<button class="btn">

Add Subject

</button>


</form>


</div>


<div class="card">


<h2>
📚 Current Subjects
</h2>


<table>


<tr>

<th>
Subject
</th>

<th>
Code
</th>

<th>
Class
</th>

<th>
Teacher
</th>

</tr>


{% for subject in subjects %}


<tr>


<td>
{{ subject["subject_name"] }}
</td>


<td>
{{ subject["subject_code"] }}
</td>


<td>
{{ subject["class_name"] or "-" }}
</td>


<td>
{{ subject["teacher_name"] or "-" }}
</td>


</tr>


{% endfor %}


</table>


</div>

"""


    return page(

        template,

        message=message,

        classes=classes,

        teachers=teachers,

        subjects=subjects

    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000

    )
