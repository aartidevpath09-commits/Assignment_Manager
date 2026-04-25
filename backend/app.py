from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_connection
from models import create_tables
from flask import send_from_directory

import bcrypt
import jwt
import datetime
import os
from werkzeug.utils import secure_filename
import threading
from notifier import start_scheduler
import time



app = Flask(__name__)
CORS(app)

# SECRET KEY for JWT
SECRET_KEY = "mysecretkey"

# Upload config
UPLOAD_FOLDER = "uploads"

# if uploads exists but is file → delete
if os.path.exists(UPLOAD_FOLDER) and not os.path.isdir(UPLOAD_FOLDER):
    os.remove(UPLOAD_FOLDER)

# create folder safely
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

create_tables()


# =========================
# 🔔 START NOTIFIER (BACKGROUND THREAD)
# =========================
threading.Thread(target=start_scheduler, daemon=True).start()

# =========================
# AUTH (REGISTER + LOGIN)
# =========================

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({"error": "All fields required"}), 400

    # 🔐 hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
    "INSERT INTO users (name, password, role) VALUES (%s, %s, %s)",
     (username, hashed.decode('utf-8'), role)
       )
    
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "User Registered"})


@app.route('/login', methods=['POST'])
def login():
    data = request.json

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE name=%s AND role=%s",
        (username, role)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    # ❌ user not found
    if not user:
        return jsonify({"message": "Invalid Credentials"}), 401

    # ✅ correct password index = 3
    if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):

        token = jwt.encode({
           "user_id": user[0],
           "username": username,
           "role": role,
           "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "message": "Login Success",
            "token": token,
            "role": role,
            "user_id": user[0]
        })

    return jsonify({"message": "Invalid Credentials"}), 401

# =========================
# ASSIGNMENT CRUD (Teacher)
# =========================

# CREATE
@app.route('/assignments', methods=['POST'])
def add_assignment():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO assignments (title, description, due_date) VALUES (%s, %s, %s)",
        (data['title'], data['subject'], data['due_date'])
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Assignment Added"})


# READ
@app.route('/assignments', methods=['GET'])
def get_assignments():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, title, description, due_date FROM assignments")

    rows = cur.fetchall()

    cur.close()
    conn.close()

    assignments = []

    for r in rows:
        assignments.append({
            "id": r[0],
            "title": r[1],
            "subject": r[2],  
            "due_date": str(r[3])
        })

    return jsonify(assignments)
# UPDATE
@app.route('/assignments/<int:id>', methods=['PUT'])
def update_assignment(id):
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE assignments SET title=%s, subject=%s, due_date=%s WHERE id=%s",
        (data['title'], data['subject'], data['due_date'], id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Assignment Updated"})


# DELETE
@app.route('/assignments/<int:id>', methods=['DELETE'])
def delete_assignment(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM assignments WHERE id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Assignment Deleted"})


# =========================
# STUDENT SUBMIT
# =========================

@app.route('/submit', methods=['POST'])
def submit_assignment():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO submissions (assignment_id, student_id, file_url, file_name) VALUES (%s, %s, %s, %s)",
        (data['assignment_id'], data['student_id'], data['file_url'], data['file_name'])
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Submitted"})


# =========================
# 📁 FILE UPLOAD (PDF)
# =========================



@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # ✅ file check
        if 'file' not in request.files:
            return jsonify({"message": "No file uploaded"}), 400

        file = request.files['file']

        if file.filename == "":
            return jsonify({"message": "No selected file"}), 400

        # ✅ form data check
        assignment_id = request.form.get("assignment_id")
        student_id = request.form.get("student_id")

        if not assignment_id or not student_id:
            return jsonify({"message": "Missing assignment_id or student_id"}), 400

        # ✅ convert to int (important)
        assignment_id = int(assignment_id)
        student_id = int(student_id)

        # ✅ unique filename
        filename = str(int(time.time())) + "_" + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # ✅ save file
        file.save(filepath)

        print("FILE SAVED:", filepath)
        print("Assignment ID:", assignment_id)
        print("Student ID:", student_id)

        # ✅ DB insert
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO submissions (assignment_id, student_id, file_url, file_name) VALUES (%s, %s, %s, %s)",
            (assignment_id, student_id, filepath, filename)
        )
        
        cur.execute(
    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, %s)",
    (student_id, "Assignment uploaded successfully", False)
        )


        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "File Uploaded Successfully"}), 200

    except Exception as e:
        print("UPLOAD ERROR:", e)   # 🔥 terminal मध्ये exact error दिसेल
        return jsonify({"message": "Upload failed"}), 500



@app.route('/submissions', methods=['GET'])
def get_submissions():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, assignment_id, file_name FROM submissions")
    rows = cur.fetchall()

    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "assignment_id": r[1],
            "file_name": r[2]
        })

    cur.close()
    conn.close()

    return jsonify(data)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/notifications/<int:user_id>')
def get_notifications(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT message, created_at FROM notifications WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )

    rows = cur.fetchall()

    data = []
    for r in rows:
        data.append({
            "message": r[0],
            "time": str(r[1])
        })

    cur.close()
    conn.close()

    return jsonify(data)

# =========================

@app.route('/')
def home():
    return {"message": "Backend Running 🚀"}


if __name__ == "__main__":
    app.run(debug=True)