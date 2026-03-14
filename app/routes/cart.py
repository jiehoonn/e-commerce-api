from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.file_storage import load_data, write_data

cart_bp = Blueprint("cart", __name__)

cartfile = "cart.json"
productfile = "products.json"

# ================= HELPER FUNCTIONS =================

def calculate_total(cart):
    return round(sum(item["price"] for item in cart.values()), 2)

# ====================================================

# 3. Shopping Cart:
#     ```JSON
#     {
#         "1" : {
#             "cart": {
#                 "1" : {
#                     "product_id": 1,
#                     "quantity" : 5,
#                     "price": 29.99
#                 },
#                 "2" : {
#                     "product_id": 2,
#                     "quantity" : 2,
#                     "price": 13.99
#                 },
#             },
#             "totalPrice": 177.93
#         }
#     }
#     ```

# 3. Cart
# GET    /api/cart              → get current user's cart (user_id from token)
# POST   /api/cart              → add item to current user's cart
# PUT    /api/cart/<product_id> → update item quantity in current user's cart
# DELETE /api/cart/<product_id> → remove item from current user's cart
# DELETE /api/cart              → clear current user's entire cart

@cart_bp.route("/cart", methods=["GET"])
@jwt_required()
def get_cart():
    user_id = str(get_jwt_identity())  # pulled from token, not URL
    
    data = load_data(cartfile)
    
    if user_id not in data:
        return jsonify({"cart": {}, "totalPrice": 0}), 200
    
    return jsonify(data[user_id]), 200

@cart_bp.route("/cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = str(get_jwt_identity())

    added_product = request.get_json()

    if not added_product:
        return jsonify({"error": "No data provided"}), 400
    if "product_id" not in added_product or "quantity" not in added_product:
        return jsonify({"error": "product_id and quantity are required"}), 400

    product_id = str(added_product["product_id"])
    quantity = int(added_product["quantity"])

    # Validate product exists in catalog
    products_data = load_data(productfile)
    if product_id not in products_data:
        return jsonify({"error": "Product not found in catalog"}), 404

    try:
        cart_data = load_data(cartfile)

        # Initialize cart if user has none yet
        if user_id not in cart_data:
            cart_data[user_id] = {"cart": {}, "totalPrice": 0}

        # If product already in cart, update quantity and price
        if product_id in cart_data[user_id]["cart"]:
            cart_data[user_id]["cart"][product_id]["quantity"] += quantity
            cart_data[user_id]["cart"][product_id]["price"] = round((
                cart_data[user_id]["cart"][product_id]["quantity"] * 
                float(products_data[product_id]["price"])
            ), 2)
        # Otherwise add it fresh
        else:
            cart_data[user_id]["cart"][product_id] = {
                "product_id": product_id,
                "quantity": quantity,
                "price": round(float(products_data[product_id]["price"]) * quantity, 2)
            }

        # Recalculate total
        cart_data[user_id]["totalPrice"] = calculate_total(cart_data[user_id]["cart"])

        write_data(cart_data, cartfile)
        return jsonify(cart_data[user_id]), 201

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
    
@cart_bp.route("/cart/<string:product_id>", methods=["PATCH"])
@jwt_required()
def update_quantity(product_id):
    user_id = str(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided."}), 400
    if "quantity" not in data:
        return jsonify({"error": "Quantity field is required"}), 400
    
    cart_data = load_data(cartfile)
    products_data = load_data(productfile)

    if user_id not in cart_data:
        return jsonify({"error": "User has no cart"}), 404

    if product_id not in cart_data[user_id]["cart"]:
        return jsonify({"error": "Product does not exist in user's cart."}), 404
    
    quantity = data["quantity"]

    try:
        quantity = int(data["quantity"])
        if quantity <= 0:
            return jsonify({"error": "Quantity must be a positive number"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Quantity must be a valid integer"}), 400
    
    try:
        cart_data[user_id]["cart"][product_id]["quantity"] = int(quantity)
        cart_data[user_id]["cart"][product_id]["price"] = round(float(products_data[product_id]["price"]) * int(quantity), 2)
        cart_data[user_id]["totalPrice"] = calculate_total(cart_data[user_id]["cart"])

        write_data(cart_data, cartfile)

        return jsonify(cart_data[user_id]["cart"]), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error has occurred {e}"}), 500

@cart_bp.route("/cart/<string:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    user_id = str(get_jwt_identity())

    cart_data = load_data(cartfile)

    if user_id not in cart_data:
        return jsonify({"error": "User has no cart"}), 404

    if product_id not in cart_data[user_id]["cart"]:
        return jsonify({"error": "Product does not exist in user's cart."}), 404
    
    try:
        del cart_data[user_id]["cart"][product_id]

        cart_data[user_id]["totalPrice"] = calculate_total(cart_data[user_id]["cart"])

        write_data(cart_data, cartfile)

        return jsonify(cart_data[user_id]["cart"]), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error has occurred {e}"}), 500

@cart_bp.route("/cart", methods=["DELETE"])
@jwt_required()
def clear_cart():
    user_id = str(get_jwt_identity())

    cart_data = load_data(cartfile)

    if user_id not in cart_data:
        return jsonify({"error": "User has no cart"}), 404
    
    try:
        del cart_data[user_id]

        write_data(cart_data, cartfile)

        return "", 204
    except Exception as e:
        return jsonify({"error": f"An unexpected error has occurred {e}"}), 500