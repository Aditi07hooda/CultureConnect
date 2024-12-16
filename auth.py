from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import user
from db_config import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = user(name=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.id
    return jsonify({"message": "User registered successfully!"}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    users = user.query.filter_by(email=data['email']).first()
    if users and check_password_hash(users.password, data['password']):
        session['user_id'] = users.id
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"message": "Invalid credentials"}), 401