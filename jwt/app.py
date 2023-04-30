from flask import Flask, request, jsonify
import jwt
import datetime, os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from utils import select_user_by_id

load_dotenv()

app = Flask(__name__)

SECRET = os.environ.get('JWT_SECRET')

# decode token -> user id -> select user by id -> exists? ok
@app.route('/', methods=['GET'])
def verify_token():
    try:
        token = request.headers['x-access-tokens']
    except:
        return jsonify({'Forbidden': 'Access token is missing'}), 403

    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        user, db_ok = select_user_by_id(data['user_id'])
        if not db_ok:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert user
        return jsonify(user), 200
    except:
        return jsonify({'Forbidden': 'Token is invalid'}), 403
    

# encode id, username, password + expiration
@app.route('/', methods=['POST'])
def generate_token():
    try:
        token = jwt.encode(
            {
                'user_id'   : request.form['user_id'],
                'username'  : request.form['username'],
                'password'  : request.form['password'],
                'exp'       : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            SECRET, algorithm="HS256")
    except:
        return jsonify({'Error': 'Something went wrong'}), 500
    return jsonify({"token": str(token)}), 200

if __name__ == '__main__':
    app.run(debug=True)