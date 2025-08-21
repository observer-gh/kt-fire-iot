# DataLake

Data ingestion and streaming processing service for IoT fire monitoring.

## 🏗️ Architecture

### Data Flow

1. **Real-time Data Ingestion**: 센서 데이터는 Mock Server나 외부 API에서 수신되어 Redis에 저장됩니다.
2. **Redis Storage**: 모든 센서 데이터는 Redis에 실시간으로 저장되어 빠른 접근이 가능합니다.
3. **Periodic Flush**: 1분 간격으로 Redis의 데이터를 로컬 스토리지에 flush합니다.
4. **Metadata Storage**: flush 시 메타데이터(수집 기간, 스토리지 위치, 통계 정보 등)를 PostgreSQL에 저장합니다.
5. **Event Publishing**: `sensorDataSaved` Kafka 이벤트는 flush 시에만 발행됩니다.
6. **Anomaly Detection**: 이상치 탐지는 실시간으로 수행되며 즉시 `sensorDataAnomalyDetected` 이벤트가 발행됩니다.

### Key Components

- **Redis Client**: 센서 데이터의 임시 저장소 역할
- **Batch Scheduler**: Redis flush와 배치 업로드를 관리하며 메타데이터 생성
- **Storage Service**: 로컬 스토리지에 데이터를 영구 저장하고 메타데이터를 PostgreSQL에 저장
- **Kafka Publisher**: 이벤트 발행을 담당
- **Metadata Management**: 스토리지 flush 정보를 추적하고 관리

### Storage Metadata

Redis flush 시마다 다음과 같은 메타데이터가 PostgreSQL의 `storage_metadata` 테이블에 저장됩니다:

- **기본 정보**: flush 시간, 데이터 수집 기간, 레코드 수
- **스토리지 정보**: 저장 경로, 스토리지 타입, 파일 크기
- **처리 정보**: 처리 시간, 성공/실패 개수
- **추가 정보**: 배치 ID, flush 타입, 에러 메시지 등

이를 통해 데이터 수집 현황을 추적하고 스토리지 효율성을 모니터링할 수 있습니다.

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
  -e REDIS_FLUSH_INTERVAL_SECONDS=60 \
  -e MOCK_SERVER_URL=http://mock-server:8081 \
  -e MOCK_SERVER_DATA_COUNT=10 \
  -e MOCK_SERVER_DATA_FETCH_INTERVAL=5 \
  -e MOCK_SERVER_STREAM_COUNT=5 \
  -e MOCK_SERVER_BATCH_COUNT=100 \
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

### Core APIs

- `GET /healthz` - Health check with Redis and Mock Server status
- `GET /redis/status` - Redis connection status and info (includes sensor data count)
- `GET /stats` - Service statistics and storage info (with Redis caching)
- `GET /docs` - API documentation (Swagger UI)

### Storage Metadata APIs (New)

- `GET /storage/metadata` - Get storage metadata with filtering and pagination
- `GET /storage/metadata/{metadata_id}` - Get specific storage metadata by ID
- `GET /storage/metadata/stats/summary` - Get summary statistics of storage metadata

### Data Ingestion APIs

#### Mock Server Integration (New)

- `POST /ingest` - **Mock Server에서 실시간 데이터를 가져와서 Redis에 저장**
- `POST /ingest/stream` - Mock Server에서 스트리밍 데이터를 가져와서 Redis에 저장
- `POST /ingest/batch` - Mock Server에서 배치 데이터를 가져와서 Redis에 저장

#### Redis Management APIs (New)

- `POST /trigger-redis-flush` - Redis 데이터를 강제로 로컬 스토리지에 flush

#### Mock Data Scheduler Control APIs (New)

- `GET /scheduler/mock/status` - Mock Data Scheduler 상태 확인
- `POST /scheduler/mock/start` - Mock Data Scheduler 시작
- `POST /scheduler/mock/stop` - Mock Data Scheduler 중지
- `POST /scheduler/mock/restart` - Mock Data Scheduler 재시작
- `POST /scheduler/mock/force-process` - Mock 데이터 처리 강제 실행 (스케줄러 상태와 무관)

