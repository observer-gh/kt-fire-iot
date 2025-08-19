# DataLake

Data ingestion and streaming processing service for IoT fire monitoring.

## 🚀 Quick Start

### With Docker Compose (Recommended)
```bash
# Start all services including DataLake
docker-compose up -d

# Start just DataLake and dependencies
docker-compose up -d postgres redis kafka datalake
```

### Manual Build & Run
```bash
# Build
docker build -t fire-iot-datalake .

# Run with dependencies
docker run -d --name datalake --network fire-iot-network -p 8084:8080 \
  -e POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/core \
  -e REDIS_URL=redis://redis:6379 \
  -e KAFKA_BROKERS=kafka:29092 \
  fire-iot-datalake
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## 📊 APIs

- `GET /healthz` - Health check
- `POST /ingest` - Ingest sensor data from external APIs
- `GET /docs` - API documentation (Swagger UI)

## 🔄 Data Flow

```
External API → DataLake (clean/process) → Kafka → Other Services
```

### Data Processing
- **Validation**: Sensor type and value bounds
- **Cleaning**: Out-of-range values clamped
- **Alert Detection**: Automatic threshold checking
- **Event Publishing**: Kafka topics based on data type

### Kafka Topics
- `fire-iot.alerts` - Alert events (HIGH/CRITICAL severity)
- `fire-iot.sensor-data` - Normal sensor readings

## 🧪 Testing

### Test Data Ingestion
```bash
# Temperature alert
curl -X POST http://localhost:8084/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": "station-001",
    "sensor_type": "temperature",
    "value": 85.5,
    "timestamp": "2024-01-15T10:30:00Z"
  }'

# Smoke critical alert
curl -X POST http://localhost:8084/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": "station-002",
    "sensor_type": "smoke",
    "value": 600.0,
    "timestamp": "2024-01-15T10:31:00Z"
  }'
```

### Health Check
```bash
curl http://localhost:8084/healthz
```

## 📁 Structure

```
app/
├── main.py              # FastAPI application + ingest endpoint
├── models.py            # Pydantic data models
├── processor.py         # Data cleaning & alert detection
└── publisher.py         # Kafka event publishing
```

## 🔧 Configuration

### Environment Variables
- `POSTGRES_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `KAFKA_BROKERS` - Kafka broker addresses

### Sensor Thresholds
- **Temperature**: Alert at 80°C (HIGH), 95°C (CRITICAL)
- **Humidity**: Alert at 90% (HIGH), 98% (CRITICAL)
- **Smoke**: Alert at 100ppm (HIGH), 500ppm (CRITICAL)
- **CO2**: Alert at 1000ppm (HIGH), 2000ppm (CRITICAL)
- **Pressure**: Alert at 1050hPa (HIGH), 1080hPa (CRITICAL)
