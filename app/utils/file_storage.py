import json
import os

# ===================== FILEPATH =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "data")

filename = os.path.join(DATA_DIR, "users.json")

# ================= HELPER FUNCTIONS =================

def load_user_data():
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if not os.path.exists(filename):
            with open(filename, mode='w') as f:
                json.dump({}, f)

        with open(filename, mode='r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        # Handle the case where the file does not exist
        print(f"Error: The file '{filename}' was not found.")
        return {}  # Or return an empty dictionary, e.g., return {}
    except json.JSONDecodeError:
        # Handle the case where the file has invalid JSON syntax
        print(f"Error: Failed to decode JSON from the file '{filename}'. Check file format.")
        return {}
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"An unexpected error occurred: {e}")
        return {}
    
def write_user_data(data: dict):
    try:
        with open(filename, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except TypeError as e:
        # Handle errors if the Python object is not JSON serializable
        print(f"Error: The object is not JSON serializable. Details: {e}")
        # Optional: Clean up the file if a partial write occurred
        if os.path.exists(filename) and os.path.getsize(filename) == 0:
            os.remove(filename)
    except PermissionError:
        # Handle errors related to file permissions
        print(f"Error: Permission denied when writing to {filename}.")
    except IOError as e:
        # Catch other I/O related errors
        print(f"Error: An I/O error occurred: {e}")
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"An unexpected error occurred: {e}")
    else:
        # This block executes if the try block finishes without an exception
        print(f"Successfully wrote data to {filename}")