# Fire IoT MSA

IoT fire monitoring system with real-time data processing and alerts.

## Service Links

### Core Services

- **[DataLake](./services/datalake/README.md)** - Gets sensor data, finds problems, shows dashboard
- **[ControlTower](./services/controltower/README.md)** - Main service that gives data to other services
- **[FacilityManagement](./services/facilitymanagement/README.md)** - Manages equipment and maintenance info
- **[Alert](./services/alert/README.md)** - Sends alerts when problems found
- **[MockServer](./services/mock-server/README.md)** - Makes fake data for testing

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

Mock Server needs:
- Nothing (standalone)
```

### Communication Patterns

```
DataLake → Kafka → ControlTower (sensor data)
DataLake → Kafka → Alert (anomaly alerts)
ControlTower → Kafka → Alert (warning alerts)
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
- **ControlTower API**: http://localhost:8082
- **FacilityManagement API**: http://localhost:8083
- **Mock Server**: http://localhost:8001
- **Kafka UI**: http://localhost:8090

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
```

### Local Development

```bash
# DataLake
cd services/datalake
python -m uvicorn app.main:app --reload

# ControlTower
cd services/controltower
./mvnw spring-boot:run

# FacilityManagement
cd services/facilitymanagement
./mvnw spring-boot:run
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
