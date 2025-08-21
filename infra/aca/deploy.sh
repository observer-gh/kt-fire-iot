#!/bin/bash

# Fire IoT Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="Project_Team_05"
LOCATION="koreacentral"
ENVIRONMENT="dev"
DOCKER_HUB_ORG="johnha97"
IMAGE_TAG="latest"
DEPLOYMENT_NAME="fire-iot-$(date +%Y%m%d-%H%M%S)"

echo -e "${GREEN}🚀 Starting Fire IoT Deployment${NC}"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Please install Azure CLI first.${NC}"
    exit 1
fi


if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Check Azure login status and login if needed
echo -e "${YELLOW}🔐 Checking Azure login status...${NC}"
if ! az account show --only-show-errors > /dev/null 2>&1; then
    echo -e "${YELLOW}Not logged in. Logging into Azure...${NC}"
    az login --only-show-errors
else
    echo -e "${GREEN}✅ Already logged into Azure${NC}"
fi

# Create resource group
echo -e "${YELLOW}📦 Creating resource group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Check Docker images exist in Docker Hub (parallel)
echo -e "${YELLOW}🐳 Checking Docker images in Docker Hub (parallel)...${NC}"

# Define services with their image names
services=(
    "controltower:kt-fire-iot-controltower"
    "facilitymanagement:kt-fire-iot-facilitymanagement"
    "datalake-api:kt-fire-iot-datalake-api"
    "datalake-dashboard:kt-fire-iot-datalake-dashboard"
    "alert:kt-fire-iot-alert"
    "mock-server:kt-fire-iot-mock-server"
    "videoanalysis:kt-fire-iot-videoanalysis"
)

# Function to check a single image
check_image() {
    local service_info=$1
    local service=$(echo "$service_info" | cut -d: -f1)
    local image_name=$(echo "$service_info" | cut -d: -f2)
    
    if docker manifest inspect $DOCKER_HUB_ORG/$image_name:$IMAGE_TAG > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Found $service ($image_name)${NC}"
        return 0
    else
        echo -e "${RED}❌ Missing $service ($image_name)${NC}"
        return 1
    fi
}

# Run all checks in parallel
pids=()
for service_info in "${services[@]}"; do
    check_image "$service_info" &
    pids+=($!)
done

# Wait for all checks to complete
failed=0
for pid in "${pids[@]}"; do
    if ! wait $pid; then
        failed=1
    fi
done

if [ $failed -eq 1 ]; then
    echo -e "${RED}❌ Some Docker images are missing from Docker Hub${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All Docker images found!${NC}"

# Deploy infrastructure
echo -e "${YELLOW}🏗️ Deploying infrastructure...${NC}"
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --name $DEPLOYMENT_NAME \
    --template-file main.bicep \
    --parameters parameters.bicepparam \
    --output table

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"

# Get outputs
echo -e "${YELLOW}📊 Getting deployment outputs...${NC}"
az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name $DEPLOYMENT_NAME \
    --query properties.outputs \
    --output table

echo -e "${GREEN}🎉 All done! Your Fire IoT platform is now deployed.${NC}"
