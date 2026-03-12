from flask import Flask, request, redirect, url_for, flash, render_template_string

app = Flask(__name__)
app.secret_key = "supersecretkey"

# In-memory student data
students = [
    {"id": 1, "name": "Juan", "grade": 10, "section": "Zechariah", "age": 15, "favorite_subject": "Math"},
    {"id": 2, "name": "Maria", "grade": 9, "section": "Gabriel", "age": 14, "favorite_subject": "Science"}
]

# Keep track of last added/edited student for highlighting
last_updated_id = None

@app.route('/')
def home():
    global last_updated_id
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
        <h1 class="mb-4 text-center text-primary">Student Management</h1>

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
        <div class="card mb-4 p-3 shadow-sm border-primary">
            <h4 class="text-primary">Add New Student</h4>
            <form action="{{ url_for('add_student') }}" method="POST">
                <div class="row g-3">
                    <div class="col-md-2"><input type="text" name="name" class="form-control" placeholder="Name"></div>
                    <div class="col-md-1"><input type="number" name="grade" class="form-control" placeholder="Grade"></div>
                    <div class="col-md-2"><input type="text" name="section" class="form-control" placeholder="Section"></div>
                    <div class="col-md-1"><input type="number" name="age" class="form-control" placeholder="Age"></div>
                    <div class="col-md-2"><input type="text" name="favorite_subject" class="form-control" placeholder="Favorite Subject"></div>
                    <div class="col-md-2"><button type="submit" class="btn btn-primary w-100">Add Student</button></div>
                </div>
            </form>
        </div>

        <!-- Student Table -->
        <table class="table table-striped table-bordered shadow-sm bg-white">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Grade</th>
                    <th>Section</th>
                    <th>Age</th>
                    <th>Favorite Subject</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for student in students %}
                <tr class="{% if student.id == last_updated_id %}highlight{% endif %}">
                    <form action="{{ url_for('edit_student', student_id=student.id) }}" method="POST">
                    <td>{{ student.id }}</td>
                    <td><input type="text" name="name" value="{{ student.name }}" class="form-control"></td>
                    <td><input type="number" name="grade" value="{{ student.grade }}" class="form-control"></td>
                    <td><input type="text" name="section" value="{{ student.section }}" class="form-control"></td>
                    <td><input type="number" name="age" value="{{ student.age }}" class="form-control"></td>
                    <td><input type="text" name="favorite_subject" value="{{ student.favorite_subject }}" class="form-control"></td>
                    <td class="d-flex gap-1">
                        <button type="submit" class="btn btn-success btn-sm">Save</button>
                        <a href="{{ url_for('delete_student', student_id=student.id) }}" 
                           class="btn btn-danger btn-sm" 
                           onclick="return confirm('Are you sure you want to delete this student?');">Delete</a>
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
    return render_template_string(template, students=students, last_updated_id=last_updated_id)

# -------------------------------
# Add student
# -------------------------------
@app.route('/add_student', methods=['POST'])
def add_student():
    global last_updated_id
    name = request.form.get("name")
    grade = request.form.get("grade")
    section = request.form.get("section")
    age = request.form.get("age")
    favorite_subject = request.form.get("favorite_subject")

    if not all([name, grade, section, age, favorite_subject]):
        flash("All fields are required!", "danger")
        return redirect(url_for('home'))

    new_id = max([s["id"] for s in students]) + 1 if students else 1
    students.append({
        "id": new_id,
        "name": name,
        "grade": int(grade),
        "section": section,
        "age": int(age),
        "favorite_subject": favorite_subject
    })
    last_updated_id = new_id
    flash(f"Student {name} added successfully!", "success")
    return redirect(url_for('home'))

# -------------------------------
# Edit student
# -------------------------------
@app.route('/edit_student/<int:student_id>', methods=['POST'])
def edit_student(student_id):
    global last_updated_id
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        flash("Student not found!", "danger")
        return redirect(url_for('home'))

    student["name"] = request.form.get("name")
    student["grade"] = int(request.form.get("grade"))
    student["section"] = request.form.get("section")
    student["age"] = int(request.form.get("age"))
    student["favorite_subject"] = request.form.get("favorite_subject")
    last_updated_id = student_id
    flash(f"Student {student['name']} updated successfully!", "success")
    return redirect(url_for('home'))

# -------------------------------
# Delete student
# -------------------------------
@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    global students, last_updated_id
    student = next((s for s in students if s["id"] == student_id), None)
    if student:
        students = [s for s in students if s["id"] != student_id]
        flash(f"Student {student['name']} deleted successfully!", "success")
    else:
        flash("Student not found!", "danger")
    last_updated_id = None
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
