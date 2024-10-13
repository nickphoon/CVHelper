# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install dependencies for running GUI applications
RUN apt-get update && apt-get install -y \
    python3-pyqt5 \
    libgl1-mesa-glx \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your application
CMD ["python", "app.py"]
