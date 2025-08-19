# ControlTower

Central hub service providing read-only APIs for IoT fire monitoring data. no db for now

## 🚀 Quick Start

### Build

```bash
# With Maven
mvn clean package

# With Docker
docker build -t fire-iot-controltower .
```

### Run

```bash
# Local development
mvn spring-boot:run

# With Docker
docker run -d --name controltower --network infra_fire-iot-network -p 8082:8080 \
  -e POSTGRES_URL=jdbc:postgresql://fire-iot-postgres:5432/core \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres fire-iot-controltower
```

### Test

```bash
# Health check
curl http://localhost:8082/healthz

# API documentation
open http://localhost:8082/swagger-ui.html
```

## 📊 APIs

- `GET /api/v1/healthz` - Health check
- `GET /api/v1/alerts` - List alerts with pagination
- `GET /api/v1/stations/latest` - Latest station data
- `GET /api/v1/stations/{id}/latest` - Specific station data

## 🔧 Development

### Database Migration

```bash
# Run migrations
mvn flyway:migrate

# Check migration status
mvn flyway:info
```

### Testing

```bash
# Unit tests
mvn test

# Integration tests
mvn test -Dspring.profiles.active=test
```

## 📁 Structure

```
src/
├── main/
│   ├── java/com/fireiot/controltower/
│   │   ├── ControlTowerApplication.java
│   │   ├── controllers/     # REST controllers
│   │   ├── services/        # Business logic
│   │   ├── repositories/    # Data access
│   │   └── models/          # Entities & DTOs
│   └── resources/
│       ├── application.yml  # Configuration
│       └── db/migration/    # Flyway migrations
└── test/                    # Tests
```
