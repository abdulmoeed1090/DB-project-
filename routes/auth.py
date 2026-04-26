from flask import Blueprint, jsonify, request
from db import query
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    rows = query(
        "SELECT UserID, Name, RoleID FROM Users WHERE Email = ? AND PasswordHash = ? AND IsActive = 1",
        (data['email'], data['password'])
    )
    if not rows:
        return jsonify({"error": "Invalid credentials"}), 401
    user = rows[0]
    token = create_access_token(identity=str(user['UserID']))
    return jsonify({"token": token, "user": user})