# Fire IoT MSA

Full-stack microservices for IoT fire monitoring with real-time data processing, alert management, and dashboard.

## 🏗️ Architecture

- **Dashboard** (Next.js + Tailwind) - Frontend dashboard
- **ControlTower** (Java Spring Boot) - Central hub APIs
- **FacilityManagement** (Java Spring Boot) - Equipment data
- **DataLake** (Python FastAPI) - Data ingestion
- **Alert** (Python Worker) - Alert processing

## 🚀 Quick Start

### Prerequisites

```bash
docker-compose
node 18+ (for local dashboard dev)
java 21+ (for local backend dev)
python 3.11+ (for local backend dev)
```

### Start Everything (Recommended)

```bash
# Start all services with proper dependencies
docker-compose up -d

# Check status
docker-compose ps
```

### Start Infrastructure Only

```bash
# Start just infrastructure (PostgreSQL, Redis, Kafka)
docker-compose up -d postgres redis zookeeper kafka kafka-ui pgadmin
```

### Start Services Individually

```bash
# Backend services
docker-compose up -d datalake controltower facilitymanagement alert

# Frontend
docker-compose up -d dashboard
```

### Build All

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build datalake
```

## 📊 Access Points

- **Dashboard**: http://localhost:3000
- **ControlTower API**: http://localhost:8082
- **DataLake API**: http://localhost:8084
- **FacilityManagement API**: http://localhost:8083
- **Kafka UI**: http://localhost:8090
- **PgAdmin**: http://localhost:8091

## 🗄️ Databases

- **DataLake DB**: localhost:5433/datalake
- **ControlTower DB**: localhost:5434/controltower
- **FacilityManagement DB**: localhost:5435/facilitymanagement

## 🚀 Deploy

### Local

```bash
docker-compose up -d
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
├── docker-compose.yml  # All services orchestration
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

## 🧹 Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```
