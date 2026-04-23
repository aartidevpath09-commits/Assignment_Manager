from flask import Blueprint, request, jsonify
from db import cursor, conn

assignment_bp = Blueprint("assignment", __name__)

# CREATE
@assignment_bp.route("/assignment", methods=["POST"])
def create_assignment():
    data = request.json

    cursor.execute(
        "INSERT INTO assignments (title,description,due_date,created_by) VALUES (%s,%s,%s,%s)",
        (data["title"], data["description"], data["due_date"], data["teacher_id"])
    )
    conn.commit()

    return jsonify({"message": "Assignment created"})


# READ
@assignment_bp.route("/assignments", methods=["GET"])
def get_assignments():
    cursor.execute("SELECT * FROM assignments")
    return jsonify(cursor.fetchall())


# UPDATE
@assignment_bp.route("/assignment/<int:id>", methods=["PUT"])
def update_assignment(id):
    data = request.json

    cursor.execute(
        "UPDATE assignments SET title=%s, description=%s, due_date=%s WHERE id=%s",
        (data["title"], data["description"], data["due_date"], id)
    )
    conn.commit()

    return jsonify({"message": "Updated"})


# DELETE
@assignment_bp.route("/assignment/<int:id>", methods=["DELETE"])
def delete_assignment(id):
    cursor.execute("DELETE FROM assignments WHERE id=%s", (id,))
    conn.commit()

    return jsonify({"message": "Deleted"})