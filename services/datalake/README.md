# DataLake

Data ingestion and streaming processing service for IoT fire monitoring.

## 🚀 Quick Start

### With Docker Compose (Recommended)

```bash
# Start all services including DataLake
docker-compose up -d

# Start just DataLake and dependencies
docker-compose up -d postgres redis kafka datalake-api datalake-dashboard

# Start DataLake API only
docker-compose up -d datalake-api

# Start DataLake dashboard only
docker-compose up -d datalake-dashboard
```

### Manual Build & Run

```bash
# Build API service
docker build -f Dockerfile.api -t fire-iot-datalake-api .

# Build dashboard service
docker build -f Dockerfile.dashboard -t fire-iot-datalake-dashboard .

# Run API service with dependencies
docker run -d --name datalake-api --network fire-iot-network -p 8084:8080 \
  -e POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/core \
  -e REDIS_URL=redis://redis:6379 \
  -e KAFKA_BROKERS=kafka:29092 \
  -e STORAGE_TYPE=mock \
  -e BATCH_SIZE=100 \
  fire-iot-datalake-api

# Run dashboard service
docker run -d --name datalake-dashboard --network fire-iot-network -p 8501:8501 \
  -e POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/core \
  fire-iot-datalake-dashboard
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run API service with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Run dashboard
streamlit run app/dashboard/main_dashboard.py --server.port=8501 --server.address=0.0.0.0

# Or use the provided script
./start_dashboard.sh
```

## 📊 APIs

- `GET /healthz` - Health check with Redis status
- `GET /redis/status` - Redis connection status and info
- `POST /ingest` - Ingest sensor data from external APIs
- `POST /trigger-batch-upload` - Manually trigger batch upload
- `GET /stats` - Service statistics and storage info (with Redis caching)
- `GET /storage/batches` - Get uploaded batches (MockStorage only)
- `DELETE /storage/batches` - Clear batch tracking (MockStorage only)
- `DELETE /cache` - Clear Redis cache
- `GET /docs` - API documentation (Swagger UI)

## 🎯 Real-time Dashboard

The DataLake service includes a comprehensive real-time monitoring dashboard built with Streamlit.

### Dashboard Features

- **Real-time Sensor Monitoring**: Live gauge charts for temperature, humidity, smoke density, CO level, and gas level
- **Historical Data Visualization**: Time series charts with configurable time ranges (1 hour, 24 hours, 7 days)
- **Alert Management**: Real-time alert detection and display with severity levels
- **Data Quality Monitoring**: Detection of missing data and quality issues

### Access Dashboard

```bash
# Via Docker Compose
docker-compose up -d datalake-dashboard
# Then open http://localhost:8501 in your browser

# Via Local Development
streamlit run app/dashboard/main_dashboard.py --server.port=8501

# Via Script
./start_dashboard.sh
```

### Access API

```bash
# Via Docker Compose
docker-compose up -d datalake-api
# Then access http://localhost:8084

# Via Local Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Health check
curl http://localhost:8084/healthz
```

### Dashboard Controls

- **Time Range**: Choose between real-time, 1 hour, 24 hours, or 7 days
- **Sensor Selection**: Show/hide specific sensor types
- **Auto Refresh**: Automatic updates every 30 seconds
- **Manual Refresh**: Manual refresh button for immediate updates

### Alert Thresholds

- **Temperature**: HIGH at 40°C, CRITICAL at 60°C
- **Humidity**: HIGH at 90%, CRITICAL at 95%
- **Smoke Density**: HIGH at 0.500, CRITICAL at 1.000
- **CO Level**: HIGH at 30.000 ppm, CRITICAL at 50.000 ppm
- **Gas Level**: HIGH at 100.000 ppm, CRITICAL at 200.000 ppm

## 🔄 Data Flow

```
External API → DataLake (clean/process) → Database → Redis Cache → Storage → Kafka → Other Services
```

## 🗄️ Redis Caching

The DataLake service now includes Redis caching for improved performance:

- **Stats Caching**: Service statistics are cached for 5 minutes to reduce database queries
- **Health Monitoring**: Redis connection status is included in health checks
- **Cache Management**: Dedicated endpoints for cache status and clearing
- **Performance**: Faster response times for frequently accessed data

### Redis Configuration

- **URL**: Configurable via `REDIS_URL` environment variable
- **Default**: `redis://redis:6379` (Docker Compose)
- **Fallback**: `redis://localhost:6379` (Local development)
- **Connection**: Automatic connection with health monitoring

### Data Processing

- **Validation**: Sensor data validation and bounds checking
- **Cleaning**: Out-of-range values clamped to valid ranges
- **Anomaly Detection**: Automatic threshold-based anomaly detection
- **Database Storage**: Real-time data stored in PostgreSQL
- **Batch Upload**: Configurable batch processing to file storage
- **Event Publishing**: Kafka topics for anomaly detection and data saved events

### Kafka Topics

- `fire-iot.sensorDataAnomalyDetected` - Anomaly detection events
- `fire-iot.sensorDataSaved` - Data saved to storage events
- `fire-iot.sensor-data` - Normal sensor readings

