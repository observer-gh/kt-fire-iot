# Infrastructure

Infrastructure configuration and deployment scripts for Fire IoT MSA.

## 📁 Structure

```
infra/
├── env.local            # Local environment variables
├── env.cloud            # Cloud environment variables
├── aca/                 # Azure Container Apps
│   ├── main.bicep       # Bicep template
│   ├── parameters.dev.bicepparam
│   ├── deploy-bicep.sh  # Deployment script
│   └── build-and-push.sh # Image build script
└── README.md
```

## 🚀 Local Development

### Start All Services

```bash
docker-compose up -d
```

### Stop All Services

```bash
docker-compose down
```

### Check Status

```bash
docker-compose ps
```

## ☁️ Azure Deployment

### Build and Push Images

```bash
./infra/aca/build-and-push.sh v1.0.0
```

### Deploy to Azure

```bash
./infra/aca/deploy-bicep.sh dev your-dockerhub-org v1.0.0
```

### Check Deployment

```bash
az containerapp list --resource-group fire-iot-rg
```

## 🔧 Configuration

### Environment Variables

- `env.local` - Local development settings
- `env.cloud` - Cloud deployment settings

### Ports

- **DataLake PostgreSQL**: 5433 (local), 5432 (container)
- **ControlTower PostgreSQL**: 5434 (local), 5432 (container)
- **FacilityManagement PostgreSQL**: 5435 (local), 5432 (container)
- **Redis**: 6379
- **Kafka**: 9092
- **Kafka UI**: 8090
- **PgAdmin**: 8091

## 📊 Monitoring

### Access Points

- **Kafka UI**: http://localhost:8090
- **PgAdmin**: http://localhost:8091
- **PostgreSQL**: localhost:5433

### Health Checks

```bash
# PostgreSQL Databases
docker exec fire-iot-postgres-datalake pg_isready -U postgres
docker exec fire-iot-postgres-controltower pg_isready -U postgres
docker exec fire-iot-postgres-facilitymanagement pg_isready -U postgres

# Redis
docker exec fire-iot-redis redis-cli ping

# Kafka
docker exec fire-iot-kafka kafka-topics --bootstrap-server localhost:9092 --list
```
