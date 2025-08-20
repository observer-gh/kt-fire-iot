#!/bin/bash

# Fire IoT MSA - Azure Deployment Script
# Single script to handle complete deployment including infrastructure, database, and verification

set -e

# Configuration - read from parameters file
DOCKER_HUB_ORG=${1:-"your-dockerhub-org"}
IMAGE_TAG=${2:-latest}
POSTGRES_PASSWORD=${3:-"YourSecurePassword123!"}

# Use single parameters file
PARAM_FILE="parameters.bicepparam"
if [ ! -f "$PARAM_FILE" ]; then
    echo "❌ Parameter file $PARAM_FILE not found!"
    exit 1
fi

# Extract values from bicepparam file (simple parsing)
LOCATION=$(grep "location" "$PARAM_FILE" | cut -d'=' -f2 | tr -d " '")
ENVIRONMENT=$(grep "environment" "$PARAM_FILE" | cut -d'=' -f2 | tr -d " '")

# Get resource group from Azure context (will be set by user)
RESOURCE_GROUP="Project_Team_05"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Fire IoT MSA - Azure Deployment${NC}"
echo -e "${BLUE}===================================${NC}"
echo -e "${YELLOW}🏢 Docker Hub Org: $DOCKER_HUB_ORG${NC}"
echo -e "${YELLOW}🏷️  Image Tag: $IMAGE_TAG${NC}"
echo -e "${YELLOW}📁 Resource Group: $RESOURCE_GROUP${NC}"
echo -e "${YELLOW}📍 Location: $LOCATION${NC}"
echo -e "${YELLOW}📦 Environment: $ENVIRONMENT${NC}"

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    # Check Bicep
    if ! command -v bicep &> /dev/null; then
        echo -e "${RED}❌ Bicep is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    # Check Azure login
    if ! az account show &> /dev/null; then
        echo -e "${YELLOW}⚠️  Not logged in to Azure. Please run 'az login' first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met!${NC}"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    echo -e "${YELLOW}🏗️  Deploying infrastructure...${NC}"
    
    # Create resource group if it doesn't exist
    echo -e "${YELLOW}📦 Creating resource group...${NC}"
    az group create --name $RESOURCE_GROUP --location $LOCATION --output none

    # Validate Bicep template
    echo -e "${YELLOW}🔍 Validating Bicep template...${NC}"
    bicep build main.bicep

    # Deploy using Bicep with parameters file
    echo -e "${YELLOW}🚀 Deploying infrastructure...${NC}"
    az deployment group create \
        --resource-group $RESOURCE_GROUP \
        --template-file main.bicep \
        --parameters $PARAM_FILE \
        --parameters \
            dockerHubOrg=$DOCKER_HUB_ORG \
            imageTag=$IMAGE_TAG \
            postgresAdminPassword=$POSTGRES_PASSWORD \
        --output table
}

# Function to build and push Docker images
build_and_push_images() {
    echo -e "${YELLOW}🐳 Building and pushing Docker images to Docker Hub...${NC}"
    
    # Build and push images
    local services=("controltower" "facilitymanagement" "datalake" "alert")
    
    for service in "${services[@]}"; do
        echo -e "${YELLOW}   Building $service...${NC}"
        docker build -t $DOCKER_HUB_ORG/$service:$IMAGE_TAG services/$service/
        docker push $DOCKER_HUB_ORG/$service:$IMAGE_TAG
    done
}

