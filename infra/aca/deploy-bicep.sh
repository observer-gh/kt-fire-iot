#!/bin/bash

# Bicep Deployment Script for Azure Container Apps
# This script deploys the Fire IoT MSA using Bicep templates

set -e

# Configuration
RESOURCE_GROUP="fire-iot-rg"
LOCATION="eastus"
ENVIRONMENT=${1:-dev}
DOCKER_HUB_ORG=${2:-"your-dockerhub-org"}
IMAGE_TAG=${3:-latest}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying Fire IoT MSA using Bicep${NC}"
echo -e "${YELLOW}📦 Environment: $ENVIRONMENT${NC}"
echo -e "${YELLOW}🏢 Docker Hub Org: $DOCKER_HUB_ORG${NC}"
echo -e "${YELLOW}🏷️  Image Tag: $IMAGE_TAG${NC}"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Bicep is installed
if ! command -v bicep &> /dev/null; then
    echo -e "${RED}❌ Bicep is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Azure. Please run 'az login' first.${NC}"
    exit 1
fi

# Create resource group if it doesn't exist
echo -e "${YELLOW}📦 Creating resource group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Validate Bicep template
echo -e "${YELLOW}🔍 Validating Bicep template...${NC}"
bicep build infra/aca/main.bicep

# Deploy using Bicep
echo -e "${YELLOW}🚀 Deploying infrastructure...${NC}"
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file infra/aca/main.bicep \
    --parameters \
        resourceGroupName=$RESOURCE_GROUP \
        location=$LOCATION \
        environment=$ENVIRONMENT \
        dockerHubOrg=$DOCKER_HUB_ORG \
        imageTag=$IMAGE_TAG \
        postgresConnectionString="$POSTGRES_CONNECTION_STRING" \
        redisConnectionString="$REDIS_CONNECTION_STRING" \
        eventHubConnectionString="$EVENTHUB_CONNECTION_STRING" \
        otelEndpoint="$OTEL_ENDPOINT" \
    --output table

# Get deployment outputs
echo -e "${GREEN}📋 Service URLs:${NC}"
CONTROLTOWER_URL=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name main \
    --query properties.outputs.controlTowerUrl.value \
    --output tsv)
echo -e "${GREEN}   ControlTower: $CONTROLTOWER_URL${NC}"

FACILITYMANAGEMENT_URL=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name main \
    --query properties.outputs.facilityManagementUrl.value \
    --output tsv)
echo -e "${GREEN}   FacilityManagement: $FACILITYMANAGEMENT_URL${NC}"

DATALAKE_URL=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name main \
    --query properties.outputs.dataLakeUrl.value \
    --output tsv)
echo -e "${GREEN}   DataLake: $DATALAKE_URL${NC}"

echo -e "${GREEN}🎉 Bicep deployment completed successfully!${NC}"
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "${YELLOW}   1. Set up Azure Database for PostgreSQL${NC}"
echo -e "${YELLOW}   2. Set up Azure Cache for Redis${NC}"
echo -e "${YELLOW}   3. Set up Azure Event Hubs${NC}"
echo -e "${YELLOW}   4. Configure connection strings in environment variables${NC}"
