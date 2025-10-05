from flask import Flask, render_template, request, redirect, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"
DB_NAME = 'students.db'

# --------------------------
# Database helper functions
# --------------------------

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Alumni table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT NOT NULL
        )
    ''')

    # Workshops table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workshops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT NOT NULL,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            guest_lecturer TEXT NOT NULL
        )
    ''')

    # Culturals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS culturals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL
        )
    ''')

    # Industrial Visits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL
        )
    ''')

    # Tech Fest table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS techfest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL
        )
    ''')

    # Contact Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    # Faculty table
    cursor.execute("DROP TABLE IF EXISTS faculty")
    cursor.execute('''
         CREATE TABLE faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            designation TEXT NOT NULL,
            qualification TEXT NOT NULL,
            image TEXT NOT NULL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM faculty")
    count = cursor.fetchone()[0]
    if count == 0:
        faculty_data = [
            ("N. Ambika Devi", "Head of Department", "MCA., M.Phil., B.Ed", "hod.jpg"),
            ("M. Bhanupriya", "Co-ordinator", "MCA., DDM.", "coo.jpg"),
            ("T. Ramya", "Assistant Professor", "M.Sc., M.Phil.", "t.ramya mam.jpg"),
            ("S. Bhanu", "Assistant Professor", "M.Sc., M.Phil.", "bhanu.jpg"),
            ("M. Suvitha", "Assistant Professor", "M.Sc., M.Phil.", "suvi.jpg"),
            ("V. Saranya Devi", "Assistant Professor", "M.A., M.Phil., M.Ed.", "saranya.jpg"),
            ("M. Ramya", "Assistant Professor", "M.Sc., M.Phil.", "m.ramya.jpg"),
            ("K. Mahalakshmi", "Assistant Professor", "MCA", "maha mam.jpg"),
            ("V. Hema", "Assistant Professor", "MCA", "hema.jpg"),
            ("M. Illakiya", "Assistant Professor", "MCA", "ilakiya.jpg")
        ]
        for f in faculty_data:
            cursor.execute(
                "INSERT INTO faculty (name, designation, qualification, image) VALUES (?, ?, ?, ?)",
                 f
            )


    conn.commit()
    conn.close()


# --------------------------
# Alumni functions
# --------------------------

def get_alumni():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, company FROM alumni")
    data = cursor.fetchall()
    conn.close()
    return data

def add_alumni(name, company):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alumni (name, company) VALUES (?, ?)", (name, company))
    conn.commit()
    conn.close()

def delete_alumni(alumni_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alumni WHERE id = ?", (alumni_id,))
    conn.commit()
    conn.close()


# --------------------------
# Events functions
# --------------------------

def get_workshops():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, course, date, title, guest_lecturer FROM workshops")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "course": r[1], "date": r[2], "title": r[3], "guest_lecturer": r[4]} for r in rows]

def get_culturals():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_name FROM culturals")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "event_name": r[1]} for r in rows]

def get_visits():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, location FROM visits")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "location": r[1]} for r in rows]

def get_techfest():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_name FROM techfest")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "event_name": r[1]} for r in rows]

# --------------------------
# Faculty functions
# --------------------------

def get_faculty():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    data = cursor.fetchall()
    conn.close()
    return data

def add_faculty(name, designation, qualification, image_filename):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO faculty (name, designation, qualification, image) VALUES (?, ?, ?, ?)",
        (name, designation, qualification, image_filename)
    )
    conn.commit()
    conn.close()

def delete_faculty(faculty_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faculty WHERE id = ?", (faculty_id,))
    conn.commit()
    conn.close()

# --------------------------
# Routes (Static pages)
# --------------------------

@app.route('/')
def home():
    if 'role' not in session:
        return redirect('/login')  # Not logged in → login page
    role = session.get('role')
    return render_template('index.html', role=role)  # Pass role to template
 # Not logged in → go to login

@app.route('/about')
def about():
    return render_template('about.html')

# Faculty page
@app.route('/faculty')
def faculty():
    faculty_list = get_faculty()
    role = session.get('role', 'student')
    return render_template('faculty.html', faculty_list=faculty_list, role=role)

# Add Faculty (Admin only)
@app.route('/add_faculty', methods=['GET', 'POST'])
def add_faculty_route():
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/faculty')

    if request.method == 'POST':
        name = request.form.get('name')
        designation = request.form.get('designation')
        qualification = request.form.get('qualification')
        image = request.files['image']

        if name and designation and qualification and image:
            image.save(f"static/images/{image.filename}")
            add_faculty(name, designation, qualification, image.filename)
            flash("Faculty added successfully!", "success")
        return redirect('/faculty')

    return render_template('add_faculty.html')

# Delete Faculty (Admin only)
@app.route('/delete_faculty/<int:faculty_id>')
def delete_faculty_route(faculty_id):
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/faculty')

    delete_faculty(faculty_id)
    flash("Faculty deleted successfully!", "success")
    return redirect('/faculty')


@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


# --------------------------
# Events Page
# --------------------------

@app.route('/events')
def events():
    if 'role' not in session:
        flash("Please login first", "error")
        return redirect('/login')

    workshops = get_workshops()
    culturals = get_culturals()
    visits = get_visits()
    techfest = get_techfest()
    role = session.get('role')
    
    return render_template('events.html',
                           workshops=workshops,
                           culturals=culturals,
                           visits=visits,
                           techfest=techfest,
                           role=role)



# --------------------------
# Contact Page
# --------------------------

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    role = session.get('role', 'student')

    if request.method == 'POST' and role == 'student':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if name and email and subject and message:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)",
                (name, email, subject, message)
            )
            conn.commit()
            conn.close()
            flash("Your message has been sent successfully!", "success")
        else:
            flash("Please fill all fields!", "error")
        return redirect('/contact')

    # For admin, fetch all messages
    messages = []
    if role == 'admin':
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contact_messages")
        messages = cursor.fetchall()
        conn.close()

    return render_template('contact.html', role=role, messages=messages)

