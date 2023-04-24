How to run the services.
1. Download dependenceis
```console
pip install -r requirements.txt
```
2. Initialize database
```console
python3 init_db.py
```
3. Run JWT microservice in port 5003
```console
python3 jwt_authentication.py
```
4. Run user managment microservice in port 5000
```console
python3 users.py
```
5. Run URL shortener microservice in port 5001
```console
python3 users.py
```

After user login, JWT token is returned. Place this token in the request header with key "x-access-tokens" to update password or use URL shortener service.

Put parameters such as (username, password) or (link) in request's JSON as a dictionary.


References to site : https://www.bacancytechnology.com/blog/flask-jwt-authentication for guidance.
