from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.file_storage import load_data, write_data

from datetime import datetime, timezone

# Helper Functions
payments_file = "payments.json"
cartfile = "cart.json"

def get_next_payment_id(user_payment_history):
    if not user_payment_history:
        return 1
    next_id = len(user_payment_history) + 1
    while str(next_id) in user_payment_history:
        next_id += 1
    return next_id
# =============================

# 4. Payments
#     ```bash
#     POST /api/payments/checkout
#     GET  /api/payments
#     ```

# 4. Payments
#     ```JSON
#     {
#         "1": { <----- User ID
#           "1": { <---- Payment ID
#                "id": 1,
#                "user_id": 1,
#                "cart": {
#                    "1" : {
#                        "product_id": 1,
#                        "quantity" : 5,
#                        "price": 29.99
#                    }
#                },
#                "total": 149.95,
#                "status": "completed",
#                "createdAt": "2026-03-11T00:00:00Z"
#             },
#           "2": {
#               ...
#             }
#         }
#     }
#     ```

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/payments/checkout", methods=["POST"])
@jwt_required()
def post_payment():
    user_id = str(get_jwt_identity())

    # "cart": {
    #     "1": {
    #         "product_id": "1",
    #         "quantity": 2,
    #         "price": 7.98
    #     },
    #     "2": {
    #         "product_id": "2",
    #         "quantity": 4,
    #         "price": 31.96
    #     }
    # },
    # "totalPrice": 39.94

    try:
        payments_data = load_data(payments_file)
        cart_data = load_data(cartfile)

        if user_id not in cart_data:
            return jsonify({"error": "User has no cart to checkout"}), 400

        status_type = ["pending", "completed", "failed"]
        now = datetime.now(timezone.utc).isoformat()
        cart = cart_data[user_id]["cart"]
        total = cart_data[user_id]["totalPrice"]

        # No recorded history of user making a purchase
        if user_id not in payments_data:
            next_payments_id = 1

            payments_data[user_id] = {
                str(next_payments_id): {
                    "id": next_payments_id,
                    "user_id": user_id,
                    "cart": cart,
                    "total": total,
                    "status": status_type[0],
                    "createdAt": now
                }
            }
        else:
            next_payments_id = get_next_payment_id(payments_data[user_id])

            payments_data[user_id][next_payments_id] = {
                    "id": next_payments_id,
                    "user_id": user_id,
                    "cart": cart,
                    "total": total,
                    "status": status_type[0],
                    "createdAt": now
                }
            
        write_data(payments_data, payments_file)

        # After writing payment data:
        
        if user_id in cart_data:
            del cart_data[user_id]
            write_data(cart_data, cartfile)

        return jsonify({"message": "payment submitted", "payment": payments_data[user_id]}), 201
    except Exception as e:
        return jsonify({"error": f"An unexpected error has occurred {e}"}), 500

@payments_bp.route("/payments", methods=["GET"])
@jwt_required()
def get_payment():
    user_id = str(get_jwt_identity())

    try:
        payments_data = load_data(payments_file)
        users_data = load_data("users.json")
        
        if user_id not in payments_data:
            return jsonify({"error": f"No payment history recorded for user {users_data[user_id]['username']}"}), 404
        
        return jsonify(payments_data[user_id]), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error has occurred {e}"}), 500