#### External API Integration (Legacy)

- `POST /ingest/external` - 외부 API에서 센서 데이터 수신하여 Redis에 저장

### Storage & Batch APIs

- `POST /trigger-batch-upload` - Manually trigger batch upload
- `GET /storage/batches` - Get uploaded batches (MockStorage only)
- `DELETE /storage/batches` - Clear batch tracking (MockStorage only)
- `DELETE /cache` - Clear Redis cache

## 🔄 Mock Server Integration

DataLake는 이제 Mock Server와 자동으로 연동되어 실시간 데이터를 주기적으로 가져와서 처리합니다.

### Features

- **자동 폴링**: 설정된 간격으로 Mock Server에서 데이터를 가져옴
- **실시간 처리**: 받아온 데이터를 즉시 처리하고 이상치 탐지
- **이벤트 발행**: 이상치 발견 시 ControlTower로 이벤트 발행
- **다양한 데이터 타입**: 실시간, 스트리밍, 배치 데이터 지원

### Configuration

```bash
# Mock Server 설정
MOCK_SERVER_URL=http://localhost:8081          # Mock Server URL
MOCK_SERVER_DATA_COUNT=10                     # 기본 데이터 개수
MOCK_SERVER_DATA_FETCH_INTERVAL=5             # 데이터 가져오기 간격 (초) - 기본값: 5초
MOCK_SERVER_STREAM_COUNT=5                    # 스트리밍 데이터 개수
MOCK_SERVER_BATCH_COUNT=100                   # 배치 데이터 개수

# Dashboard 설정
DASHBOARD_REFRESH_INTERVAL=1                  # 대시보드 자동 새로고침 간격 (초) - 기본값: 1초
```

### Data Flow

1. **Mock Server** → 실시간 센서 데이터 생성 (90% 정상, 10% 이상)
2. **DataLake** → 주기적으로 Mock Server에서 데이터 가져오기
3. **DataLake** → 데이터 처리 및 이상치 탐지
4. **DataLake** → 이상치 발견 시 ControlTower로 이벤트 발행
5. **DataLake** → 모든 데이터를 데이터베이스에 저장

## 🎯 Real-time Dashboard

The DataLake service includes a comprehensive real-time monitoring dashboard built with Streamlit.

### Dashboard Features

- **Real-time Sensor Monitoring**: Live gauge charts for temperature, humidity, smoke density, CO level, and gas level
- **Historical Data Visualization**: Time series charts with configurable time ranges (1 hour, 24 hours, 7 days)
- **Alert Management**: Real-time alert detection and display with severity levels
- **Data Quality Monitoring**: Detection of missing data and quality issues
- **Storage Metadata Monitoring**: Comprehensive tracking of Redis flush operations and storage efficiency

### Storage Metadata Dashboard (New)

- **Summary Metrics**: Total flushes, records processed, average processing time, recent activity
- **Detailed View**: Recent flushes table with filtering and search capabilities
- **Storage Type Breakdown**: Visual charts showing flush distribution by type
- **Performance Tracking**: Processing duration, success rates, and error counts
- **Filtering & Search**: Date range, storage type, and additional info search

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

## 📈 Performance & Monitoring

### Redis Metrics

- **Sensor Data Count**: Redis에 저장된 현재 센서 데이터 개수
- **Flush Interval**: 설정된 Redis flush 간격 (기본값: 60초)
- **Connection Status**: Redis 연결 상태 및 응답 시간

### Storage Metadata Metrics (New)

- **Total Flushes**: 전체 flush 횟수
- **Records Processed**: 처리된 총 레코드 수
- **Average Processing Time**: 평균 처리 시간 (밀리초)
- **Storage Type Breakdown**: 스토리지 타입별 flush 분포
- **Recent Activity**: 최근 24시간 내 flush 활동

### Event Publishing

