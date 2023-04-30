from flask import Flask, request, redirect, jsonify
import requests
import re, json, random, os
from time import time
from hashids import Hashids
from utils import *
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Read ENV vars
SECRET = os.environ.get('JWT_SECRET')
JWT_HOST = os.environ.get('JWT_HOST')
JWT_PORT = os.environ.get('JWT_PORT')


def request_validation(headers):
    response = requests.get(f'http://{JWT_HOST}:{JWT_PORT}', headers=headers)
    return json.loads(response.text), response.status_code

@app.route('/', methods=['POST'])
def shorten_link():
    # 1. JWT token must be present
    if not request.headers or 'x-access-tokens' not in request.headers:
        return jsonify({'Forbidden': 'Access token is missing'}), 403

    # 2. A link must be present and valid
    try:
        url = request.json['link']
        if not is_valid_url(url):
            return jsonify({"Error": "URL is not valid"}), 400
    except:
        return jsonify({"Error": "A link not found in request"}), 400

    # 3. Verify token
    try:
        user, status = request_validation(request.headers)
        if status == 500:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert status == 200
    except:
        return jsonify({'Forbidden': 'Token is invalid'}), 403
    
    # 4. Create new instance in DB
    try:
        result, status = create_url(url, user['id'])
        if status:
            return jsonify({'id': result['id'], 'original': url, 'short': result['short']}), 201
        if type(result) is dict:
            return jsonify({'id': result['id'], 'original': url, 'short': result['short']}), 200 
        return jsonify({'Error': 'DB failed to execute query'}), 500
    except:
        return jsonify({'Error': 'Something went wrong'}), 500
    

@app.route('/', methods=['GET'])
def get_all():
    # 1. JWT token must be present
    if not request.headers or 'x-access-tokens' not in request.headers:
        return jsonify({'Forbidden': 'Access token is missing'}), 403
    
    # 2. Verify token
    try:
        user, status = request_validation(request.headers)
        if status == 500:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert status == 200
    except:
        return jsonify({'Forbidden': 'Token is invalid'}), 403
    
    try:
        result, status = retrieve_all(user['id'])
        if status:
            return result, 200
        else:
            return jsonify({'Error': 'DB failed to execute query'}), 500
    except:
        return jsonify({'Error': 'Something went wrong'}), 500
    

@app.route('/',  methods=['DELETE'])
def delete():
    # 1. JWT token must be present
    if not request.headers or 'x-access-tokens' not in request.headers:
        return jsonify({'Forbidden': 'Access token is missing'}), 403
    
    # 2. Verify token and return "Not found" errpr
    try:
        _, status = request_validation(request.headers)
        if status == 500:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert status == 200
        return jsonify({"Error": "Page not found"}), 404
    except:
        return jsonify({'Forbidden': 'Token is invalid'}), 403


@app.route('/<id>',  methods=['GET'])
def get_by_id(id):
    # 1. JWT token must be present
    if not request.headers or 'x-access-tokens' not in request.headers:
        return jsonify({'Forbidden': 'Access token is missing'}), 403
    
    # 2. Verify token 
    try:
        _, status = request_validation(request.headers)
        if status == 500:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert status == 200
    except:
        return jsonify({'Forbidden': 'Token is invalid'}), 403

    # 3. Get a url by id and redirect to the website
    try:
        result, status = select_url_by_(id=id)
        assert status
        return redirect(result['original'], code=301)
    except:
        return jsonify({'Error': 'DB failed to execute query'}), 500


@app.route('/<id>',  methods=['PUT'])
def update_by_id(id):
    # 1. JWT token must be present
    if not request.headers or 'x-access-tokens' not in request.headers:
        return jsonify({'Forbidden': 'Access token is missing'}), 403
    
    # 2. A new link must be present and valid
    try:
        new_url = request.json['link']
        if not is_valid_url(new_url):
            return jsonify({"Error": "URL is not valid"}), 400
    except:
        return jsonify({"Error": "A link not found in request"}), 400

    # 3. Verify token 
    try:
        user, status = request_validation(request.headers)
        if status == 500:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert status == 200
    except:
        return jsonify({'Forbidden': 'Token is invalid'}), 403

    # 3. Update link
    try:
        result, status = update_link(id, new_url, user['id'])
        assert status
        if result:
            return jsonify({'id': result['id'], 'original': new_url, 'short': result['short']}), 200
        return jsonify({"Error": "id not found under your account"}), 404
    except:
        return jsonify({'Error': 'DB failed to execute query'}), 500

@app.route('/<id>',  methods=['DELETE'])
def delete_by_id(id):
    # 1. JWT token must be present
    if not request.headers or 'x-access-tokens' not in request.headers:
        return jsonify({'Forbidden': 'Access token is missing'}), 403
    
    # 2. Verify token 
    try:
        user, status = request_validation(request.headers)
        if status == 500:
            return jsonify({'Error': 'DB failed to execute query'}), 500
        assert status == 200
    except:
        return jsonify({'Forbidden': 'Token is invalid'}), 403

    try:
        result, status = remove_url(id, user['id'])
        if status:
            if result:
                return jsonify({"Message": f"Succesfully deleted {result['id']}:{result['original']}"}), 204
            return jsonify({"Error": "id not found under your account"}), 404
        return jsonify({'Error': 'DB failed to execute query'}), 500
    except:
        return jsonify({'Error': 'Something went wrong'}), 500
        

if __name__ == '__main__':
    app.run(debug=True)