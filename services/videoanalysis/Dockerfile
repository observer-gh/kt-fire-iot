FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY main.py .

# Create output directory
RUN mkdir -p /app/output/frames

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Run the service
CMD ["python", "main.py"]
