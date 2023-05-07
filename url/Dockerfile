FROM python:3.7-slim-buster

WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y curl
RUN pip install -r requirements.txt
EXPOSE 5001
COPY . .
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]