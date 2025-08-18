# Fire IoT MSA

Full-stack microservices for IoT fire monitoring with real-time data processing, alert management, and dashboard.

## 🏗️ Architecture

- **Dashboard** (Next.js + Tailwind) - Frontend dashboard
- **ControlTower** (Java Spring Boot) - Central hub APIs
- **StaticManagement** (Java Spring Boot) - Equipment data
- **DataLake** (Python FastAPI) - Data ingestion
- **Alert** (Python Worker) - Alert processing

## 🚀 Quick Start

### Prerequisites

```bash
docker-compose
node 18+ (for dashboard)
java 21+ (for backend)
python 3.11+ (for backend)
```

### Start Everything

```bash
# Infrastructure
./infra/start-local.sh

# Frontend
cd dashboard && npm run dev

# Backend services
docker-compose -f infra/compose.local.yml up -d
```

### Build All

```bash
# Frontend
cd dashboard && docker build -t fire-iot-dashboard .

# Backend
docker build -t fire-iot-datalake services/datalake
docker build -t fire-iot-controltower services/controltower
docker build -t fire-iot-staticmanagement services/staticmanagement
docker build -t fire-iot-alert services/alert
```

## 📊 Access Points

- **Dashboard**: http://localhost:3000
- **ControlTower API**: http://localhost:8082
- **DataLake API**: http://localhost:8084
- **Kafka UI**: http://localhost:8090
- **PgAdmin**: http://localhost:8091

## 🚀 Deploy

### Local

```bash
docker-compose -f infra/compose.local.yml up -d
```

### Azure

```bash
./infra/aca/deploy-bicep.sh dev your-org v1.0.0
```

## 📁 Structure

```
├── dashboard/          # Next.js frontend
├── services/           # Backend microservices
├── contracts/          # OpenAPI + event schemas
├── infra/              # Docker + Azure config
└── test-setup.sh       # Testing
```

## 🔧 Development

```bash
# Frontend dev
cd dashboard && npm run dev

# Backend dev
cd services/datalake && python -m uvicorn app.main:app --reload
cd services/controltower && ./mvnw spring-boot:run
```
