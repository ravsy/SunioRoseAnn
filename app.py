from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, String
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------------------
# Database Setup
# -------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------------
# Model
# -------------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    section = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    favorite_subject = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database
with app.app_context():
    db.create_all()

last_updated_id = None

# -------------------------------
# Home Page
# -------------------------------
@app.route('/')
def home():
    global last_updated_id
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort_by', '')

    students_query = Student.query

    # 🔍 Search
    if search:
        students_query = students_query.filter(
            (Student.name.ilike(f"%{search}%")) |
            (Student.section.ilike(f"%{search}%")) |
            (cast(Student.grade, String).ilike(f"%{search}%"))
        )

    # 🔄 Sort
    if sort_by == "name":
        students_query = students_query.order_by(Student.name)
    elif sort_by == "grade":
        students_query = students_query.order_by(Student.grade)

    students = students_query.all()
    total_students = Student.query.count()

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Student Management</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            table tbody tr:hover {background-color: #f1f1f1;}
            .highlight {animation: highlight 2s;}
            @keyframes highlight {0% {background-color: #d1e7dd;} 100% {background-color: white;}}
        </style>
    </head>
    <body class="bg-light">
    <div class="container py-5">

        <h1 class="mb-3 text-center text-primary">🎓 Student Management System</h1>
        <h5 class="text-center text-secondary">Total Students: {{ total_students }}</h5>

        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <!-- Search & Sort -->
        <div class="d-flex mb-3 gap-2">
            <form class="d-flex" method="get">
                <input class="form-control me-2" type="search" placeholder="Search name, grade, section" name="search" value="{{ request.args.get('search','') }}">
                <button class="btn btn-outline-primary">Search</button>
            </form>

            <div class="btn-group ms-auto">
                <a href="{{ url_for('home', sort_by='name') }}" class="btn btn-secondary btn-sm">Sort by Name</a>
                <a href="{{ url_for('home', sort_by='grade') }}" class="btn btn-secondary btn-sm">Sort by Grade</a>
            </div>
        </div>

        <!-- Add Student -->
        <div class="card mb-4 p-3 shadow-sm border-primary">
            <h4 class="text-primary">Add Student</h4>
            <form action="{{ url_for('add_student') }}" method="POST">
                <div class="row g-3">
                    <div class="col-md-2"><input type="text" name="name" class="form-control" placeholder="Name" required></div>
                    <div class="col-md-1"><input type="number" step="0.1" name="grade" class="form-control" placeholder="Grade" required></div>
                    <div class="col-md-2"><input type="text" name="section" class="form-control" placeholder="Section" required></div>
                    <div class="col-md-1"><input type="number" name="age" class="form-control" placeholder="Age" required></div>
                    <div class="col-md-2"><input type="text" name="favorite_subject" class="form-control" placeholder="Favorite Subject" required></div>
                    <div class="col-md-2"><button class="btn btn-primary w-100">Add</button></div>
                </div>
            </form>
        </div>

        <!-- Table -->
        <table class="table table-striped table-bordered shadow-sm bg-white">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Grade</th>
                    <th>Section</th>
                    <th>Age</th>
                    <th>Favorite Subject</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>

            <tbody>
                {% for student in students %}
                <tr class="{% if student.id == last_updated_id %}highlight{% endif %}">
                    <form action="{{ url_for('edit_student', student_id=student.id) }}" method="POST">
                        <td>{{ student.id }}</td>
                        <td><input type="text" name="name" value="{{ student.name }}" class="form-control"></td>
                        <td><input type="number" step="0.1" name="grade" value="{{ student.grade }}" class="form-control"></td>
                        <td><input type="text" name="section" value="{{ student.section }}" class="form-control"></td>
                        <td><input type="number" name="age" value="{{ student.age }}" class="form-control"></td>
                        <td><input type="text" name="favorite_subject" value="{{ student.favorite_subject }}" class="form-control"></td>
                        <td>{{ student.created_at.strftime('%Y-%m-%d') }}</td>
                        <td class="d-flex gap-1">
                            <button class="btn btn-success btn-sm">Save</button>
                            <a href="{{ url_for('delete_student', student_id=student.id) }}"
                               class="btn btn-danger btn-sm"
                               onclick="return confirm('Delete this student?');">Delete</a>
                        </td>
                    </form>
                </tr>
                {% endfor %}
            </tbody>
        </table>

    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(template, students=students, last_updated_id=last_updated_id, total_students=total_students)

# -------------------------------
# Add
# -------------------------------
@app.route('/add_student', methods=['POST'])
def add_student():
    global last_updated_id

    new_student = Student(
        name=request.form['name'].strip(),
        grade=float(request.form['grade']),
        section=request.form['section'].strip(),
        age=int(request.form['age']),
        favorite_subject=request.form['favorite_subject'].strip()
    )

    db.session.add(new_student)
    db.session.commit()

    last_updated_id = new_student.id
    flash("Student added successfully!", "success")
    return redirect(url_for('home'))

# -------------------------------
# Edit
# -------------------------------
@app.route('/edit_student/<int:student_id>', methods=['POST'])
def edit_student(student_id):
    global last_updated_id

    student = Student.query.get_or_404(student_id)

    student.name = request.form['name'].strip()
    student.grade = float(request.form['grade'])
    student.section = request.form['section'].strip()
    student.age = int(request.form['age'])
    student.favorite_subject = request.form['favorite_subject'].strip()

    db.session.commit()

    last_updated_id = student.id
    flash("Student updated!", "success")
    return redirect(url_for('home'))

# -------------------------------
# Delete
# -------------------------------
@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    global last_updated_id

    student = Student.query.get_or_404(student_id)

    db.session.delete(student)
    db.session.commit()

    last_updated_id = None
    flash("Student deleted!", "success")
    return redirect(url_for('home'))

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
