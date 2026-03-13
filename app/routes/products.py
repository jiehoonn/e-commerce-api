from flask import Blueprint, request, jsonify
from app.utils.file_storage import load_data, write_data
from datetime import datetime, timezone

products_bp = Blueprint("products", __name__)

datafile = "products.json"

# ================= HELPER FUNCTIONS =================

def find_next_id(data):
    if not data:
        return "1"
    next_id = len(data) + 1
    while str(next_id) in data:
        next_id += 1
    return str(next_id)

# ====================================================

@products_bp.route("/products", methods=["GET"])
def retrieve_products():
    try:
        data = load_data(datafile)
        return jsonify(list(data.values())), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@products_bp.route("/products/<int:id>", methods=["GET"])
def retrieve_product(id):
    try:
        data = load_data(datafile)
        if str(id) not in data:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(data[str(id)]), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@products_bp.route("/products", methods=["POST"])
def add_product():
    new_product = request.get_json()

    if not new_product:
        return jsonify({"error": "No data provided"}), 400
    if "name" not in new_product or "price" not in new_product or "quantity" not in new_product:
        return jsonify({"error": "Name, price, and quantity are required"}), 400

    try:
        price = float(new_product["price"])
        quantity = int(new_product["quantity"])
        if price <= 0 or quantity < 0:
            return jsonify({"error": "Price must be positive and quantity cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Price must be a number and quantity must be an integer"}), 400

    try:
        data = load_data(datafile)
        next_id = find_next_id(data)
        now = datetime.now(timezone.utc).isoformat()

        product = {
            "id": next_id,
            "name": new_product["name"],
            "price": price,
            "quantity": quantity,
            "createdAt": now
        }

        data[next_id] = product
        write_data(data, datafile)
        return jsonify(data[next_id]), 201
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@products_bp.route("/products/<int:id>", methods=["PATCH"])
def update_product(id):
    update_data = request.get_json()

    if not update_data:
        return jsonify({"error": "No data provided"}), 400

    valid_properties = ["name", "price", "quantity"]
    for prop in update_data:
        if prop not in valid_properties:
            return jsonify({"error": f"Invalid property: {prop}"}), 400

    try:
        data = load_data(datafile)
        if str(id) not in data:
            return jsonify({"error": "Product not found"}), 404

        for prop in update_data:
            data[str(id)][prop] = update_data[prop]

        write_data(data, datafile)
        return jsonify(data[str(id)]), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@products_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    try:
        data = load_data(datafile)
        if str(id) not in data:
            return jsonify({"error": "Product not found"}), 404

        del data[str(id)]
        write_data(data, datafile)
        return jsonify({"message": "Product successfully deleted"}), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500