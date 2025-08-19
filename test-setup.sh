#!/bin/bash

# Fire IoT MSA Test Script
# This script tests the entire setup

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🧪 Testing Fire IoT MSA Setup${NC}"

# Test 1: Infrastructure Services
echo -e "${YELLOW}1. Testing Infrastructure Services...${NC}"

# PostgreSQL
if docker exec fire-iot-postgres psql -U postgres -d core -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ PostgreSQL is running${NC}"
else
    echo -e "${RED}   ❌ PostgreSQL is not responding${NC}"
fi

# Redis
if docker exec fire-iot-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Redis is running${NC}"
else
    echo -e "${RED}   ❌ Redis is not responding${NC}"
fi

# Kafka
if docker exec fire-iot-kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Kafka is running${NC}"
else
    echo -e "${RED}   ❌ Kafka is not responding${NC}"
fi

# Test 2: Database Schema
echo -e "${YELLOW}2. Testing Database Schema...${NC}"

# Check if tables exist
TABLES=$(docker exec fire-iot-postgres psql -U postgres -d core -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

if echo "$TABLES" | grep -q "alerts"; then
    echo -e "${GREEN}   ✅ Alerts table exists${NC}"
else
    echo -e "${RED}   ❌ Alerts table missing${NC}"
fi

if echo "$TABLES" | grep -q "station_data"; then
    echo -e "${GREEN}   ✅ Station data table exists${NC}"
else
    echo -e "${RED}   ❌ Station data table missing${NC}"
fi

# Test 3: Service Structure
echo -e "${YELLOW}3. Testing Service Structure...${NC}"

# Check if all service directories exist
SERVICES=("controltower" "facilitymanagement" "datalake" "alert")

for service in "${SERVICES[@]}"; do
    if [ -d "services/$service" ]; then
        echo -e "${GREEN}   ✅ $service directory exists${NC}"
    else
        echo -e "${RED}   ❌ $service directory missing${NC}"
    fi
done

# Test 4: Configuration Files
echo -e "${YELLOW}4. Testing Configuration Files...${NC}"

# Check Dockerfiles
for service in "${SERVICES[@]}"; do
    if [ -f "services/$service/Dockerfile" ]; then
        echo -e "${GREEN}   ✅ $service Dockerfile exists${NC}"
    else
        echo -e "${RED}   ❌ $service Dockerfile missing${NC}"
    fi
done

# Check Java POM files
for service in "controltower" "facilitymanagement"; do
    if [ -f "services/$service/pom.xml" ]; then
        echo -e "${GREEN}   ✅ $service pom.xml exists${NC}"
    else
        echo -e "${RED}   ❌ $service pom.xml missing${NC}"
    fi
done

# Check Python requirements
for service in "datalake" "alert"; do
    if [ -f "services/$service/requirements.txt" ]; then
        echo -e "${GREEN}   ✅ $service requirements.txt exists${NC}"
    else
        echo -e "${RED}   ❌ $service requirements.txt missing${NC}"
    fi
done

# Test 5: Infrastructure Configuration
echo -e "${YELLOW}5. Testing Infrastructure Configuration...${NC}"

if [ -f "infra/compose.local.yml" ]; then
    echo -e "${GREEN}   ✅ Docker Compose file exists${NC}"
else
    echo -e "${RED}   ❌ Docker Compose file missing${NC}"
fi

if [ -f "infra/aca/main.bicep" ]; then
    echo -e "${GREEN}   ✅ Bicep template exists${NC}"
else
    echo -e "${RED}   ❌ Bicep template missing${NC}"
fi

# Test 6: Contracts
echo -e "${YELLOW}6. Testing Contracts...${NC}"

if [ -f "contracts/openapi/controltower.yaml" ]; then
    echo -e "${GREEN}   ✅ ControlTower OpenAPI spec exists${NC}"
else
    echo -e "${RED}   ❌ ControlTower OpenAPI spec missing${NC}"
fi

if [ -f "contracts/openapi/facilitymanagement.yaml" ]; then
    echo -e "${GREEN}   ✅ FacilityManagement OpenAPI spec exists${NC}"
else
    echo -e "${RED}   ❌ FacilityManagement OpenAPI spec missing${NC}"
fi

# Check event schemas
EVENT_SCHEMAS=("datalake.data-received.json" "datalake.detected.json" "datalake.risk-scored.json" "alert.notification-created.json" "alert.notification-dispatched.json")

for schema in "${EVENT_SCHEMAS[@]}"; do
    if [ -f "contracts/events/$schema" ]; then
        echo -e "${GREEN}   ✅ $schema exists${NC}"
    else
        echo -e "${RED}   ❌ $schema missing${NC}"
    fi
done

# Test 7: Port Availability
echo -e "${YELLOW}7. Testing Port Availability...${NC}"

PORTS=("5433:PostgreSQL" "6379:Redis" "9092:Kafka" "8090:Kafka UI" "8091:PgAdmin")

for port_info in "${PORTS[@]}"; do
    IFS=':' read -r port service <<< "$port_info"
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Port $port ($service) is available${NC}"
    else
        echo -e "${RED}   ❌ Port $port ($service) is not available${NC}"
    fi
done

echo -e "${GREEN}🎉 Testing completed!${NC}"
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "${YELLOW}   1. Install Maven for Java services${NC}"
echo -e "${YELLOW}   2. Fix SSL certificate issues for Python packages${NC}"
echo -e "${YELLOW}   3. Build and run individual services${NC}"
echo -e "${YELLOW}   4. Test API endpoints${NC}"
