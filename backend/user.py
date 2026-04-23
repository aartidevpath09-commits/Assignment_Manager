from flask import Blueprint, jsonify
from db import cursor

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
def get_users():
    cursor.execute("SELECT id,name,email,role FROM users")
    users = cursor.fetchall()
    return jsonify(users)