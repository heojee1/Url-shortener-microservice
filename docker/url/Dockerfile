FROM python:3.7-slim-buster

# Set working directory
WORKDIR /code

# Set Flask envorinments
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Expose port 5001 so that the NGNIX can reach it but not accessible exterinally
EXPOSE 5001

# Copy directory
COPY . .

# Start the Flask app on port 5001
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]