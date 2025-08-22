# Fire IoT MSA

IoT fire monitoring system with real-time data processing and alerts.

## Service Links

### Core Services

- **[DataLake](./services/datalake/README.md)** - Gets sensor data, finds problems, shows dashboard

  - **API Service**: Port 8084 - Main data processing and storage service
  - **Dashboard**: Port 8501 - Streamlit-based real-time monitoring dashboard
  - **Technology**: Python, FastAPI, PostgreSQL, Redis, Kafka
  - **Features**: Real-time sensor data processing, anomaly detection, data storage, dashboard visualization

- **[ControlTower](./services/controltower/README.md)** - Main service that gives data to other services

  - **Port**: 8082
  - **Technology**: Java, Spring Boot
  - **Features**: Central data distribution, service orchestration, Kafka message routing

- **[FacilityManagement](./services/facilitymanagement/README.md)** - Manages equipment and maintenance info

  - **Port**: 8083
  - **Technology**: Java, Spring Boot, PostgreSQL
  - **Features**: Equipment management, maintenance scheduling, facility information

- **[Alert](./services/alert/README.md)** - Sends alerts when problems found

  - **Port**: No external port (internal service)
  - **Technology**: Python, Kafka consumer, Redis, Slack integration
  - **Features**: Real-time alert processing, Slack notifications, alert deduplication

- **[VideoAnalysis](./services/videoanalysis/README.md)** - AI-powered video analysis for fire detection

  - **Port**: 8085
  - **Technology**: Python, Azure Computer Vision, OpenCV
  - **Features**: Real-time video analysis, fire detection, frame processing, Kafka integration

- **[MockServer](./services/mock-server/README.md)** - Makes fake data for testing
  - **Port**: 8001
  - **Technology**: Java, Spring Boot
  - **Features**: Sensor data simulation, CCTV streaming simulation, test data generation

### Infrastructure Services

- **PostgreSQL DataLake**: Port 5433 - Main sensor data storage
- **PostgreSQL FacilityManagement**: Port 5435 - Equipment and maintenance data
- **Redis**: Port 6379 - Caching and alert deduplication
- **Kafka**: Port 9092 - Message broker for service communication
- **Zookeeper**: Port 2181 - Kafka cluster coordination
- **Kafka UI**: Port 8090 - Kafka management interface
- **PgAdmin**: Port 8091 - Database management interface

## Architecture Diagram

![Arc](./architecture.jpg)

## ADR (Architecture Decision Records)

### ADR-001: Use Kafka for Service Communication

- **Problem**: Services need to talk to each other
- **Decision**: Use Kafka for messages between services
- **Reason**: Kafka has seamless integration with Azure Event hub.

### ADR-002: Separate Databases per Service

- **Problem**: Where to store data for each service
- **Decision**: Each service has its own PostgreSQL database if needed
- **Reason**: Services can change data without affecting others

### ADR-003: Microservice Architecture with Event-Driven Communication

- **Problem**: Need for scalable, maintainable system architecture
- **Decision**: Implement MSA with Kafka-based event streaming
- **Reason**: Enables independent service development, deployment, and scaling

## Data Architecture

![erd](./erd.png)

### Database Tables (PostgreSQL)

**DataLake Database:**

```
realtime
- id (PK)
- equipment_id
- facility_id
- temperature, humidity, smoke_density, co_level, gas_level
- measured_at
- created_at

alert
- id (PK)
- equipment_id
- alert_type (WARNING, EMERGENCY)
- message
- created_at
```

**FacilityManagement Database:**

```
equipment
- id (PK)
- name, type, location
- status (ACTIVE, INACTIVE, MAINTENANCE)
- created_at

maintenance
- id (PK)
- equipment_id (FK)
- type, description
- scheduled_date, completed_date
- status (SCHEDULED, IN_PROGRESS, COMPLETED)
```

### Kafka Topics

```
dataLake.sensorDataAnomalyDetected
- equipment_id, facility_id, alert_type, message, timestamp

dataLake.sensorDataSaved
- equipment_id, facility_id, data, timestamp

controlTower.warningAlertIssued
- alert_id, message, severity, timestamp

controlTower.emergencyAlertIssued
- alert_id, message, severity, timestamp

alert.alertSendSuccess
- alert_id, message, timestamp

alert.alertSendFail
- alert_id, message, severity, timestamp
```

## Error Handling

### Strategy 1: Simple Retry

