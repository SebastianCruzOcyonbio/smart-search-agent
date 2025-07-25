# Use official Python image for reliability
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies (for common Python packages)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask (or Streamlit) on port 8501
EXPOSE 8501

# Use a non-root user for security (optional, but recommended)
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser

# Launch app via gunicorn (adjust if your entrypoint is different)
CMD ["gunicorn", "--bind", "0.0.0.0:8501", "app:app"]
