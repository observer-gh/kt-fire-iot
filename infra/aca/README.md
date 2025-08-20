# Fire IoT MSA - Azure Deployment

This directory contains Bicep templates and deployment scripts for deploying the Fire IoT Microservices Architecture to Azure.

## 🏗️ Infrastructure Components

The deployment creates the following Azure resources:

- **Azure Container Apps Environment** - Hosts all microservices
- **Azure Container Registry** - Stores Docker images
- **Azure Event Hubs** - Message broker for inter-service communication
- **Azure Database for PostgreSQL** - Primary database
- **Azure Cache for Redis** - Caching layer
- **Application Insights** - Monitoring and logging
- **Log Analytics Workspace** - Centralized logging
- **Virtual Network** - Network isolation and security

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Azure CLI** installed and configured
2. **Bicep** CLI installed
3. **Docker** installed and running
4. **PostgreSQL client** (for database setup)
5. **Azure subscription** with appropriate permissions

### Install Prerequisites

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Bicep
az bicep install

# Install Docker (if not already installed)
# macOS: brew install docker
# Ubuntu: sudo apt-get install docker.io

# Install PostgreSQL client
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql-client
```

## 🚀 Deployment

### Single Command Deployment

Run the deployment script that handles everything:

```bash
# Make script executable
chmod +x deploy.sh

# Basic deployment with defaults
./deploy.sh

# Custom deployment
./deploy.sh your-dockerhub-org v1.0.0 YourSecurePassword123!
```

### What the Script Does

The `deploy.sh` script performs these steps automatically:

1. **Prerequisites Check** - Verifies Azure CLI, Bicep, Docker, and Azure login
2. **Infrastructure Deployment** - Deploys all Azure resources using Bicep
3. **Docker Image Building** - Builds and pushes all microservice images to ACR
4. **Database Setup** - Creates PostgreSQL database and schema
5. **Verification** - Tests service endpoints and displays results

## 📁 Files Overview

| File                    | Purpose                                       |
| ----------------------- | --------------------------------------------- |
| `deploy.sh`             | Single deployment script - handles everything |
| `main.bicep`            | Bicep template defining all Azure resources   |
| `parameters.bicepparam` | Configuration parameters                      |

## 🔧 Configuration

### Configuration Management

The deployment uses a **single parameter file** for simplicity:

- **`parameters.bicepparam`** - All configuration settings

The script reads all configuration from this file, making it easy to manage and modify settings.

### Custom Parameters

Edit `parameters.dev.bicepparam` to customize:

```bicep
param resourceGroupName = 'Project_Team_05'
param location = 'eastus'
param environment = 'dev'
param dockerHubOrg = 'your-dockerhub-org'
param imageTag = 'latest'
param postgresAdminUsername = 'fireiot_admin'
param postgresAdminPassword = 'YourSecurePassword123!'
```

## 🗄️ Database Schema

The deployment creates a PostgreSQL database with these tables:

- **`sensor_data`** - IoT sensor readings (DataLake service)
- **`alerts`** - Alert history and status (Alert service)
- **`equipment`** - Equipment inventory and status (FacilityManagement service)
- **`maintenance_requests`** - Maintenance scheduling (FacilityManagement service)

## 🔍 Monitoring

After deployment, monitor your services:

1. **Azure Portal** → Container Apps
2. **Application Insights** → Live Metrics
3. **Log Analytics** → Log queries
4. **Event Hubs** → Throughput metrics

## 🧪 Testing

Test your deployed services:

```bash
# Get service URLs
az deployment group show \
  --resource-group Project_Team_05 \
  --name main \
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

1. **Bicep validation errors**: Run `bicep build main.bicep` to check syntax
2. **Docker build failures**: Ensure Docker is running and images are accessible
3. **Database connection issues**: Check PostgreSQL server is running and accessible
4. **Container Apps not starting**: Check logs in Azure Portal

### Useful Commands

```bash
# Check deployment status
az deployment group show --resource-group Project_Team_05 --name main

# View Container Apps logs
az containerapp logs show --name app-dev-controltower --resource-group Project_Team_05

# Check Event Hubs
az eventhubs eventhub list --namespace-name fire-iot-eventhub-dev --resource-group Project_Team_05
```

## 🔐 Security Notes

- Change default passwords in production
- Use Azure Key Vault for secrets management
- Enable private endpoints for database access
- Configure network security groups
- Enable Azure Defender for Containers

## 📈 Scaling

The deployment includes auto-scaling configuration:

- **Min replicas**: 1
- **Max replicas**: 3-5 (depending on service)
- **CPU**: 0.5-1.0 cores
- **Memory**: 1-2 GB

Adjust these values in `main.bicep` for your needs.
