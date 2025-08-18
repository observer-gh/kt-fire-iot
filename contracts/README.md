# Contracts

API contracts and event schemas for the Fire IoT MSA.

## 📁 Structure

```
contracts/
├── openapi/              # OpenAPI specifications
│   ├── controltower.yaml
│   └── staticmanagement.yaml
└── events/               # Event schemas
    ├── datalake.data-received.json
    ├── datalake.detected.json
    ├── datalake.risk-scored.json
    ├── alert.notification-created.json
    └── alert.notification-dispatched.json
```

## 🔧 Usage

### Validate OpenAPI Specs

```bash
# Install swagger-cli
npm install -g swagger-cli

# Validate specs
swagger-cli validate contracts/openapi/controltower.yaml
swagger-cli validate contracts/openapi/staticmanagement.yaml
```

### Generate Client Code

```bash
# Generate Java client
openapi-generator generate -i contracts/openapi/controltower.yaml -g java -o clients/controltower-java

# Generate Python client
openapi-generator generate -i contracts/openapi/controltower.yaml -g python -o clients/controltower-python
```

### Validate Event Schemas

```bash
# Install jsonschema
pip install jsonschema

# Validate event schemas
python -c "import json, jsonschema; jsonschema.validate(json.load(open('contracts/events/datalake.data-received.json')), json.load(open('contracts/events/datalake.data-received.json')))"
```

## 📋 Contract Rules

- **Versioning**: Use semantic versioning (v1, v2, etc.)
- **Idempotency**: Include `dedupe_key` field in events
- **Timestamps**: Use ISO8601 UTC format
- **Backward Compatibility**: Events must be backward-compatible
