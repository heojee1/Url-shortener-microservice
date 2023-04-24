from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify
import sqlite3
import re, json, requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ktr9xIBj1ZP-S8GM3mYKdSToiT2tZPOevIh2wX_YVd8'

# Mapping function for sqlite3 to return rows as dictionary
def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

# Creates connection to DB
def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = dict_factory
    return con

# function to insert data into users table
def insert_user(username, password):
    con = get_db_connection()
    cur = con.cursor()
    hashed_password = generate_password_hash(password)
    query = "INSERT INTO users (username, password) VALUES (?, ?)"
    cur.execute(query, (username, hashed_password))
    con.commit()
    cur.close()
    con.close()


# Selects a row by matching the link
def select_by_link(link, cur):
    data = cur.execute("SELECT * FROM urls WHERE link=?", (link, )).fetchone()
    return data


# Selects a row by matching the id
def select_by_id(id, cur):
    data = cur.execute("SELECT * FROM urls WHERE id=?", (id, )).fetchone()
    return data

# Selects a row by matching the username
def select_by_username(username, cur):
    print(f"Selecting user with username: {username}")
    data = cur.execute("SELECT * FROM users WHERE username=?",
                       (username,)).fetchone()
    print(f"Selected user data: {data}")
    return data


# Returns the password of the username
def select_password_by_username(username, cursor):
    print(f"Selecting password for user: {username}")
    data = cursor.execute(
        "SELECT password FROM users WHERE username=?", (username,)).fetchone()
    if data:
        print(f"Selected password: {data['password']}")
        return data['password']
    else:
        return None

# Updates the password of the username
def update_password(username, new_password, cur):
    print(f"Updating password for user with username: {username}")
    hashed_password = generate_password_hash(new_password)
    query = "UPDATE users SET password=? WHERE username=?"
    cur.execute(query, (hashed_password, username))
    cur.connection.commit()
    print("Password updated successfully!")
    cur.close()


# Regex from Django open source code (https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py/#L45)
def is_valid_url(url):
    regex = re.compile(
        r'^(?:http)s?://'  # scheme
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(regex.match(url))


def validate_token():
    response = requests.get('http://127.0.0.1:5003/verifytoken', headers=request.headers)
    print(response)
    if response.status_code == 200:
        return response.content
    else:
        return False


# Creates a new user
@app.route('/users', methods=['POST'])
def new_user():
    # Throw 400 error when no username and password is provided
    if not request.json or "username" not in request.json or "password" not in request.json:
        return jsonify({"error": "username and/or password not found in request"}), 400

    # Retrieve username and password from the API request body
    username = request.json["username"]
    password = request.json["password"]

    # If user exists in the DB, return data
    con = get_db_connection()
    data = select_by_username(username, con.cursor())
    con.close()
    if data:
        return jsonify({"error": "Username already exists"}), 409

    # Insert user into the DB
    insert_user(username, password)
    PARAMS = {'username':username, 'password':password}

    token =  requests.post('http://127.0.0.1:5003/generatetoken', data = PARAMS)

    # Return token in the response
    return jsonify({'message': 'sign up successful', 'token': str(token.text)}), 201


# Logs user in
@app.route('/users/login', methods=['POST'])
def login():
    # Throw 400 error when no username and password is provided
    if not request.json or "username" not in request.json or "password" not in request.json:
        return jsonify({"error": "username and/or password not found in request"}), 400

    # Retrieve username and password from the API request body
    username = request.json["username"]
    password = request.json["password"]

    # Check if the user exists in the DB and the password is correct
    con = get_db_connection()
    data = select_by_username(username, con.cursor())
    con.close()
    if not data or not check_password_hash(data['password'], password):
        return jsonify({"error": "Invalid username or password"}), 403
    PARAMS = {'username':username, 'password':password}
    token =  requests.post('http://127.0.0.1:5003/generatetoken', data = PARAMS)

    # Return token in the response
    return jsonify({'message': 'login successful', 'token': str(token.text)}), 200


# Updates user password
@app.route('/users', methods=['PUT'])
def changePassword():
    token = request.headers['x-access-tokens']
    if not token:
        return jsonify({'message': 'Access token is missing'}), 403
    try:
        content=validate_token()
        if content is False:
            return jsonify({'message': 'Token is invalid'}), 403
        # Throw 400 error when no username and password is provided
        if not request.json or "username" not in request.json or "password" not in request.json or "new_password" not in request.json:
            return jsonify({"error": "username, password, and new_password not found in request"}), 400

        # Parse the JSON content into a Python dictionary
        data = json.loads(content.decode('utf-8'))

        username = data['username']
        username_given = request.json["username"]
        old_password = request.json["password"]
        new_password = request.json["new_password"]
        con = get_db_connection()
        current_user_db = select_by_username(username, con.cursor())

        if username != current_user_db['username'] or username != username_given or not check_password_hash(current_user_db['password'], old_password):
            return jsonify({"error": "Forbidden, Invalid username or password"}), 403
        else:
            update_password(username, new_password, con.cursor())
            return jsonify({'message': f'Welcome {username_given}! Password is updated.'}), 200

    except:
        return jsonify({'message': 'Token is invalid'}), 403


# Welcome page for a user
@app.route('/users', methods=['GET'])
def get_user():
    content=validate_token()
    if content is False:
        return jsonify({'message': 'Token is invalid'}), 403
    data = json.loads(content.decode('utf-8'))
    username = data['username']
    password = data['password']
    con = get_db_connection()
    current_user = select_by_username(username, con.cursor())
    hashedPasswrd = select_password_by_username(username, con.cursor())
    check = check_password_hash(hashedPasswrd, password)
    con.close()
    return jsonify({'message': f'Welcome {current_user["username"]}!', 'password': hashedPasswrd, 'Result': check})


# Start flask app automatically when run with python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
