How to run the services.
1. Run docker compose
```console
docker compose up --build
```

After user login, JWT token is returned. Place this token in the request header with key "x-access-tokens" to update password or use URL shortener service.

Put parameters such as (username, password) or (link) in request's JSON as a dictionary.


References to site : https://www.bacancytechnology.com/blog/flask-jwt-authentication for guidance.
