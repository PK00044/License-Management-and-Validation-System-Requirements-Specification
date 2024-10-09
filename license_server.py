from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask app and database
app = Flask(__name__)
app.secret_key = 'License-Management-and-Validation-System'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

  
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

   
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_key = db.Column(db.String(80), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)


with app.app_context():
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"message": "Resource not found."}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": "An internal error occurred."}), 500



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("User not found. Please register first.")
            return redirect(url_for("login"))

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("admin_dashboard"))

        flash("Invalid credentials. Please try again.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

       
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("signup"))

        
        new_user = User(username=username)
        new_user.set_password(password)  
        db.session.add(new_user)  
        db.session.commit()  
        flash("Signup successful! Please log in.")
        return redirect(url_for("login"))  

    return render_template("signup.html")


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Serve the admin dashboard (only accessible when logged in)
@app.route("/admin")
@login_required
def admin_dashboard():
    return render_template("admin.html")


# Endpoint to retrieve all licenses
@app.route("/licenses", methods=["GET"])
def get_licenses():
    licenses = License.query.all()
    return jsonify([{"license_key": license.license_key, "status": license.status} for license in licenses])


@app.route("/activate", methods=["POST"])
def activate_license():
    data = request.get_json()
    license_key = data.get("license_key")

    # Validate the license key
    if not license_key or not license_key.isalnum():
        return jsonify({"message": "Invalid license key."}), 400  # Bad Request

    # Check if the license already exists
    existing_license = License.query.filter_by(license_key=license_key).first()
    if existing_license:
        return jsonify({"message": "License already activated."}), 400  # Bad Request

    # If license doesn't exist, create a new license
    new_license = License(license_key=license_key, status="active")
    db.session.add(new_license)
    db.session.commit()

    return jsonify({"message": "License activated successfully."}), 201  # Created


# Clear License
@app.route("/clear_licenses", methods=["POST"])
@login_required
def clear_licenses():
    password = request.form.get("password")

    
    if password == 'pratham':
        License.query.delete() 
        db.session.commit()  
        return jsonify({"message": "All licenses cleared successfully."}), 200
    else:
        return jsonify({"message": "Invalid password."}), 403


if __name__ == "__main__":
    app.run(debug=True)
