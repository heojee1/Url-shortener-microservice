#!/bin/env python3

# URL SHORTENER.py
#   by Tim Müller
#
# Created:
#   03 Mar 2022, 14:25:23
# Last edited:
#   02 May 2023, 11:46:03
# Auto updated?
#   Yes
#
# Description:
#   Implements a simple URL-shortening RESTful service.
#   Build with the Flask (https://flask.palletsprojects.com/en/2.0.x/)
#   framework.
#
#   In this service, we try to assign a short identifier to each new URL. This
#   is implemented by choosing a number, and then 'decoding' that in much the
#   same way one would decode a number to a binary string, except with a
#   different base. See 'generate_id()' for this implementation.
#
#   The version in this repository has been extended to support JWTs to
#   identify a user. You can compare it to the reference implementation from
#   assignment 1 to see what has changed (most modern editors should allow you
#   to do this easily).
#

import base64
from http.client import responses
import os
import re
import requests
import sys
import typing

from flask import Flask, abort, redirect, request
from dotenv import load_dotenv
from utils import *

load_dotenv()

### CONSTANTS ###
# Regular expressions that is used to check URLs for correctness.
# Taken from: https://stackoverflow.com/a/7995979
URL_CORRECTNESS_REGEX = (
    r"(?i)"                                                             # We activate the case-insensitivity extension for this regex. See the Python docs for more info: https://docs.python.org/3/library/re.html#regular-expression-syntax (see `(?...)`)
    r"^https?://"                                                       # Matches the start of the string (`^`) and then the `http://` or `https://` scheme
    r"(?:"                                                              # Matches either:
        r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?"         # A domain name, which consists of various subdomains separated by dots. Each of those matches an alphanumeric character, optionally followed by either 0-61 alphanumeric characters or dashes and another single alhpanumeric character. Finally, there is a letter-only toplevel domain name of 2-6 characters and an optional dot.
        r"|"                                                            # OR
        r"localhost"                                                        # We match 'localhost' literally
        r"|"                                                            # OR
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"                               # We match an IPv4 address, which are four sets of 1-3 digits.
    r")"
    r"(?::\d+)?"                                                        # Then we match an optional port, consisting of at least one digit. Note that the double colon is actually part of `(?:)`, which means a matched but not saved string.
    r"(?:/?|[/?]\S+)$"                                                  # Finally, we match an optional slash or a (slash or question mark) followed by at least one non-whitespace character. This effectively makes most of the paths wildcards, as they can be anything; but because paths can container arbitrary information, this is OK. At last we match the end-of-string boundary, `$`.
)

# Read ENV vars
JWT_HOST = os.environ.get('JWT_HOST')
JWT_PORT = os.environ.get('JWT_PORT')


def valid_url(url: str) -> bool:
    """
        Tries to match the given URL for correctness.

        Do so by simply matching it to a regular expression that performs this
        check (see the comment at URL_CORRECTNESS_REGEX).
    """

    # Match with a regex-expression
    return re.match(URL_CORRECTNESS_REGEX, url) is not None


def check_login(token: str) -> typing.Optional[str]:
    """
        Checks if the given token is a legal login token by verifying it with
        the authentication service.

        The location of the service is read from the AUTH_SVC environment variable.
    """

    # Get the auth service's location
    auth_svc = f"http://{JWT_HOST}:{JWT_PORT}"

    # Strip 'Bearer' from the token, if any
    if token[:7] == "Bearer ":
        token = token[7:]

    # Send a request to the authentication service
    try:
        r = requests.post(f"{auth_svc}/tokens", data={ "token": token })
    except requests.exceptions.RequestException as err:
        print(f"[ERROR] Token verification failed because we could not reach the authentication service ({auth_svc}/tokens): {err}", file=sys.stderr)
        return None

    # Check whether the request succeeded
    if r.status_code != 200:
        print(f"[ERROR] Token verification failed because authentication service ({auth_svc}/tokens) returned status code {r.status_code} ({responses[r.status_code] if r.status_code in responses else '???'})", file=sys.stderr)
        return None

    # Attempt to decode the response as JSON
    try:
        result = r.json()
    except requests.exceptions.JSONDecodeError as err:
        print(f"[ERROR] Token verification failed because authentication service ({auth_svc}/token) returned invalid JSON: {err}", file=sys.stderr)
        return None
    # Additionally assert it's only one of two types
    if result is not None and type(result) != str:
        print(f"[ERROR] Token verification failed because authentication service ({auth_svc}/token) returned non-string, non-null value '{result}'", file=sys.stderr)
        return None

    # We can directly return the value, since we now know it's either the username or None
    return result



### ENTRYPOINT ###
# Setup the application as a Flask app
app = Flask(__name__)


