from flask import Blueprint, request, jsonify, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import user
from db_config import db

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")  # Render the login form for GET
    elif request.method == "POST":
        data = request.json
        users = user.query.filter_by(email=data["email"]).first()
        if users and check_password_hash(users.password, data["password"]):
            session["user_id"] = users.id
            session["user_name"] = users.name
            session["email"] = users.email
            return jsonify({"message": "Login successful!"}), 200
        return jsonify({"message": "Invalid credentials"}), 401


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")  # Render the registration form for GET
    elif request.method == "POST":
        data = request.json
        hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
        new_user = user(
            name=data["username"], email=data["email"], password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id
        session["user_name"] = new_user.name
        session["email"] = new_user.email
        return jsonify({"message": "User registered successfully!"}), 201

@auth.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return render_template("login.html"), 200
