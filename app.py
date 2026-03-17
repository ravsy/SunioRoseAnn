from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ----------------
# DATABASE SETUP
# ----------------
# Render PostgreSQL Database URL
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://student_user:I3bs3JHp1ZgNrxmTAIVS9SOUsJFXLOd8@dpg-d6sfn74hg0os73f66bt0-a/student_db_x63g"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------
# STUDENT TABLE
# ----------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Float, nullable=False)

# ----------------
# HTML TEMPLATE
# ----------------
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Database</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container mt-5">
    <h1 class="mb-4 text-center">Student Database</h1>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <!-- Add Student Form -->
    <div class="card mb-4 shadow-sm">
        <div class="card-body">
            <form action="{{ url_for('add_student') }}" method="POST" class="row g-3">
                <div class="col-md-6">
                    <input type="text" name="name" class="form-control" placeholder="Student Name" required>
                </div>
                <div class="col-md-4">
                    <input type="number" step="0.01" name="grade" class="form-control" placeholder="Grade" required>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">Add</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Students Table -->
    <div class="card shadow-sm">
        <div class="card-body">
            <table class="table table-hover table-striped">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Grade</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{ student.id }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ "%.2f"|format(student.grade) }}</td>
                    </tr>
                    {% endfor %}
                    {% if students|length == 0 %}
                    <tr>
                        <td colspan="3" class="text-center">No students added yet.</td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ----------------
# ROUTES
# ----------------
@app.route('/')
def index():
    students = Student.query.all()
    return render_template_string(html_template, students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    grade = float(request.form['grade'])
    new_student = Student(name=name, grade=grade)
    db.session.add(new_student)
    db.session.commit()
    flash("Student added successfully!", "success")
    return redirect(url_for('index'))

# ----------------
# CREATE TABLES (ONLY ONCE)
# ----------------
with app.app_context():
    db.create_all()

# ----------------
# RUN APP (RENDER-FRIENDLY)
# ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
