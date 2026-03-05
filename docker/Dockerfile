# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy pyproject.toml first for dependency caching
COPY pyproject.toml .

# Install pip dependencies using pip install with no cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory and config directory into the container
COPY src ./src
COPY config ./config

# Add a LABEL maintainer with value 'ai-factory'
LABEL maintainer="ai-factory"

# Set the default CMD to python src/monitor/runner.py
CMD ["python", "src/monitor/runner.py"]
