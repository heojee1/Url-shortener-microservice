# Web assignment 3

## How to run the services.
```console
docker compose up --build
```

After user login, JWT token is returned. Place this token in the request header with key "x-access-tokens" to update password or use URL shortener service.
Put parameters such as (username, password) or (link) in request's JSON as a dictionary.


## Structure
Folders **jwt**, **url**, and **user** each contain Dockerfile, .env, requirements.txt, app.py, and utils.py.

___

References to site : https://www.bacancytechnology.com/blog/flask-jwt-authentication for guidance.