# Function to setup database
setup_database() {
    echo -e "${YELLOW}🗄️  Setting up database...${NC}"
    
    # Get PostgreSQL server details
    POSTGRES_FQDN=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name main \
        --query properties.outputs.postgresServerFqdn.value \
        --output tsv)
    
    echo -e "${GREEN}   PostgreSQL Server: $POSTGRES_FQDN${NC}"
    
    # Check if psql is installed
    if ! command -v psql &> /dev/null; then
        echo -e "${YELLOW}⚠️  psql is not installed. Installing PostgreSQL client...${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install postgresql
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y postgresql-client
        else
            echo -e "${RED}❌ Please install PostgreSQL client manually${NC}"
            exit 1
        fi
    fi
    
    # Create database and tables
    echo -e "${YELLOW}🗄️  Creating database and tables...${NC}"
    
    # Create the fireiot database
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_FQDN -U fireiot_admin -d postgres -c "
    CREATE DATABASE fireiot;
    "
    
    # Create tables (basic schema)
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_FQDN -U fireiot_admin -d fireiot -c "
    -- Sensor Data Table
    CREATE TABLE IF NOT EXISTS sensor_data (
        id SERIAL PRIMARY KEY,
        sensor_id VARCHAR(100) NOT NULL,
        sensor_type VARCHAR(50) NOT NULL,
        value DECIMAL(10,4) NOT NULL,
        unit VARCHAR(20),
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        location VARCHAR(200),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Alerts Table
    CREATE TABLE IF NOT EXISTS alerts (
        id SERIAL PRIMARY KEY,
        alert_type VARCHAR(50) NOT NULL,
        severity VARCHAR(20) NOT NULL,
        message TEXT NOT NULL,
        sensor_id VARCHAR(100),
        status VARCHAR(20) DEFAULT 'ACTIVE',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        resolved_at TIMESTAMP WITH TIME ZONE
    );

    -- Equipment Table
    CREATE TABLE IF NOT EXISTS equipment (
        id SERIAL PRIMARY KEY,
        equipment_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        type VARCHAR(100) NOT NULL,
        location VARCHAR(200),
        status VARCHAR(20) DEFAULT 'OPERATIONAL',
        last_maintenance TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Maintenance Requests Table
    CREATE TABLE IF NOT EXISTS maintenance_requests (
        id SERIAL PRIMARY KEY,
        equipment_id VARCHAR(100) NOT NULL,
        request_type VARCHAR(50) NOT NULL,
        description TEXT,
        priority VARCHAR(20) DEFAULT 'MEDIUM',
        status VARCHAR(20) DEFAULT 'PENDING',
        requested_by VARCHAR(100),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        completed_at TIMESTAMP WITH TIME ZONE
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_sensor_data_sensor_id ON sensor_data(sensor_id);
    CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);
    CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
    CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
    CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
    CREATE INDEX IF NOT EXISTS idx_maintenance_requests_status ON maintenance_requests(status);
    "
    
    echo -e "${GREEN}✅ Database setup completed successfully!${NC}"
}

# Function to verify deployment
verify_deployment() {
    echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
    
    # Get service URLs
    CONTROLTOWER_URL=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name main \
        --query properties.outputs.controlTowerUrl.value \
        --output tsv)
    
    FACILITYMANAGEMENT_URL=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name main \
        --query properties.outputs.facilityManagementUrl.value \
        --output tsv)
    
    DATALAKE_URL=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name main \
        --query properties.outputs.dataLakeUrl.value \
        --output tsv)
    
    EVENTHUB_NAMESPACE=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name main \
        --query properties.outputs.eventHubNamespace.value \
        --output tsv)
    
    POSTGRES_FQDN=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name main \
        --query properties.outputs.postgresServerFqdn.value \
        --output tsv)
    
    REDIS_HOSTNAME=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name main \
        --query properties.outputs.redisHostName.value \
        --output tsv)
    
    # Display results
    echo -e "${GREEN}📋 Service URLs:${NC}"
    echo -e "${GREEN}   ControlTower: $CONTROLTOWER_URL${NC}"
    echo -e "${GREEN}   FacilityManagement: $FACILITYMANAGEMENT_URL${NC}"
    echo -e "${GREEN}   DataLake: $DATALAKE_URL${NC}"
    echo -e "${GREEN}📋 Infrastructure Details:${NC}"
    echo -e "${GREEN}   Event Hub Namespace: $EVENTHUB_NAMESPACE${NC}"
    echo -e "${GREEN}   PostgreSQL Server: $POSTGRES_FQDN${NC}"
    echo -e "${GREEN}   Redis Cache: $REDIS_HOSTNAME${NC}"
    
    # Wait for services to be ready
    echo -e "${YELLOW}⏳ Waiting for services to be ready (2 minutes)...${NC}"
    sleep 120
    
    # Test endpoints
    echo -e "${YELLOW}🧪 Testing service endpoints...${NC}"
    
    local services=(
        "ControlTower:$CONTROLTOWER_URL"
        "FacilityManagement:$FACILITYMANAGEMENT_URL"
        "DataLake:$DATALAKE_URL"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name url <<< "$service"
        if curl -f -s "$url/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is healthy${NC}"
        else
            echo -e "${YELLOW}⚠️  $name health check failed (may still be starting)${NC}"
        fi
    done
}

# Main deployment flow
main() {
    echo -e "${BLUE}🚀 Starting complete deployment...${NC}"
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Deploy infrastructure
    deploy_infrastructure
    
    # Step 3: Build and push Docker images
    build_and_push_images
    
    # Step 4: Setup database
    setup_database
    
    # Step 5: Verify deployment
    verify_deployment
    
    echo -e "${GREEN}🎉 Complete deployment finished successfully!${NC}"
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo -e "${BLUE}   1. Monitor Container Apps in Azure Portal${NC}"
    echo -e "${BLUE}   2. Check Application Insights for monitoring${NC}"
    echo -e "${BLUE}   3. Test your microservices APIs${NC}"
    echo -e "${BLUE}   4. Set up CI/CD pipeline if needed${NC}"
}

# Run main function
main
