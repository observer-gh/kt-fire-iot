#!/bin/bash

# Start Local Development Environment
echo "🚀 Starting Fire IoT MSA Local Development Environment..."

# Load local environment variables
export $(cat infra/env.local | xargs)

# Start infrastructure services
echo "📦 Starting infrastructure services..."
docker-compose -f infra/compose.local.yml --env-file infra/env.local up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose -f infra/compose.local.yml ps

echo "✅ Local environment started!"
echo "📊 Kafka UI: http://localhost:${KAFKA_UI_PORT:-8080}"
echo "🗄️  PgAdmin: http://localhost:${PGADMIN_PORT:-8081}"
echo "📈 PostgreSQL: localhost:${POSTGRES_PORT:-5432}"
echo "🔴 Redis: localhost:${REDIS_PORT:-6379}"
echo "📡 Kafka: localhost:${KAFKA_PORT:-9092}"
