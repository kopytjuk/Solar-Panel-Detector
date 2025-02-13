# Use the official Python image from the Docker Hub
FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc python3-dev ffmpeg libsm6 libxext6

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Update pip
RUN pip install --upgrade pip

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/src

# Specify the command to run your application
CMD ["python", "detect_cli.py", "/images", "result.csv"]