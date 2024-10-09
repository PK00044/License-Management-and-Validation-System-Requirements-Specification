# License Management and Validation System Documentation

## 1. Introduction

The **License Management and Validation System** is a software solution that allows administrators and users to manage software licenses. This includes the ability to activate, revoke, and clear licenses. The system is designed to be multi-tenant, supporting multiple clients (tenants) with role-based access control, ensuring data isolation between different clients.

### Key Features:
- Multi-tenancy support (multiple clients using the same system with isolated data).
- Role-based access control (e.g., admin, user).
- License management: activation, revocation, and clearing.
- Offline functionality using local storage.
- RESTful API support for tenants to integrate license management into their own systems.

---

## 2. Installation Instructions

### Prerequisites:
- Python 3.6 or higher
- A local SQLite database (or another database supported by SQLAlchemy)
- Flask and required libraries (detailed in `requirements.txt`)

### Steps:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the Project Directory**:
   ```bash
   cd <project-directory>
   ```

3. **Set Up Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

4. **Install Required Dependencies**:
   Install all dependencies using the provided `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   Create a `.env` file in the root of the project directory for environment-specific configurations:
   ```
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   ```

6. **Set Up the Database**:
   Initialize and create the necessary tables for your database.
   ```bash
   python
   >>> from license_server import db
   >>> db.create_all()
   ```

7. **Run the Flask Application**:
   Start the development server:
   ```bash
   python license_server.py
   ```

8. **Access the Application**:
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 3. Project Structure

The structure of your project looks like this:

```
License Management/
├── license_server.py        # Main Flask application file
├── models.py                # Database models and schema for users, licenses, tenants
├── templates/               # HTML templates for front-end pages (login, signup, admin)
│   ├── login.html
│   ├── signup.html
│   ├── admin.html
├── static/                  # Static files like CSS and JavaScript
│   ├── css/
│   
├── tests/                   # Unit and integration tests
│   ├── test_app.py
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
```

### Key Files:
- `license_server.py`: The main Flask app that routes HTTP requests and manages user sessions.
- `models.py`: Defines database models for **User**, **Tenant**, and **License**.
- `templates/`: Contains HTML files for rendering the UI.
- `static/`: Contains static assets like CSS.
- `.env`: Contains environment-specific configurations (e.g., `SECRET_KEY`).
- `requirements.txt`: Lists all the required Python libraries and dependencies.

---

## 4. Multi-Tenancy and Role-Based Access

### Multi-Tenancy:

Multi-tenancy ensures that different tenants (clients) can use the same system but only see and interact with their own data. This is achieved by associating each user and license with a **tenant_id**.

### Role-Based Access Control (RBAC):

RBAC ensures that different types of users (e.g., admin, user) have different levels of access. For example:
- **Admin**: Can activate, revoke, and clear licenses.
- **User**: Can only activate licenses.

#### Example of Multi-Tenant User Model:
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Role: 'admin' or 'user'
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)  # Link user to a tenant
```

---

## 5. API Documentation

The application provides a RESTful API to allow tenants to manage their licenses programmatically.

### Endpoints:

#### 1. **POST /signup**
- **Description**: Registers a new user.
- **Request Body**:
  - `username`: Unique username (string).
  - `password`: Password for the user account (string).
- **Response**:
  - `201 Created` on successful registration.
  - `400 Bad Request` if the username already exists.

#### 2. **POST /login**
- **Description**: Logs in a user.
- **Request Body**:
  - `username`: User's username (string).
  - `password`: User's password (string).
- **Response**:
  - `302 Found` on successful login (redirects to the dashboard).
  - `401 Unauthorized` if the credentials are invalid.

#### 3. **POST /activate**
- **Description**: Activates a license for the current tenant.
- **Request Body**:
  - `license_key`: License key to activate (string).
- **Response**:
  - `201 Created` on successful activation.
  - `400 Bad Request` if the license key is invalid or already exists.

#### 4. **POST /revoke**
- **Description**: Revokes a license for the current tenant (admin only).
- **Request Body**:
  - `license_key`: License key to revoke (string).
- **Response**:
  - `200 OK` on successful revocation.
  - `404 Not Found` if the license does not exist.

#### 5. **POST /clear_licenses**
- **Description**: Clears all licenses for the current tenant (admin only).
- **Request Body**:
  - `password`: Admin password (string).
- **Response**:
  - `200 OK` on successful clearing.
  - `403 Forbidden` if the password is incorrect.

#### 6. **GET /licenses**
- **Description**: Retrieves all licenses for the current tenant.
- **Response**:
  - `200 OK` with a list of licenses (JSON).
  - `204 No Content` if no licenses exist.

---

## 6. Code Walkthrough and Comments

### license_server.py

This is the main application file where all the routes are defined.

#### Example of the Signup Route with Role and Tenant Assignment:
```python
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        role = "user"  # Default role for new users
        tenant_id = 1  # Assign a default tenant or based on logic

        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("signup"))

        # Create new user and hash password
        new_user = User(username=username, role=role, tenant_id=tenant_id)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")
```

---

## 7. Testing Instructions

To ensure your application works as expected, you can run both **unit tests** and **integration tests**.

### Running Unit Tests:

```bash
pytest tests/test_app.py
```

### Running Integration Tests:

```bash
pytest tests/test_integration.py
```

### Example Test Case for License Activation:

```python
def test_license_activation(self):
    # Test activating a license
    self.app.post('/signup', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    self.app.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    response = self.app.post('/activate', json={
        'license_key': 'ABC123'
    })
    self.assertEqual(response.status_code, 201)  # Check for successful activation
```

---

## 8. Additional Notes

- **Multi-Tenancy**: If the application needs to support more than one tenant, ensure that tenant IDs are assigned correctly to all users and licenses.
- **Security**: Always ensure that sensitive data, such as passwords, is securely hashed using methods like `generate_password_hash()`.
- **Role-Based Access**: Role-based access is implemented using the `role` field in the `User` model. Modify it to assign different access levels (e.g., admin vs. user).

---
