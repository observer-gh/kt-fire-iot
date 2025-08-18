# StaticManagement

Master data management service for fire department equipment and maintenance records.

## 🚀 Quick Start

### Build

```bash
# With Maven
mvn clean package

# With Docker
docker build -t fire-iot-staticmanagement .
```

### Run

```bash
# Local development
mvn spring-boot:run

# With Docker
docker run -d --name staticmanagement --network infra_fire-iot-network -p 8083:8080 \
  -e POSTGRES_URL=jdbc:postgresql://fire-iot-postgres:5432/core \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres fire-iot-staticmanagement
```

### Test

```bash
# Health check
curl http://localhost:8083/healthz

# API documentation
open http://localhost:8083/swagger-ui.html
```

## 📊 APIs

- `GET /api/v1/healthz` - Health check
- `GET /api/v1/equipment` - List equipment
- `POST /api/v1/equipment` - Register equipment
- `GET /api/v1/equipment/{id}` - Get equipment details
- `PUT /api/v1/equipment/{id}` - Update equipment
- `GET /api/v1/maintenance` - List maintenance records
- `POST /api/v1/maintenance` - Record maintenance

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
│   ├── java/com/fireiot/staticmanagement/
│   │   ├── StaticManagementApplication.java
│   │   ├── controllers/     # REST controllers
│   │   ├── services/        # Business logic
│   │   ├── repositories/    # Data access
│   │   └── models/          # Entities & DTOs
│   └── resources/
│       ├── application.yml  # Configuration
│       └── db/migration/    # Flyway migrations
└── test/                    # Tests
```