- **Anomaly Events**: 이상치 탐지 시 즉시 발행 (`sensorDataAnomalyDetected`)
- **Data Saved Events**: Redis flush 시에만 발행 (`sensorDataSaved`)
- **Batch Events**: 배치 업로드 시 발행

### Storage Efficiency

- **Real-time Storage**: Redis를 통한 빠른 데이터 접근
- **Batch Persistence**: 주기적인 로컬 스토리지 flush로 데이터 영속성 보장
- **Memory Management**: flush 후 Redis 데이터 자동 정리
- **Metadata Tracking**: 모든 flush 작업의 메타데이터를 PostgreSQL에 저장하여 추적 가능

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

- `datalake.sensorDataAnomalyDetected` - Anomaly detection events
- `datalake.sensorDataSaved` - Data saved to storage events
- `datalake.sensorData` - Legacy sensor data events (deprecated)

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

````bash
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
curl http://localhost:8084/storage/batches

### Mock Data Scheduler Control

```bash
# Check scheduler status
curl http://localhost:8084/scheduler/mock/status

# Start the scheduler
curl -X POST http://localhost:8084/scheduler/mock/start

# Stop the scheduler
curl -X POST http://localhost:8084/scheduler/mock/stop

# Restart the scheduler
curl -X POST http://localhost:8084/scheduler/mock/restart

# Force process mock data once (even if scheduler is stopped)
curl -X POST http://localhost:8084/scheduler/mock/force-process
curl http://localhost:8084/stats

# Manually trigger batch upload
curl -X POST http://localhost:8084/trigger-batch-upload

# View uploaded batches (MockStorage only)
curl http://localhost:8084/storage/batches
````

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

## 🔄 Data Processing Flow

### 1. Real-time Data Ingestion

```bash
# Mock Server에서 실시간 데이터 수신 및 Redis 저장
curl -X POST http://localhost:8080/ingest

# 외부 API에서 데이터 수신 및 Redis 저장
curl -X POST http://localhost:8080/ingest/external \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "sensor_001",
    "facility_id": "facility_001",
    "measured_at": "2024-01-01T12:00:00Z",
    "temperature": 25.5,
    "humidity": 60.0
  }'
```

### 2. Redis Data Management

```bash
# Redis 상태 및 센서 데이터 개수 확인
curl http://localhost:8080/redis/status

# 강제 Redis flush 실행
curl -X POST http://localhost:8080/trigger-redis-flush
```

### 3. Monitoring & Statistics

```bash
# 서비스 통계 확인 (Redis 데이터 개수 포함)
curl http://localhost:8080/stats

# 배치 업로드 강제 실행
curl -X POST http://localhost:8080/trigger-batch-upload
```

## 📡 Event Publishing Rules

### Kafka Event Types

#### 1. sensorDataAnomalyDetected

- **When**: 이상치 탐지 시 즉시 발행
- **Topic**: `datalake.sensorDataAnomalyDetected`
- **Usage**: 실시간 알림 및 경고 시스템

#### 2. sensorDataSaved ⚠️ IMPORTANT

- **When**: Redis flush 시에만 발행 (1분 간격)
- **Topic**: `datalake.sensorDataSaved`
- **Usage**: 데이터 영속성 확인 및 배치 처리
- **NOT for**: 실시간 데이터 수신 시

#### 3. Legacy sensorData (Deprecated)

- **When**: 사용하지 않음 (하위 호환성 유지)
- **Topic**: `datalake.sensorData`
- **Note**: 이 메서드는 Redis flush 시에만 사용되어야 함

### Event Flow Diagram

```
Real-time Data → Redis Storage → Periodic Flush (1min) → Local Storage → sensorDataSaved Event
     ↓
Anomaly Detection → sensorDataAnomalyDetected Event (Immediate)
```

### Common Mistakes to Avoid

❌ **Don't**: Call `publish_data_saved` during real-time data ingestion
✅ **Do**: Call `publish_data_saved` only during Redis flush operations
❌ **Don't**: Use `publish_sensor_data` for new implementations
✅ **Do**: Use `publish_data_saved` for data persistence events
