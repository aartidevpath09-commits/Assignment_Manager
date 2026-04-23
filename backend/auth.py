from flask import Blueprint, request, jsonify
from db import cursor, conn
import bcrypt
from auth_utils import generate_token

auth_bp = Blueprint("auth", __name__)

# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)",
        (data["name"], data["email"], hashed, data["role"])
    )
    conn.commit()

    return jsonify({"message": "Registered successfully"})


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    cursor.execute("SELECT * FROM users WHERE email=%s", (data["email"],))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(data["password"].encode(), user[3].encode()):
        token = generate_token(user)

        return jsonify({
            "token": token,
            "id": user[0],
            "name": user[1],
            "role": user[4]
        })

    return jsonify({"message": "Invalid credentials"}), 401