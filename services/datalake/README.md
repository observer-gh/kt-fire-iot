# DataLake

Data ingestion and streaming processing service for IoT fire monitoring.

## 🚀 Quick Start

### Build

```bash
# With Docker
docker build -t fire-iot-datalake .

# Local development
pip install -r requirements.txt
```

### Run

```bash
# Local development
python -m app.main

# With Docker
docker run -d --name datalake --network infra_fire-iot-network -p 8084:8080 fire-iot-datalake
```

### Test

```bash
# Health check
curl http://localhost:8084/healthz

# API documentation
open http://localhost:8084/docs
```

## 📊 APIs

- `GET /healthz` - Health check
- `POST /ingest` - Ingest sensor data
- `GET /docs` - API documentation (Swagger UI)

## 🔧 Development

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Database Migration

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## 📁 Structure

```
app/
├── main.py              # FastAPI application
├── consumer.py          # Kafka/Event Hubs consumer
├── sinks/               # Data sinks
│   ├── db.py           # Database operations
│   ├── redis.py        # Redis operations
│   └── events.py       # Event publishing
└── models/              # Pydantic models
```
