from flask import Flask, request, jsonify
import sqlite3
import requests
import re, json, random
from hashids import Hashids
from time import time


SALT = "Very $$**^91@ sEcret SaaaLltT"  # Salt used to create hashes
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ktr9xIBj1ZP-S8GM3mYKdSToiT2tZPOevIh2wX_YVd8'

def select_by_id(id, username, cur):
    data = cur.execute("SELECT * FROM urls WHERE id=? AND username=?", (id, username)).fetchone()
    return data

def select_by_link(link, username, cur):
    data = cur.execute("SELECT * FROM urls WHERE link=? AND username=? ", (link, username)).fetchone()
    return data

def validate_token():
    response = requests.get('http://127.0.0.1:5003/verifytoken', headers=request.headers)
    print(response)
    if response.status_code == 200:
        return response.content
    else:
        return False


def select_by_username(username, cur):
    print(f"Selecting user with username: {username}")
    data = cur.execute("SELECT * FROM users WHERE username=?",
                       (username,)).fetchone()
    print(f"Selected user data: {data}")
    return data


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


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


# Creates connection to DB
def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = dict_factory
    return con


# URL shortner methods
# Creates a new (id, short url, orignal url) tuple if possible
@app.route('/', methods=['POST'])
def shorten_link():
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Access token is missing'}), 403
    try:
        content=validate_token()
        if content is False:
            return jsonify({'message': 'Token is invalid'}), 403

        # Throw 400 error when no link is provided
        if not request.data or not request.json or "link" not in request.json:
            return jsonify({"error": "no url found in request"}), 400

        # Retrieve link from the API request body
        link = request.json["link"]

        # Throw 400 error if the link is not valid
        if not is_valid_url(link):
            return jsonify({"error": "URL is not valid"}), 400

        # Connect to DB
        con = get_db_connection()
        cur = con.cursor()

        user = json.loads(content.decode('utf-8'))
        username = user['username']
        
        # If link exists in the DB, return data
        data = select_by_link(link, username, cur)
        if data:
            return jsonify({"short_url": data["short_url"], "id": data["id"]}), 200

        # Create new short url for the link
        number = int(round(time() * 1000)) + random.randint(0, 1e8)
        hashids = Hashids(min_length=8, salt=SALT)
        hashid = hashids.encode(number)

        # Insert into the DB
        query = "INSERT INTO urls (link, short_url, username) VALUES (?, ?, ?)"
        data = cur.execute(query, (link, hashid, username))
        con.commit()
        cur.close()
        con.close()

        # Return created url and id in DB
        return jsonify({"short_url": hashid, "id": data.lastrowid}), 201

    except:
        return jsonify({'message': 'Token is invalid'}), 403


@app.route('/', methods=['GET'])
def get_all():
    content=validate_token()
    if content is False:
        return jsonify({'message': 'Token is invalid'}), 403
    try:
        user = json.loads(content.decode('utf-8'))
        username = user['username']

        # Connect to DB
        con = get_db_connection()
        cur = con.cursor()

        # Get all rows from DB
        query = "SELECT * FROM urls WHERE username=?"
        cur.execute(query, (username, ))
        data = cur.fetchall()

        # Close DB
        cur.close()
        con.close()

        # Return data
        return json.dumps([dict(ix) for ix in data]), 200

    except:
        return jsonify({'message': 'Token is invalid'}), 403


# Responds with error code when attempt to request DELETE to path "/"
@app.route('/',  methods=['DELETE'])
def delete():
    content=validate_token()
    if content is False:
        return jsonify({'message': 'Token is invalid'}), 403

    try:
        return jsonify({"error": "not found"}), 404

    except:
        return jsonify({'message': 'Token is invalid'}), 403
# Redirects to a website associated with a given id if possible


@app.route('/<id>',  methods=['GET'])
def get_id(id):
    content=validate_token()
    if content is False:
        return jsonify({'message': 'Token is invalid'}), 403

    try:
        user = json.loads(content.decode('utf-8'))
        username = user['username']

        # Conect to DB
        con = get_db_connection()
        cur = con.cursor()

        # Get row with matching id
        data = select_by_id(id, username, cur)

        # Close DB
        cur.close()
        con.close()

        # Throw 404 error if id is not found in DB
        if not data:
            return jsonify({"error": "No data found"}), 404

        # Redirect to the original link if id found in DB
        return redirect(data["link"], code=301)

    except:
        return jsonify({'message': 'Token is invalid'}), 403

# Updates the associated original url of the id if possible


@app.route('/<id>', methods=['PUT'])
def update_id(id):
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Access token is missing'}), 403
    content=validate_token()
    if content is False:
        return jsonify({'message': 'Token is invalid'}), 403
    try:
        # Throw 400 error if a link is not provided
        if not request.data or not request.json or not request.json["link"]:
            return jsonify({"error": "no url is found in request."}), 400

        link = request.json["link"]

        # Connect to DB
        con = get_db_connection()
        cur = con.cursor()

        # Throw 400 error if the link is not valid
        if not is_valid_url(link):
            return jsonify({"response": "url is not valid in request."}), 400

        user = json.loads(content.decode('utf-8'))
        username = user['username']

        # Update the link in the DB
        query = "UPDATE urls SET link=? WHERE id=? AND username=?"
        cur.execute(query, (link, id, username))
        con.commit()

        # Close DB
        cur.close()
        con.close()

        # Return 200 if a row was updated
        if cur.rowcount:
            return jsonify({"response": "updated."}), 200

        # Throw 404 error if id was not found in DB
        return jsonify({"response": "id not found in table."}), 404

    except:
        return jsonify({'message': 'Token is invalid'}), 403

# Deletes the row with matching id if possible


@app.route('/<id>',  methods=['DELETE'])
def delete_id(id):
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Access token is missing'}), 403
    content=validate_token()
    if content is False:
        return jsonify({'message': 'Token is invalid'}), 403
    try:
        user = json.loads(content.decode('utf-8'))
        username = user['username']

        # connect to DB
        con = get_db_connection()
        cur = con.cursor()

        # Delete row with match id
        query = "Delete FROM urls WHERE id = ? AND username=?"
        cur.execute(query, (id, username))
        con.commit()

        # Close DB
        cur.close()
        con.close()

        # Return 204 status if a row was deleted
        if cur.rowcount:
            return jsonify({"response": "deleted."}), 204

        # Throw 404 error if id was not found in DB
        return jsonify({"response": "id not found in table."}), 404
    except:
        return jsonify({'message': 'Token is invalid'}), 403


# Deletes all rows present in the DB
@app.route('/deleteAllUrls', methods=['DELETE'])
def delete_all():
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Access token is missing'}), 403
    content=validate_token()
    if content is False:
        return jsonify({'message': 'Token is invalid'}), 403
    try:
        user = json.loads(content.decode('utf-8'))
        username = user['username']

        # connect to DB
        con = get_db_connection()
        cur = con.cursor()

        # Delete all rows in DB
        query = "Delete FROM urls WHERE username=?"
        cur.execute(query, (username, ))
        con.commit()

        # Close DB
        cur.close()
        con.close()

        # Return 204 status if succesfully deleted
        if cur.rowcount:
            return jsonify({"response": "all rows deleted."}), 204
        # DB is already empty
        return jsonify({"response": "Table is already empty."}), 200
    except:
        return jsonify({'message': 'Token is invalid'}), 403

# Start flask app automatically when run with python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
