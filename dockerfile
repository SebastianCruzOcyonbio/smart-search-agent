# Base image
FROM python:3.12-slim

# Set working dir
WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Set environment vars (optional if using App Runner secrets)
ENV PYTHONUNBUFFERED=1

# Expose Flask on port 8501
EXPOSE 8501

# Launch app via gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8501", "main:app"]
