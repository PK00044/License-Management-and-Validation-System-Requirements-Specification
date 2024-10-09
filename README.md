## License Management and Validation System Documentation

### 1. Introduction

This application allows users to manage software licenses, providing functionalities for activation, revocation, and license clearing. The system is designed to be user-friendly and efficient, making it easy for administrators to handle licenses for their software products.

### 2. Installation Instructions

To set up the application locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the Project Directory**:
   ```bash
   cd <project-directory>
   ```

3. **Install Required Dependencies**:
   Make sure you have Python installed (version 3.6 or higher). Then run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   Start the Flask server:
   ```bash
   python license_server.py
   ```

5. **Access the Application**:
   Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

### 3. Usage Guide

#### User Registration
1. Navigate to the **Signup** page.
2. Enter a unique username and a secure password.
3. Click on **Sign Up** to create your account.

#### User Login
1. Navigate to the **Login** page.
2. Enter your username and password.
3. Click on **Login** to access the dashboard.

#### License Management
- **Activate License**:
  1. Enter the license key in the provided field.
  2. Click on **Activate** to activate the license.

- **Revoke License**:
  1. Enter the license key in the provided field.
  2. Click on **Revoke** to revoke the license.

- **Clear All Licenses**:
  1. Enter your admin password in the provided field.
  2. Click on **Clear Licenses** to remove all licenses from the system.

### 4. Project Structure

The directory structure of the project is as follows:

```
License Management/
├── license_server.py  # Main Flask application file
├── models.py          # Database models and schema
├── templates/         # Contains HTML templates for rendering
├── static/            # Contains static files like CSS and JavaScript
├── tests/             # Contains unit and integration tests for the application
└── requirements.txt    # Python dependencies
```

### 5. Code Comments

Ensure your code has appropriate comments explaining complex logic or important functionalities. Here are some examples of code comments you should include in your application:

```python
@app.route("/activate", methods=["POST"])
def activate_license():
    data = request.get_json()
    license_key = data.get("license_key")

    # Validate the license key to ensure it's not empty and only contains alphanumeric characters
    if not license_key or not license_key.isalnum():
        return jsonify({"message": "Invalid license key."}), 400  # Bad Request

    # Check if the license already exists in the database
    existing_license = License.query.filter_by(license_key=license_key).first()
    if existing_license:
        return jsonify({"message": "License already activated."}), 400  # Bad Request

    # If license doesn't exist, create a new license entry
    new_license = License(license_key=license_key, status="active")
    db.session.add(new_license)
    db.session.commit()

    return jsonify({"message": "License activated successfully."}), 201  # Created
```

### 6. API Documentation

Here’s a comprehensive list of all API endpoints with their methods, required parameters, and responses:

#### **User Endpoints**

1. **POST /signup**
   - **Description**: Registers a new user.
   - **Request Body**:
     - `username`: Unique username (string).
     - `password`: Password for the user account (string).
   - **Responses**:
     - `201 Created` on successful registration.
     - `400 Bad Request` if the username already exists.

2. **POST /login**
   - **Description**: Authenticates a user.
   - **Request Body**:
     - `username`: User's username (string).
     - `password`: User's password (string).
   - **Responses**:
     - `302 Found` on successful login (redirects).
     - `401 Unauthorized` if credentials are invalid.

#### **License Management Endpoints**

3. **POST /activate**
   - **Description**: Activates a license with a given key.
   - **Request Body**:
     - `license_key`: Key of the license to be activated (string).
   - **Responses**:
     - `201 Created` on successful activation.
     - `400 Bad Request` if the license already exists or is invalid.

4. **POST /revoke**
   - **Description**: Revokes a license with a given key.
   - **Request Body**:
     - `license_key`: Key of the license to be revoked (string).
   - **Responses**:
     - `200 OK` on successful revocation.
     - `404 Not Found` if the license does not exist.

5. **POST /clear_licenses**
   - **Description**: Clears all licenses from the database after password verification.
   - **Request Body**:
     - `password`: Admin password (string).
   - **Responses**:
     - `200 OK` on successful clearing.
     - `403 Forbidden` if the password is incorrect.

6. **GET /licenses**
   - **Description**: Retrieves all licenses.
   - **Responses**:
     - `200 OK` with a list of licenses in JSON format.
     - `204 No Content` if no licenses exist.

### 7. Testing Instructions

To run the unit tests and integration tests, use the following commands:

```bash
# Run unit tests
pytest tests/test_app.py
```
