# Infrastructure

Infrastructure configuration and deployment scripts for Fire IoT MSA.

## 📁 Structure

```
infra/
├── env.local            # Local environment variables
├── env.cloud            # Cloud environment variables
├── aca/                 # Azure Container Apps
│   ├── main.bicep       # Bicep template
│   ├── parameters.bicepparam
│   ├── deploy.sh        # Single deployment script
│   └── README.md        # Detailed deployment guide
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

### Quick Deployment

Deploy everything with a single command:

```bash
cd infra/aca
chmod +x deploy.sh
./deploy.sh
```

### What Gets Deployed

The deployment creates:

- **4 Web Apps** (ControlTower, FacilityManagement, DataLake, Alert)
- **Event Hubs** for message queuing
- **PostgreSQL Database** with private networking
- **Redis Cache** for caching
- **Application Insights** for monitoring
- **Virtual Network** for security

### Prerequisites

1. **Azure CLI** installed and logged in
2. **Docker** installed
3. **Docker Hub images** pushed:
   - `johnha97/controltower:latest`
   - `johnha97/facilitymanagement:latest`
   - `johnha97/datalake:latest`
   - `johnha97/alert:latest`

### Build Images (if needed)

```bash
# Build and push each service
docker build -t johnha97/controltower:latest ./services/controltower/
docker push johnha97/controltower:latest

docker build -t johnha97/facilitymanagement:latest ./services/facilitymanagement/
docker push johnha97/facilitymanagement:latest

docker build -t johnha97/datalake:latest ./services/datalake/
docker push johnha97/datalake:latest

docker build -t johnha97/alert:latest ./services/alert/
docker push johnha97/alert:latest
```

### Check Deployment

```bash
# List all deployments
az deployment group list --resource-group Project_Team_05

# Get latest deployment outputs
az deployment group show \
  --resource-group Project_Team_05 \
  --name fire-iot-$(date +%Y%m%d-%H%M%S) \
  --query properties.outputs
```

## 🔧 Configuration

### Environment Variables

- `env.local` - Local development settings
- `env.cloud` - Cloud deployment settings

### Ports (Local Development)

- **DataLake PostgreSQL**: 5433 (local), 5432 (container)
- **ControlTower PostgreSQL**: 5434 (local), 5432 (container)
- **FacilityManagement PostgreSQL**: 5435 (local), 5432 (container)
- **Redis**: 6379
- **Kafka**: 9092
- **Kafka UI**: 8090
- **PgAdmin**: 8091

## 📊 Monitoring

### Local Access Points

- **Kafka UI**: http://localhost:8090
- **PgAdmin**: http://localhost:8091
- **PostgreSQL**: localhost:5433

### Azure Monitoring

- **Azure Portal** → App Services
- **Application Insights** → Live Metrics
- **Log Analytics** → Log queries

### Health Checks

```bash
# Local PostgreSQL Databases
docker exec fire-iot-postgres-datalake pg_isready -U postgres
docker exec fire-iot-postgres-controltower pg_isready -U postgres
docker exec fire-iot-postgres-facilitymanagement pg_isready -U postgres

# Local Redis
docker exec fire-iot-redis redis-cli ping

# Local Kafka
docker exec fire-iot-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Azure Web Apps
curl https://app-dev-controltower.azurewebsites.net/health
curl https://app-dev-facilitymanagement.azurewebsites.net/health
curl https://app-dev-datalake.azurewebsites.net/health
curl https://app-dev-alert.azurewebsites.net/health
```

## 🧹 Cleanup

### Local Cleanup

```bash
docker-compose down -v
```

### Azure Cleanup

```bash
az group delete --name Project_Team_05 --yes --no-wait
```

## 📞 Troubleshooting

### Common Issues

1. **Docker images not found**: Build and push to Docker Hub first
2. **Azure login issues**: Run `az login` manually
3. **Resource group creation fails**: Check Azure permissions
4. **Web Apps not starting**: Check logs in Azure Portal

### Useful Commands

```bash
# Check deployment status
az deployment group list --resource-group Project_Team_05

# View Web App logs
az webapp log tail --name app-dev-controltower --resource-group Project_Team_05

# Check Event Hubs
az eventhubs eventhub list --namespace-name fire-iot-eventhub-dev --resource-group Project_Team_05
```
