---
sidebar_position: 3
---

# Self-Hosting

Run QWED on your own infrastructure.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/QWED-AI/qwed-verification.git
cd qwed-verification

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

## Services

| Service | Port | Purpose |
|---------|------|---------|
| QWED API | 8000 | Main API |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & rate limiting |
| Grafana | 3000 | Dashboards |
| Prometheus | 9090 | Metrics |
| Jaeger | 16686 | Tracing |

## Configuration

### Environment Variables

```bash
# .env file
QWED_API_KEY=qwed_your_key
QWED_DATABASE_URL=postgresql://user:pass@localhost:5432/qwed
QWED_REDIS_URL=redis://localhost:6379
QWED_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### API Configuration

```python
# config.py
SETTINGS = {
    "rate_limit_enabled": True,
    "rate_limit_per_minute": 60,
    "cache_ttl_seconds": 3600,
    "max_query_length": 10000,
    "allowed_engines": ["math", "logic", "code", "sql"],
}
```

## Docker

### API Only

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["uvicorn", "qwed_new.api.main:app", "--host", "0.0.0.0"]
```

### Build & Run

```bash
docker build -t qwed-api .
docker run -p 8000:8000 -e QWED_API_KEY=... qwed-api
```

## Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qwed-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qwed-api
  template:
    metadata:
      labels:
        app: qwed-api
    spec:
      containers:
      - name: qwed
        image: qwed/qwed-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: QWED_API_KEY
          valueFrom:
            secretKeyRef:
              name: qwed-secrets
              key: api-key
```

> 🏢 **Enterprise Support Coming Soon:** Managed hosting, dedicated support, and SLA guarantees. Contact rahul@qwedai.com

## Scaling

### Horizontal Scaling

- Stateless API servers behind load balancer
- Redis for distributed rate limiting
- PostgreSQL with read replicas

### Performance Tuning

```bash
# Increase workers
uvicorn qwed_new.api.main:app --workers 4

# Enable connection pooling
export QWED_DB_POOL_SIZE=20
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Prometheus Metrics

```
qwed_verification_total{engine="math", status="verified"}
qwed_verification_latency_seconds
qwed_cache_hit_rate
```

## Security

1. **Always use HTTPS** in production
2. **Set strong API keys**
3. **Enable rate limiting**
4. **Use network isolation**
5. **Rotate secrets regularly**

