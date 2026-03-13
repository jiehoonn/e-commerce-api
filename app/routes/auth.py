from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.utils.file_storage import load_user_data, write_user_data

import hashlib
from datetime import datetime, timezone

# ================= HELPER FUNCTIONS =================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def find_next_id(data):
    if not data:
        return "1"
    
    next_id = len(data) + 1

    while str(next_id) in data:
        next_id += 1

    return str(next_id)

# ====================================================

auth_bp = Blueprint("auth", __name__)

# 1. Auth
#     ```bash
#     POST /api/auth/register
#     POST /api/auth/login
#     ```

# {
#     "1" : {
#         "id": 1,
#         "username": "jiehoon",
#         "password": "hashed_password",
#         "createdAt": "2026-03-11T00:00:00Z"
#     },
# }

# POST /api/auth/register
@auth_bp.route("/auth/register", methods=["POST"])
def register_user():
    new_user_info = request.get_json()  # Should contain username & password

    if "username" not in new_user_info or "password" not in new_user_info:
        return jsonify({"error: Username and Password are required."}), 400
    
    try:
        # Load the Data:
        user_database = load_user_data()

        # Find next available User ID:
        next_id = find_next_id(user_database)
        
        # Store new registered user data and prepare for insertion
        username, password = new_user_info["username"], hash_password(new_user_info["password"])
        now = datetime.now(timezone.utc).isoformat()

        # Format new user entry
        user_database[str(next_id)] = {
            "id": next_id,
            "username": username,
            "password": password,
            "createdAt": now
        }

        write_user_data(user_database)
        return jsonify(user_database[str(next_id)]), 201
    except Exception as e:
        return jsonify({"error": f"An unexpected error has occurred: {e}"}), 500

@auth_bp.route("/auth/login", methods=["POST"])
def login_user():
    # 1. get username and password from request body
    user_details = request.get_json()

    # 2. validate they exist
    if not user_details:
        return jsonify({"error": "No data provided"}), 400

    if "username" not in user_details or "password" not in user_details:
        return jsonify({"error: Username and Password are required."}), 400
    
    username, password = user_details["username"], hash_password(user_details["password"])
    
    try:
        # 3. load users from file
        users_data = load_user_data()
    
        # 4. find the user by username
        found_user = None
        for user in users_data.values():
            if user["username"] == username:
                found_user = user
                break

        # 5. if not found → 401
        # 6. hash the incoming password and compare to stored hash
        # 7. if no match → 401
        if not found_user or found_user["password"] != password:
            return jsonify({"error": "Verify your login credentials are correct."}), 401
        
        # 8. create token with create_access_token(identity=user["id"])
        token = create_access_token(identity=found_user["id"])

        # 9. return token → 200
        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error has occurred while logging in: {e}"}), 500