- If service call fails, try again 3 times
- Wait 1 second between tries
- If still fails, log error and stop

### Strategy 2: Circuit Breaker

- If service fails 5 times in 1 minute, stop trying for 30 seconds
- Let service recover, then try again
- Prevents system overload

### Implementation Examples

### Health Checks

Each service has `/healthz` endpoint:

```
GET /healthz
Response: {"status": "healthy", "timestamp": "2024-01-01T12:00:00Z"}
```

### Error Logging

- All errors logged with timestamp and service name
- Critical errors sent to monitoring system
- Database connection errors trigger retry

## MSA Board

### Service Dependencies

```
DataLake needs:
- PostgreSQL (store data)
- Redis (cache)
- Kafka (send messages)
- Mock Server (get data)

ControlTower needs:
- Kafka (get messages)
- No database (read-only)

FacilityManagement needs:
- PostgreSQL (store equipment data)

Alert needs:
- Kafka (get messages)
- Redis (deduplication)
- Slack (send notifications)

VideoAnalysis needs:
- Kafka (send analysis results)
- Mock Server (get video streams)
- Azure Computer Vision API

Mock Server needs:
- Nothing (standalone)
```

### Communication Patterns

```
DataLake → Kafka → ControlTower (sensor data)
DataLake → Kafka → Alert (anomaly alerts)
ControlTower → Kafka → Alert (warning/emergency alerts)
VideoAnalysis → Kafka → Alert (fire detection alerts)
FacilityManagement → Kafka → Alert (maintenance alerts)
```

## Quick Start

### Start Everything

```bash
docker-compose up -d
```

### Check Status

```bash
docker-compose ps
```

### Access Points

- **DataLake Dashboard**: http://localhost:8501
- **DataLake API**: http://localhost:8084
- **ControlTower API**: http://localhost:8082
- **FacilityManagement API**: http://localhost:8083
- **VideoAnalysis Service**: http://localhost:8085
- **Mock Server**: http://localhost:8001
- **Kafka UI**: http://localhost:8090
- **PgAdmin**: http://localhost:8091

### Stop Everything

```bash
docker-compose down
```

## Development

### Build Services

```bash
# Build all
docker-compose build

# Build specific service
docker-compose build datalake
docker-compose build controltower
docker-compose build facilitymanagement
docker-compose build alert
docker-compose build videoanalysis
docker-compose build mock-server
```

### Local Development

```bash
# DataLake API
cd services/datalake
python -m uvicorn app.main:app --reload --port 8084

# DataLake Dashboard
cd services/datalake
streamlit run run_dashboard.py --server.port 8501

# ControlTower
cd services/controltower
./mvnw spring-boot:run

# FacilityManagement
cd services/facilitymanagement
./mvnw spring-boot:run

# Alert Service
cd services/alert
python -m uvicorn app.main:app --reload

# VideoAnalysis
cd services/videoanalysis
python main.py

# Mock Server
cd services/mock-server
./mvnw spring-boot:run
```

## Service Health Monitoring

### Health Check Endpoints

- **DataLake API**: `http://localhost:8084/healthz`
- **ControlTower**: `http://localhost:8082/healthz`
- **FacilityManagement**: `http://localhost:8083/healthz`
- **VideoAnalysis**: `http://localhost:8085/healthz`
- **Mock Server**: `http://localhost:8001/healthz`

### Monitoring Commands

```bash
# Check all service statuses
docker-compose ps

# View service logs
docker-compose logs -f [service-name]

# Check specific service health
curl http://localhost:8084/healthz
curl http://localhost:8082/healthz
curl http://localhost:8083/healthz
curl http://localhost:8085/healthz
curl http://localhost:8001/healthz
```

## Deployment

### Local

```bash
docker-compose up -d
```

### Azure

```bash
cd infra/aca
./deploy.sh
```

## Technology Stack

### Backend Services

- **Python**: DataLake, Alert, VideoAnalysis
- **Java**: ControlTower, FacilityManagement, MockServer
- **Frameworks**: FastAPI, Spring Boot, Streamlit

### Infrastructure

- **Message Broker**: Apache Kafka
- **Databases**: PostgreSQL (multiple instances)
- **Cache**: Redis
- **Containerization**: Docker, Docker Compose

### External Services

- **Azure Computer Vision**: Video analysis and fire detection
- **Slack**: Alert notifications
- **Azure Event Hub**: Production message streaming (planned)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
