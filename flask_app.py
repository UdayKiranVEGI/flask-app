from flask import Flask, request, jsonify, render_template 
import json
import os
import threading
import sys

app = Flask(__name__)

# Path to the JSON file to be updated
JSON_FILE_PATH = "Ebike_server_data.json"

# Ensure the JSON file exists
if not os.path.exists(JSON_FILE_PATH):
    # Create an empty JSON file if it doesn't exist
    with open(JSON_FILE_PATH, "w") as f:
        json.dump({}, f)

# Thread lock to ensure safe file access
lock = threading.Lock()


@app.route('/update-EBike-json', methods=['POST','GET'])
def update_EBike_json_file():
    try:
        with lock:  # Acquire the lock to ensure safe access to the file
            # Load the existing JSON data from the file
            with open("Ebike_server_data.json", "r") as f:
                existing_data = json.load(f)

            # Get the incoming JSON data from the request
            # incoming_data, Repo = request.get_json(force=True)  # Force parsing of JSON
            data = request.get_json(force=True)  # This returns a dictionary

            incoming_data = data.get("data")  # Extract "data"
            Repo = data.get("Repo")  # Extract "Repo"

            if not incoming_data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            existing_data["E-Bike"][Repo][0].insert(2, incoming_data)

            # Save the updated data back to the file
            with open("Ebike_server_data.json", "w") as f:
                json.dump(existing_data, f, indent=4)

        return jsonify({"message": "JSON file updated successfully", "updated_data": existing_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-EBike-json', methods=['GET'])
def get_EBike_json_data():
    try:
        with lock:  # Acquire the lock to ensure safe access to the file
            # Load the existing JSON data from the file
            with open("Ebike_server_data.json", "r") as f:
                existing_data = json.load(f)
        return jsonify(existing_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def EBike_index():
    with lock:  # Acquire the lock to ensure safe access to the file
        # Load the existing JSON data to display on the HTML page
        with open("Ebike_server_data.json", "r") as f:
            existing_data = json.load(f)
    return render_template("build_links_Ebike.html", data=existing_data)
if __name__ == '__main__':
    # Run the Flask app on all interfaces so it can be accessed in the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
