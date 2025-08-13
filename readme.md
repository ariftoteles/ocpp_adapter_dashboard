## 📂 Folder Structure
```
project/
│
├── database.json        # Simple database
├── index.html           # Main dashboard page
├── login.html           # Login page
├── script.js            # JavaScript for frontend
├── style.css            # CSS for styling
├── server.py            # Flask server + protected API
├── requirements.txt     # Python dependencies
└── venv/                # Virtual environment
```

---

## 🚀 Installation
1. **Clone or move the project to Raspberry Pi / PC**
   ```bash
   git clone <repository>
   cd dashboard_ocpp_adapter
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - **Windows (CMD)**
     ```bash
     venv\Scripts\activate
     ```
   - **Windows (PowerShell)**
     ```powershell
     venv\Scripts\Activate.ps1
     ```
   - **Linux / Mac / Raspberry Pi**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📦 `requirements.txt` content
```
flask
```
> You can auto-generate this file with:
> ```bash
> pip freeze > requirements.txt
> ```

---

## ▶️ Run the Server
Make sure the virtual environment is active, then run:
```bash
python server.py
```
The server will run at:
```
http://localhost:8000
```
or accessible from another device on the same network:
```
http://<RASPBERRY_PI_IP>:8000
```

---

## 🔑 Login
- **Username**: `admin`
- **Password**: `terlanjuradmin`

A token will be stored in the browser after login, used for accessing `GET /api/data` and `POST /api/save`.

---

## ⚙️ API Endpoints
| Method | Endpoint      | Description                  | Protected |
|--------|--------------|------------------------------|-----------|
| POST   | `/api/login` | Login and retrieve a token   | ❌        |
| GET    | `/api/data`  | Retrieve database.json data  | ✅        |
| POST   | `/api/save`  | Save changes to the database | ✅        |

**Note:** Protected endpoints require an Authorization header:
```
Authorization: Bearer <token>
```