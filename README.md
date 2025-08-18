# Fire IoT MSA

Microservices architecture for IoT fire monitoring system with real-time data processing and alert management.

## 🏗️ Architecture

- **ControlTower** (Java Spring Boot) - Central hub for read-only APIs
- **StaticManagement** (Java Spring Boot) - Equipment and maintenance data
- **DataLake** (Python FastAPI) - Data ingestion and streaming processing
- **Alert** (Python Worker) - Alert deduplication and dispatch

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Java 21 (for local development)
- Python 3.11 (for local development)

### Start Infrastructure

```bash
./infra/start-local.sh
```

### Build All Services

```bash
# Python services
docker build -t fire-iot-datalake services/datalake
docker build -t fire-iot-alert services/alert

# Java services
docker build -t fire-iot-controltower services/controltower
docker build -t fire-iot-staticmanagement services/staticmanagement
```

### Run Services

```bash
# DataLake API
docker run -d --name datalake --network infra_fire-iot-network -p 8084:8080 fire-iot-datalake

# ControlTower API
docker run -d --name controltower --network infra_fire-iot-network -p 8082:8080 \
  -e POSTGRES_URL=jdbc:postgresql://fire-iot-postgres:5432/core \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres fire-iot-controltower

# Alert Worker
docker run -d --name alert --network infra_fire-iot-network fire-iot-alert
```

## 📊 Access Points

- **Kafka UI**: http://localhost:8090
- **PgAdmin**: http://localhost:8091
- **DataLake API**: http://localhost:8084
- **ControlTower API**: http://localhost:8082

## 🧪 Testing

```bash
./test-setup.sh
```

## 🚀 Deployment

### Local Development

```bash
docker-compose -f infra/compose.local.yml up -d
```

### Azure Deployment

```bash
# Build and push images
./infra/aca/build-and-push.sh v1.0.0

# Deploy to Azure
./infra/aca/deploy-bicep.sh dev your-dockerhub-org v1.0.0
```

## 📁 Project Structure

```
├── contracts/           # OpenAPI specs & event schemas
├── services/           # Microservices
│   ├── controltower/   # Java Spring Boot
│   ├── staticmanagement/ # Java Spring Boot
│   ├── datalake/       # Python FastAPI
│   └── alert/          # Python Worker
├── infra/              # Infrastructure & deployment
└── test-setup.sh       # Testing script
```

## 🔧 Development

See individual service READMEs for detailed development instructions.