### API FUNCTIONS ###
# We use a flask macro to make let this function be called for the root URL ("/") and the specified HTTP methods.
@app.route("/", methods=['GET', 'POST', 'DELETE'])
def root():
    """
        Handles everything that falls under the API root (/).

        Supported methods:
         - GET: Returns a list of all the identifiers, as a JSON file.
         - POST: Asks to generate a new ID for the given URL (not in the URL itself, but as a form-parameter).
         - DELETE: Not supported for the general, so will return a 404 always.
        
        In all cases, if the user fails to authorize himself, a 403 is returned.
    """

    # Switch on the method used
    if request.method == "GET":
        # Get the authorization token
        if "Authorization" not in request.headers: return "Forbidden", 403
        token = request.headers["Authorization"]

        # Check if the token is valid
        username = check_login(token)
        if username is None: return "Forbidden", 403

        # Collect all the results for this user in a JSON map
        # We can simply return a dict, and flask will automatically serialize this to JSON for us
        try:
            result, status = retrieve_all(username)
            if status:
                return result, 200
            else:
                return 'DB failed to execute query', 500
        except:
            return 'Something went wrong', 500

    elif request.method == "POST":
        # Get the authorization token
        if "Authorization" not in request.headers: return "Forbidden", 403
        token = request.headers["Authorization"]

        # Check if the token is valid
        username = check_login(token)
        if username is None: return "Forbidden", 403

        # Try to get the URL
        if "url" not in request.form:
            return "URL not specified", 400
        url = request.form["url"]

        # Validate the URL
        if not valid_url(url):
            return "Invalid URL", 400

        try:
            result, status = create_url(url, username)
            if status:
                return "success", 201
            if type(result) is dict:
                return "already exists", 200 
            return 'DB failed to execute query', 500
        except:
            return 'Something went wrong', 500

    elif request.method == "DELETE":
        # Get the authorization token
        if "Authorization" not in request.headers: return "Forbidden", 403
        token = request.headers["Authorization"]

        # Check if the token is valid
        username = check_login(token)
        if username is None: return "Forbidden", 403

        # Get the list of stuff to delete for this user
        try:
            result, status = remove_all_url(username)
            if not status:
                return 'DB failed to execute query', 500
            if result:
                return "Deleted all urls", 204
        except:
            return 'Something went wrong', 500
        return "Nothing to delete", 404


# We use a flask macro to make let this function be called for any nested string under the root URL ("/:id") and the specified HTTP methods.
# The syntax of the identifier is '<string:id>', which tells flask it's a string (=any non-slash text) that is named 'id'
@app.route("/<string:id>", methods=['GET', 'PUT', 'DELETE'])
def url(id):
    """
        Handles everything that falls under a URL that is an identifier (/:id).

        Methods:
         - GET: Returns the URL behind the given identifier as a 301 result (moved permanently) so the browser automatically redirects.
         - PUT: Updates the given ID to point to the given URL (as a POST field). Returns a 200 on success, 400 on failure or 404 on not-existing ID.
         - DELETE: Deletes the ID/URL mapping based on the ID given, returning a 204 (no content).
    """

    # Switch on the method used
    if request.method == "GET":
        # No authentication needed, as this is public now

        # Check to see if we know this one
        try:
            result, status = select_url_by_(id=id)
            print(result, result['original'])
            if status:
                return redirect(result['original'], code=301)
            else:
                return "No url found", 404
        except:
            return 'DB failed to execute query', 500

    elif request.method == "PUT":
        # Get the authorization token
        if "Authorization" not in request.headers: return "Forbidden", 403
        token = request.headers["Authorization"]

        # Check if the token is valid
        username = check_login(token)
        if username is None: return "Forbidden", 403

        # Try to get the URL
        if "url" not in request.form:
            return "URL not specified", 400
        new_url = request.form["url"]

        # Validate the URL
        if not valid_url(new_url):
            return "Invalid URL", 400
        
        try:
            user, status = select_user_by_(username=username)
            if not status:
                'DB failed to execute query', 500
            if status and not user:
                return "Forbidden", 403
        except:
            return 'Something went wrong', 500

        try:
            result, status = update_link(id, new_url, username)
            assert status
            if result:
                return "success", 200
            return "id not found under your account", 404
        except:
            return 'DB failed to execute query', 500
        

    elif request.method == "DELETE":
        # Get the authorization token
        if "Authorization" not in request.headers: return "Forbidden", 403
        token = request.headers["Authorization"]

        # Check if the token is valid
        username = check_login(token)
        if username is None: return "Forbidden", 403

        try:
            result, status = remove_url(id, username)
            print(result)
            if not status:
                return 'DB failed to execute query', 500
            if result:
                    return "Delete successful", 204
            return "id not found under your account", 404
        except:
            return 'Something went wrong', 500