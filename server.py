# from http.server import SimpleHTTPRequestHandler, HTTPServer
# import json, os, secrets

# PORT = 8000
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(BASE_DIR, "database.json")

# # User & session token (sederhana, tidak persistent)
# USERNAME = "admin"
# PASSWORD = "terlanjuradmin"
# TOKENS = set()

# class Handler(SimpleHTTPRequestHandler):
#     def _set_headers(self, content_type="application/json"):
#         self.send_header("Access-Control-Allow-Origin", "*")
#         self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
#         self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
#         self.send_header("Content-Type", content_type)

#     def do_OPTIONS(self):
#         self.send_response(200)
#         self._set_headers()
#         self.end_headers()

#     def do_GET(self):
#         if self.path == "/api/data":
#             # 🔒 Cek token sebelum kirim data
#             auth = self.headers.get("Authorization", "")
#             token = auth.replace("Bearer ", "")
#             if token not in TOKENS:
#                 self.send_response(401)
#                 self._set_headers()
#                 self.end_headers()
#                 self.wfile.write(b'{"error": "Unauthorized"}')
#                 return

#             try:
#                 with open(DB_PATH, "r", encoding="utf-8") as f:
#                     data = f.read()
#                 self.send_response(200)
#                 self._set_headers()
#                 self.end_headers()
#                 self.wfile.write(data.encode("utf-8"))
#             except Exception as e:
#                 self.send_error(500, f"Error reading database.json: {e}")
#         else:
#             super().do_GET()

#     def do_POST(self):
#         if self.path == "/api/login":
#             try:
#                 length = int(self.headers.get("Content-Length", "0"))
#                 body = self.rfile.read(length).decode("utf-8")
#                 creds = json.loads(body)
#                 if creds.get("username") == USERNAME and creds.get("password") == PASSWORD:
#                     token = secrets.token_hex(16)
#                     TOKENS.add(token)
#                     self.send_response(200)
#                     self._set_headers()
#                     self.end_headers()
#                     self.wfile.write(json.dumps({"success": True, "token": token}).encode())
#                 else:
#                     self.send_response(401)
#                     self._set_headers()
#                     self.end_headers()
#                     self.wfile.write(b'{"success": false, "message": "Invalid credentials"}')
#             except Exception as e:
#                 self.send_error(400, f"Gagal login: {e}")

#         elif self.path == "/api/save":
#             # 🔒 Cek token
#             auth = self.headers.get("Authorization", "")
#             token = auth.replace("Bearer ", "")
#             if token not in TOKENS:
#                 self.send_response(401)
#                 self._set_headers()
#                 self.end_headers()
#                 self.wfile.write(b'{"error": "Unauthorized"}')
#                 return

#             try:
#                 length = int(self.headers.get("Content-Length", "0"))
#                 body = self.rfile.read(length).decode("utf-8")
#                 parsed = json.loads(body)
#                 with open(DB_PATH, "w", encoding="utf-8") as f:
#                     json.dump(parsed, f, indent=2, ensure_ascii=False)
#                 self.send_response(200)
#                 self._set_headers()
#                 self.end_headers()
#                 self.wfile.write(b'{"ok":true}')
#             except Exception as e:
#                 self.send_error(400, f"Gagal menyimpan: {e}")
#         else:
#             self.send_error(404)

# if __name__ == "__main__":
#     os.chdir(BASE_DIR)
#     print(f"Serving at http://localhost:{PORT}")
#     HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


from flask import Flask, request, jsonify, send_from_directory
import os, json, secrets

app = Flask(__name__, static_folder=".", static_url_path="")

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.json")

# User & session token
USERNAME = "admin"
PASSWORD = "terlanjuradmin"
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