@app.route('/delete_contact/<int:msg_id>')
def delete_contact(msg_id):
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/contact')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contact_messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    flash("Message deleted successfully!", "success")
    return redirect('/contact')


# --------------------------
# Student Page
# --------------------------

@app.route('/student')
def student():
    alumni_list = get_alumni()
    role = session.get('role', 'student')  # Pass user role
    return render_template('student.html', alumni_list=alumni_list, role=role)



@app.route('/add_alumni', methods=['POST'])
def add_alumni_route():
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/student')

    name = request.form.get('name')
    company = request.form.get('company')
    if name and company:
        add_alumni(name, company)
    return redirect('/student')


@app.route('/delete_alumni/<int:alumni_id>')
def delete_alumni_route(alumni_id):
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/student')

    delete_alumni(alumni_id)
    return redirect('/student')


# --------------------------
# Add / Delete Events (Admin only)
# --------------------------

# Add workshop
@app.route('/add_workshop', methods=['POST'])
def add_workshop():
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/events')

    course = request.form.get('course')
    date = request.form.get('date')
    title = request.form.get('title')
    guest_lecturer = request.form.get('guest_lecturer')
    if course and date and title and guest_lecturer:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO workshops (course, date, title, guest_lecturer) VALUES (?, ?, ?, ?)",
                       (course, date, title, guest_lecturer))
        conn.commit()
        conn.close()
    return redirect('/events')

# Add cultural
@app.route('/add_cultural', methods=['POST'])
def add_cultural():
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/events')

    event_name = request.form.get('event_name')
    if event_name:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO culturals (event_name) VALUES (?)", (event_name,))
        conn.commit()
        conn.close()
    return redirect('/events')

# Add visit
@app.route('/add_visit', methods=['POST'])
def add_visit():
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/events')

    location = request.form.get('location')
    if location:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO visits (location) VALUES (?)", (location,))
        conn.commit()
        conn.close()
    return redirect('/events')

# Add techfest
@app.route('/add_techfest', methods=['POST'])
def add_techfest():
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/events')

    event_name = request.form.get('event_name')
    if event_name:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO techfest (event_name) VALUES (?)", (event_name,))
        conn.commit()
        conn.close()
    return redirect('/events')


# Delete workshop
@app.route('/delete_workshop/<int:workshop_id>')
def delete_workshop(workshop_id):
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/events')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workshops WHERE id = ?", (workshop_id,))
    conn.commit()
    conn.close()
    return redirect('/events')

# Delete cultural
@app.route('/delete_cultural/<int:cultural_id>')
def delete_cultural(cultural_id):
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/events')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM culturals WHERE id = ?", (cultural_id,))
    conn.commit()
    conn.close()
    return redirect('/events')

# Delete visit
@app.route('/delete_visit/<int:visit_id>')
def delete_visit(visit_id):
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/events')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM visits WHERE id = ?", (visit_id,))
    conn.commit()
    conn.close()
    return redirect('/events')

# Delete techfest
@app.route('/delete_techfest/<int:techfest_id>')
def delete_techfest(techfest_id):
    if session.get('role') != 'admin':
        flash("Unauthorized action!", "error")
        return redirect('/events')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM techfest WHERE id = ?", (techfest_id,))
    conn.commit()
    conn.close()
    return redirect('/events')


# --------------------------
# Login / Logout
# --------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "admin":
            session['role'] = 'admin'
            flash("Logged in as Admin!", "success")
            return redirect('/')
        elif username == "student" and password == "student":
            session['role'] = 'student'
            flash("Logged in as Student!", "info")
            return redirect('/')
        else:
            flash("Invalid username or password", "error")
            return redirect('/login')

    return render_template('login.html')




@app.route('/logout')
def logout():
    session.pop('role', None)
    flash("Logged out successfully!", "info")
    return redirect('/login')


# --------------------------
# Run the app
# --------------------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
 
