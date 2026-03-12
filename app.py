from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Sample in-memory student data
students = [
    {
        "id": 1,
        "name": "Juan",
        "grade": 10,
        "section": "Zechariah",
        "age": 15,
        "favorite_subject": "Math"
    },
    {
        "id": 2,
        "name": "Maria",
        "grade": 9,
        "section": "Gabriel",
        "age": 14,
        "favorite_subject": "Science"
    }
]

# -------------------------------
# Home route
# -------------------------------
@app.route('/')
def home():
    return "Welcome to my first API!", 200

# -------------------------------
# GET students
# -------------------------------
@app.route('/student', methods=['GET'])
def get_student():
    student_id = request.args.get('id')
    if student_id:
        try:
            student_id = int(student_id)
        except ValueError:
            return jsonify({"error": "Invalid student ID"}), 400
        student = next((s for s in students if s["id"] == student_id), None)
        if student:
            return jsonify(student), 200
        else:
            return jsonify({"error": "Student not found"}), 404
    else:
        return jsonify(students), 200

# -------------------------------
# POST new student
# -------------------------------
@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    required_fields = ["name", "grade", "section", "age", "favorite_subject"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing fields. Required: {required_fields}"}), 400
    new_id = max([s["id"] for s in students]) + 1 if students else 1
    new_student = {"id": new_id, **data}
    students.append(new_student)
    return jsonify(new_student), 201

# -------------------------------
# PUT update student
# -------------------------------
@app.route('/student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    # Update only fields provided
    for key in ["name", "grade", "section", "age", "favorite_subject"]:
        if key in data:
            student[key] = data[key]
    return jsonify(student), 200

# -------------------------------
# DELETE student
# -------------------------------
@app.route('/student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    global students
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    students = [s for s in students if s["id"] != student_id]
    return jsonify({"message": f"Student {student_id} deleted"}), 200

# -------------------------------
# Personalized hello
# -------------------------------
@app.route('/hello', methods=['GET'])
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({"message": f"Hello, {name}!"}), 200

# -------------------------------
# Run the app
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
