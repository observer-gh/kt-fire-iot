# Infrastructure

Infrastructure configuration and deployment scripts for Fire IoT MSA.

## 📁 Structure

```
infra/
├── compose.local.yml     # Local development environment
├── env.local            # Local environment variables
├── env.cloud            # Cloud environment variables
├── start-local.sh       # Local startup script
├── aca/                 # Azure Container Apps
│   ├── main.bicep       # Bicep template
│   ├── parameters.dev.bicepparam
│   ├── deploy-bicep.sh  # Deployment script
│   └── build-and-push.sh # Image build script
└── README.md
```

## 🚀 Local Development

### Start Infrastructure

```bash
./infra/start-local.sh
```

### Stop Infrastructure

```bash
docker-compose -f infra/compose.local.yml down
```

### Check Status

```bash
docker-compose -f infra/compose.local.yml ps
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

- **PostgreSQL**: 5433 (local), 5432 (container)
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
# PostgreSQL
docker exec fire-iot-postgres pg_isready -U postgres

# Redis
docker exec fire-iot-redis redis-cli ping

# Kafka
docker exec fire-iot-kafka kafka-topics --bootstrap-server localhost:9092 --list
```
