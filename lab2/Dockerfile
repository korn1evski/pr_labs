# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set environment variables
# Prevents Python from writing .pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1
# Set the Flask application entry point
ENV FLASK_APP app.py

# Set the working directory in the container
WORKDIR /app

# Install dependencies required to build psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc

# Copy the requirements file to the container
COPY requirements.txt /app/requirements.txt

# Install any necessary dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code to the container
COPY . /app

# Expose the port the app runs on
EXPOSE 5000

# Create the uploads directory to store uploaded files
RUN mkdir -p /app/uploads

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