## 🗄️ Storage Types

### MockStorage (Local Testing)

- **Default**: `STORAGE_TYPE=mock`
- **Batch Size**: 100 records (configurable)
- **Storage**: Local filesystem (JSON files)
- **Features**: Batch tracking, statistics, testing endpoints

### StorageService (Production)

- **Set**: `STORAGE_TYPE=production`
- **Batch Size**: 1000 records (configurable)
- **Storage**: Production storage paths
- **Features**: Production-optimized batch processing

## 🧪 Testing

### Test Data Ingestion

```bash
# Normal sensor data
curl -X POST http://localhost:8084/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "EQ001",
    "facility_id": "FAC001",
    "equipment_location": "Building A, Floor 1",
    "measured_at": "2024-01-01T12:00:00Z",
    "temperature": 25.5,
    "humidity": 60.2,
    "smoke_density": 0.001,
    "co_level": 0.005,
    "gas_level": 0.002
  }'

# Temperature anomaly (above 80°C threshold)
curl -X POST http://localhost:8084/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "EQ002",
    "facility_id": "FAC001",
    "measured_at": "2024-01-01T12:00:00Z",
    "temperature": 85.0,
    "humidity": 65.0
  }'

# Smoke critical anomaly (above 500ppm threshold)
curl -X POST http://localhost:8084/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "EQ003",
    "facility_id": "FAC001",
    "measured_at": "2024-01-01T12:00:00Z",
    "smoke_density": 600.0
  }'
```

### Batch Processing Test

```bash
# Send 100 records to trigger batch upload
for i in {1..100}; do
  curl -X POST http://localhost:8084/ingest \
    -H "Content-Type: application/json" \
    -d "{
      \"equipment_id\": \"EQ00$i\",
      \"measured_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
      \"temperature\": $((20 + i % 10))
    }"
done

# Check batch upload status
curl http://localhost:8084/stats

# Manually trigger batch upload
curl -X POST http://localhost:8084/trigger-batch-upload

# View uploaded batches (MockStorage only)
curl http://localhost:8084/storage/batches
```

### Health Check

```bash
curl http://localhost:8084/healthz
```

## 📁 Structure

```
app/
├── main.py              # FastAPI application + endpoints
├── config.py            # Configuration management
├── database.py          # Database connection
├── db_models.py         # SQLAlchemy ORM models
├── models.py            # Pydantic data models
├── processor.py         # Data cleaning & anomaly detection
├── publisher.py         # Kafka event publishing
├── scheduler.py         # Batch upload scheduler
├── storage_interface.py # Storage interface abstraction
├── storage_service.py   # Production storage service
└── mock_storage.py      # Mock storage for testing
```

## 🔧 Configuration

### Environment Variables

- `POSTGRES_URL` - PostgreSQL connection string
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_HOST` - PostgreSQL host
- `POSTGRES_PORT` - PostgreSQL port
- `POSTGRES_DB` - PostgreSQL database name
- `REDIS_URL` - Redis connection string
- `KAFKA_BROKERS` - Kafka broker addresses
- `STORAGE_TYPE` - Storage type: `mock` or `production`
- `BATCH_SIZE` - Batch size for uploads
- `BATCH_INTERVAL_MINUTES` - Batch processing interval
- `STORAGE_PATH` - Storage directory path

### Anomaly Detection Thresholds

- **Temperature**: Alert at 80°C (WARN), 95°C (EMERGENCY)
- **Humidity**: Alert at 90% (WARN), 98% (EMERGENCY)
- **Smoke Density**: Alert at 100ppm (WARN), 500ppm (EMERGENCY)
- **CO Level**: Alert at 50ppm (WARN), 200ppm (EMERGENCY)
- **Gas Level**: Alert at 100ppm (WARN), 500ppm (EMERGENCY)

### Database Schema

The service uses the following tables:

- `realtime` - Real-time sensor data
- `alert` - Alert information

## 🚀 Docker Compose Testing

For complete infrastructure testing, see `DOCKER_COMPOSE_TEST.md`:

```bash
# Start entire infrastructure
docker-compose up -d

# Test DataLake API service
curl http://localhost:8084/healthz
curl http://localhost:8084/stats

# Test DataLake dashboard
# Open http://localhost:8501 in your browser
```

## 🚀 Azure App Container Service 배포

Azure App Container Service의 포트 제약사항을 고려하여 API와 대시보드를 분리하여 배포할 수 있습니다.

### API 서비스 배포

```bash
chmod +x deploy-api.sh
./deploy-api.sh <resource-group> <app-name>
```

### 대시보드 서비스 배포

```bash
chmod +x deploy-dashboard.sh
./deploy-dashboard.sh <resource-group> <app-name>
```

## 📊 Monitoring

- **Real-time records count**
- **Active alerts count**
- **Storage type and configuration**
- **Batch scheduler status**
- **Storage statistics (MockStorage)**
- **Uploaded batches tracking**
