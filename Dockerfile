# Use a base image with Python and CUDA (for GPU support)
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy the application code
COPY . .

# Expose the API port
EXPOSE 5000

# Command to run the server
CMD ["python3", "app/server.py"]
