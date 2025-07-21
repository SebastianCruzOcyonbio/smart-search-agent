# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy dependency list
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Streamlit-specific config
EXPOSE 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false"]
