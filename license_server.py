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

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  


# Define the User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False) ]
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)  

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        return self.role == role


class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  
    domain = db.Column(db.String(100), unique=True, nullable=False)

    users = db.relationship('User', backref='tenant', lazy=True) 

# Define the License model
class License(db.Model):
    __tablename__ = 'licenses'
    id = db.Column(db.Integer, primary_key=True)
    license_key = db.Column(db.String(80), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)  



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


# Login Route
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


# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

       
        role = "user"  
        tenant_id = 1  

        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("signup"))

        # Create new user
        new_user = User(username=username, role=role, tenant_id=tenant_id)
        new_user.set_password(password)  

        # Add and commit to the database
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
@login_required  
def activate_license():
    data = request.get_json()
    license_key = data.get("license_key")

    # Validate the license key
    if not license_key or not license_key.isalnum():
        return jsonify({"message": "Invalid license key."}), 400  

    
    existing_license = License.query.filter_by(license_key=license_key, tenant_id=current_user.tenant_id).first()
    if existing_license:
        return jsonify({"message": "License already activated."}), 400

    
    new_license = License(license_key=license_key, status="active", tenant_id=current_user.tenant_id)
    db.session.add(new_license)
    db.session.commit()

    return jsonify({"message": "License activated successfully."}), 201



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


@app.route("/revoke", methods=["POST"])
@login_required
def revoke_license():
    if not current_user.has_role('admin'):
        return jsonify({"message": "Unauthorized."}), 403  

    data = request.get_json()
    license_key = data.get("license_key")

    
    license_to_revoke = License.query.filter_by(license_key=license_key, tenant_id=current_user.tenant_id).first()
    if not license_to_revoke:
        return jsonify({"message": "License not found."}), 404

    
    license_to_revoke.status = "revoked"
    db.session.commit()

    return jsonify({"message": "License revoked successfully."}), 200


@app.route("/register_tenant", methods=["POST"])
@login_required
def register_tenant():
    if not current_user.has_role('super_admin'): 
        return jsonify({"message": "Unauthorized."}), 403

    data = request.form
    tenant_name = data.get("name")
    tenant_domain = data.get("domain")

    
    existing_tenant = Tenant.query.filter_by(domain=tenant_domain).first()
    if existing_tenant:
        return jsonify({"message": "Tenant domain already exists."}), 400

    
    new_tenant = Tenant(name=tenant_name, domain=tenant_domain)
    db.session.add(new_tenant)
    db.session.commit()

    return jsonify({"message": "Tenant registered successfully."}), 201


@app.route("/api/v1/licenses", methods=["GET"])
@login_required
def api_get_licenses():
    licenses = License.query.filter_by(tenant_id=current_user.tenant_id).all()

    return jsonify([{
        "license_key": license.license_key,
        "status": license.status
    } for license in licenses]), 200


if __name__ == "__main__":
    app.run(debug=True)
