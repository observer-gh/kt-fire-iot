# Fire IoT MSA - Azure Deployment

This directory contains Bicep templates and deployment scripts for deploying the Fire IoT Microservices Architecture to Azure.

## 🏗️ Infrastructure Components

The deployment creates the following Azure resources:

- **Azure App Service Plan** - Hosts all microservices as Web Apps
- **Azure Event Hubs** - Message broker for inter-service communication
- **Azure Database for PostgreSQL** - Primary database with private networking
- **Azure Cache for Redis** - Caching layer
- **Application Insights** - Monitoring and logging
- **Log Analytics Workspace** - Centralized logging
- **Virtual Network** - Network isolation and security

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Azure CLI** installed and configured
2. **Docker** installed and running
3. **Azure subscription** with appropriate permissions
4. **Docker Hub account** with images pushed

### Install Prerequisites

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Docker (if not already installed)
# macOS: brew install docker
# Ubuntu: sudo apt-get install docker.io
```

## 🚀 Quick Deployment

### Single Command Deployment

Run the deployment script that handles everything:

```bash
# Make script executable
chmod +x deploy.sh

# Deploy with default settings
./deploy.sh
```

### What the Script Does

The `deploy.sh` script performs these steps automatically:

1. **Prerequisites Check** - Verifies Azure CLI, Docker, and Azure login status
2. **Azure Login** - Logs in only if not already authenticated
3. **Resource Group Creation** - Creates the resource group if it doesn't exist
4. **Docker Image Verification** - Checks if required images exist in Docker Hub
5. **Infrastructure Deployment** - Deploys all Azure resources using Bicep
6. **Output Display** - Shows deployment outputs (URLs, connection strings, etc.)

## 📁 Files Overview

| File                    | Purpose                                       |
| ----------------------- | --------------------------------------------- |
| `deploy.sh`             | Single deployment script - handles everything |
| `main.bicep`            | Bicep template defining all Azure resources   |
| `parameters.bicepparam` | Configuration parameters                      |

## 🔧 Configuration

### Current Configuration

The deployment uses these default settings:

```bash
RESOURCE_GROUP="Project_Team_05"
LOCATION="koreacentral"
ENVIRONMENT="dev"
DOCKER_HUB_ORG="johnha97"
IMAGE_TAG="latest"
```

### Custom Parameters

Edit `parameters.bicepparam` to customize:

```bicep
param location = 'koreacentral'
param environment = 'dev'
param dockerHubOrg = 'johnha97'
param imageTag = 'latest'
param postgresAdminUsername = 'fireiot_admin'
param postgresAdminPassword = 'YourSecurePassword123!'
```

## 🐳 Docker Images

The deployment expects these images to exist in Docker Hub:

- `johnha97/controltower:latest`
- `johnha97/facilitymanagement:latest`
- `johnha97/datalake:latest`
- `johnha97/alert:latest`

### Building Images (if needed)

If images don't exist, build and push them first:

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

## 🗄️ Database Schema

The deployment creates a PostgreSQL database with these tables:

- **`sensor_data`** - IoT sensor readings (DataLake service)
- **`alerts`** - Alert history and status (Alert service)
- **`equipment`** - Equipment inventory and status (FacilityManagement service)
- **`maintenance_requests`** - Maintenance scheduling (FacilityManagement service)

## 🔍 Monitoring

After deployment, monitor your services:

1. **Azure Portal** → App Services
2. **Application Insights** → Live Metrics
3. **Log Analytics** → Log queries
4. **Event Hubs** → Throughput metrics

## 🧪 Testing

Test your deployed services:

```bash
# Get service URLs from deployment outputs
az deployment group show \
  --resource-group Project_Team_05 \
  --name fire-iot-$(date +%Y%m%d-%H%M%S) \
  --query properties.outputs

# Test health endpoints
curl https://your-controltower-url/health
curl https://your-facilitymanagement-url/health
curl https://your-datalake-url/health
```

## 🧹 Cleanup

To remove all resources:

```bash
az group delete --name Project_Team_05 --yes --no-wait
```

## 📞 Troubleshooting

### Common Issues

1. **Docker images not found**: Build and push images to Docker Hub first
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

## 🔐 Security Notes

- Change default passwords in production
- Use Azure Key Vault for secrets management
- Enable private endpoints for database access
- Configure network security groups
- Enable Azure Defender for App Services

## 📈 Scaling

The deployment uses Azure App Service with these settings:

- **App Service Plan**: Basic B1 (Linux)
- **Auto-scaling**: Configured per service
- **SSL**: HTTPS enabled by default

Adjust these values in `main.bicep` for your needs.
