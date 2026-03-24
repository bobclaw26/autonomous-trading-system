# Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Git

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/bobclaw26/autonomous-trading-system.git
cd autonomous-trading-system

# Create .env file
cp .env.example .env
# Edit .env and add your TWELVE_DATA_API_KEY

# Start all services
docker-compose up -d

# Check services
docker-compose logs -f api
docker-compose logs -f frontend

# Access dashboard
# API: http://localhost:8000
# Dashboard: http://localhost:3000
# Health check: http://localhost:8000/health
```

### Option 2: Manual Setup

```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-engine.txt
pip install fastapi uvicorn

# Create logs directory
mkdir -p logs

# Run API server
python3 -m uvicorn src.api.main:app --reload

# Frontend (in separate terminal)
cd frontend
npm install
npm run dev

# Access dashboard at http://localhost:3000
```

## Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
ENV=development
LOG_LEVEL=INFO
TWELVE_DATA_API_KEY=your_api_key_here
INITIAL_CAPITAL=100000
MAX_DRAWDOWN_PCT=0.20
```

### Config File (Optional)

Create `config.yml` for YAML configuration:

```yaml
data:
  twelve_data_api_key: your_key
  rate_limit_requests_per_minute: 800
  cache_ttl_seconds: 300

trading:
  initial_capital: 100000
  base_spread_bps: 1.0
  commission_pct: 0.001
  max_position_pct: 0.05
  max_portfolio_drawdown_pct: 0.20

risk:
  max_daily_loss_pct: 0.05
  risk_per_trade_pct: 0.02

api:
  host: 0.0.0.0
  port: 8000
  debug: true
```

## Production Deployment

### Option 1: Docker Compose

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Scale API servers
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Option 2: Standalone Server

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3.10 python3-pip redis-server

# Clone repository
git clone https://github.com/bobclaw26/autonomous-trading-system.git
cd autonomous-trading-system

# Install Python dependencies
pip install -r requirements-engine.txt
pip install gunicorn

# Setup systemd service
sudo cp deployment/trading-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trading-api
sudo systemctl start trading-api

# Frontend (using Vercel or similar)
cd frontend
npm install
npm run build
npm run start
```

### Option 3: AWS Deployment

```bash
# Using AWS RDS for PostgreSQL
# Using ElastiCache for Redis
# Using ECS for container orchestration

# Push images to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag trading-api:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/trading-api:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/trading-api:latest

# Deploy ECS task
aws ecs update-service --cluster trading --service api --force-new-deployment
```

### Option 4: Kubernetes

```bash
# Create namespace
kubectl create namespace trading

# Create secrets
kubectl -n trading create secret generic trading-secrets \
  --from-literal=TWELVE_DATA_API_KEY=your_key

# Deploy
kubectl -n trading apply -f k8s/

# Check deployment
kubectl -n trading get pods
kubectl -n trading logs deployment/api
```

## Monitoring & Logging

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "components": {
    "api": "healthy",
    "database": "healthy",
    "cache": "healthy",
    "data_service": "healthy"
  }
}
```

### Logs

```bash
# Docker logs
docker logs trading-api

# File logs
tail -f logs/trading_system.log

# Follow logs
docker-compose logs -f

# Check specific service
docker-compose logs -f api
```

### Metrics

Metrics endpoint (Future): `GET /metrics`

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Docker Issues

```bash
# Remove all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache
```

### API not responding

```bash
# Check if container is running
docker ps

# Check logs
docker logs trading-api

# Restart service
docker-compose restart api
```

### Redis connection error

```bash
# Check Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli ping

# Restart Redis
docker-compose restart redis
```

## Backup & Restore

### Backup Data

```bash
# Export trade history
curl http://localhost:8000/api/trades/export > trades_backup.json

# Backup Redis
docker exec trading-redis redis-cli BGSAVE

# Backup logs
tar -czf logs_backup.tar.gz logs/
```

### Restore Data

```bash
# Import trade history
curl -X POST -d @trades_backup.json \
  http://localhost:8000/api/trades/import
```

## Performance Tuning

### API Server

```yaml
# Increase worker count
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 src.api.main:app
```

### Redis

```yaml
# Update memory policy in redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
```

### Database

```sql
-- Add indexes
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_positions_symbol ON positions(symbol);
```

## Rollback Procedure

```bash
# Check current version
docker ps | grep trading-api

# Rollback to previous version
docker-compose down
git checkout previous-commit
docker-compose build
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

## Scaling Strategy

### Vertical Scaling
- Increase CPU/memory on single instance
- Max out before horizontal scaling

### Horizontal Scaling
```bash
# Scale API servers
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Use load balancer (nginx/AWS ELB)
# Configure sticky sessions for WebSocket
```

### Database Scaling
- Read replicas for reporting
- Sharding by time period (Phase 3)
- Time-series database (InfluxDB/TimescaleDB)

## Maintenance

### Regular Tasks

```bash
# Daily: Check health
0 * * * * curl http://localhost:8000/health

# Weekly: Clean old logs
0 0 * * 0 find logs/ -mtime +7 -delete

# Monthly: Backup data
0 0 1 * * docker exec trading-redis redis-cli BGSAVE
```

### Updates

```bash
# Check for updates
git fetch origin
git status

# Update code
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose down
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify configuration: `cat .env`
3. Test connectivity: `curl http://localhost:8000/health`
4. Check GitHub issues: https://github.com/bobclaw26/autonomous-trading-system/issues
