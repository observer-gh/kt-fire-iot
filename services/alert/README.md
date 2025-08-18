# Alert

Alert deduplication and dispatch worker service.

## 🚀 Quick Start

### Build

```bash
# With Docker
docker build -t fire-iot-alert .

# Local development
pip install -r requirements.txt
```

### Run

```bash
# Local development
python -m worker.main

# With Docker
docker run -d --name alert --network infra_fire-iot-network fire-iot-alert
```

### Test

```bash
# Check logs
docker logs alert

# Monitor worker
docker exec alert ps aux
```

## 🔧 Development

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run worker
python -m worker.main
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=worker
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
worker/
├── main.py              # Worker application
├── channels/            # Alert channels
│   ├── webhook.py      # Webhook dispatcher
│   ├── email.py        # Email dispatcher
│   └── sms.py          # SMS dispatcher
└── models/              # Pydantic models
```
