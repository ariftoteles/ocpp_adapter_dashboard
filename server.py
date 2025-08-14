from flask import Flask, request, jsonify, send_from_directory
import os, json, secrets
from dotenv import load_dotenv

# Load .env
load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")

PORT = int(os.getenv("APP_PORT", 8000))
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "terlanjuradmin")
APP_DATABASE_BASE_DIR = os.getenv("APP_DATABASE_BASE_DIR", os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DATABASE_BASE_DIR, "database.json")

TOKENS = set()

# ----------------------
# Serve Halaman Web
# ----------------------
@app.route("/")
def serve_login():
    return send_from_directory(BASE_DIR, "login.html")

@app.route("/dashboard")
def serve_dashboard():
    return send_from_directory(BASE_DIR, "index.html")

# ----------------------
# API: Login
# ----------------------
@app.route("/api/login", methods=["POST"])
def login():
    try:
        creds = request.get_json()
        if creds.get("username") == USERNAME and creds.get("password") == PASSWORD:
            token = secrets.token_hex(16)
            TOKENS.add(token)
            return jsonify({"success": True, "token": token})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ----------------------
# API: Get Data
# ----------------------
@app.route("/api/data", methods=["GET"])
def get_data():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token not in TOKENS:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------
# API: Save Data
# ----------------------
@app.route("/api/save", methods=["POST"])
def save_data():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token not in TOKENS:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        new_data = request.get_json()
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ----------------------
# Jalankan Flask
# ----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
