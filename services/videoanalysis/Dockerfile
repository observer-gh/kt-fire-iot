FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY main.py .

# Create output directory
RUN mkdir -p /app/output/frames

# Create non-root user for security
RUN groupadd -r videoanalysis && useradd -r -g videoanalysis videoanalysis
RUN chown -R videoanalysis:videoanalysis /app
USER videoanalysis

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1
ENV HEALTH_PORT=8080

# Expose health check port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/healthz/live', timeout=5)" || exit 1

# Run the service
CMD ["python", "main.py"]
