from flask import Flask, request, jsonify
import jwt
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os, requests, json
from utils import *


load_dotenv()

app = Flask(__name__)

# Read ENV vars
SECRET = os.environ.get('JWT_SECRET')
JWT_HOST = os.environ.get('JWT_HOST')
JWT_PORT = os.environ.get('JWT_PORT')


def request_token(**kwargs):
    response = requests.post(f'http://{JWT_HOST}:{JWT_PORT}', data=kwargs)
    return json.loads(response.text), response.status_code


def request_validation(headers):
    response = requests.get(f'http://{JWT_HOST}:{JWT_PORT}', headers=headers)
    return json.loads(response.text), response.status_code


def validate_password(password):
    """Password Validator"""
    reg = r"\b^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$\b"
    return bool(reg.match(password))

@app.route('/users', methods=['POST'])
def new_user():
    try:
        user = request.json
        username, password = user['username'], user['password']
        if not validate_password(password):
            return jsonify({"Error": "Password format is invalid"}), 400
    except:
        return jsonify({"Error": "Username and/or password not found in request"}), 400
    
    try:
        result, status = create_user(username, password)
        if status:
            return jsonify({'Message': 'Sign up successful'}), 200 
        if type(result) is dict:
            return jsonify({'Error': 'Username already exists'}), 409
        return jsonify({'Error': 'DB failed to execute query'}), 500
    except:
        return jsonify({'Error': 'Something went wrong'}), 500


@app.route('/users/login', methods=['POST'])
def login():
    try:
        user = request.json
        username, password = user['username'], user['password']
    except:
        return jsonify({"Error": "Username and/or password not found in request"}), 400
    
    try:
        user, db_ok = select_user_by_(username=username)
        assert db_ok
    except:
        return jsonify({'Error': 'DB failed to execute query'}), 500
    
    try:
        assert check_password_hash(user['password'], password)
    except:
        return jsonify({"Forbidden": "Invalid username or password"}), 403
    
    try:
        content, status = request_token(user_id=user['id'], username=username, password=password)
        if status == 500:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert status == 200
        return jsonify({'Message': 'Login successful', 'token': content['token']}), 200
    except:
        return jsonify({'Error': 'Failed to generate a token'}), 500


@app.route('/users', methods=['PUT'])
def change_password():
    # 1. JWT token must be present
    if not request.headers or 'x-access-tokens' not in request.headers:
        return jsonify({'Forbidden': 'Access token is missing'}), 403
    
    # 2. Old and new passwords must be present
    try:
        old_password = request.json['password']
        new_password = request.json['new_password']
    except:
        return jsonify({"Error": "Old and/or new password not found in request"}), 400

    # 3. Request verification to JWT service -- which returns a user if successful
    try:
        user, status = request_validation(request.headers)
        if status == 500:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert status == 200
    except:
        return jsonify({'Forbidden': 'Token is invalid'}), 403
    
    # 4. Update password
    try:
        _, status = update_password(user['id'], old_password, new_password)
        assert status
        return jsonify({'Message': 'Password update successful'}), 200
    except:
        return jsonify({'Error': 'DB failed to execute query'}), 500
    


if __name__ == '__main__':
    app.run(debug=True)