from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask import Flask, request, redirect, jsonify
import sqlite3
import re
import json
from hashids import Hashids
from time import time
import random

SALT = "Very $$**^91@ sEcret SaaaLltT"  # Salt used to create hashes
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ktr9xIBj1ZP-S8GM3mYKdSToiT2tZPOevIh2wX_YVd8'


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = dict_factory
    return con


def select_by_username(username, cur):
    print(f"Selecting user with username: {username}")
    data = cur.execute("SELECT * FROM users WHERE username=?",
                       (username,)).fetchone()
    print(f"Selected user data: {data}")
    return data



@app.route('/verifytoken', methods=['GET'])
def verify_token():
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
            print(token)
        if not token:
            return jsonify({'message': 'Access token is missing'}), 403
        try:
            print(token)
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            username = data['username']
            con = get_db_connection()
            current_user = select_by_username(username, con.cursor())
            con.close()
        except:
            return jsonify({'message': 'Token is invalid'}), 403
        return jsonify(data), 200


@app.route('/generatetoken', methods=['POST'])
def generate_token():
    token = jwt.encode({'username': request.form['username'], 'password': request.form['password'], 'exp': datetime.datetime.utcnow(
    ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
    return str(token)


# Start flask app automatically when run with python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
