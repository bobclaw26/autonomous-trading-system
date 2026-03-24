# System Architecture

## Overview

The Autonomous Trading System is a modular, production-grade platform for algorithmic trading with paper trading (simulation) as Phase 1.

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend Dashboard                         │
│              (Next.js + React + Tailwind)                   │
│  Portfolio • Trades • Signals • System Status               │
└────────────────────────┬────────────────────────────────────┘
                         │ WebSocket/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    API Server                                │
│                 (FastAPI + Uvicorn)                         │
│         REST endpoints + WebSocket broadcast                │
└──┬──────────────────┬──────────────────┬────────────────────┘
   │                  │                  │
   ▼                  ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Data Layer   │ │ Strategy     │ │ Risk Manager │
│ (Twelve Data)│ │ Engine       │ │ & Execution  │
│              │ │              │ │              │
│• API Client  │ │• MA Crossover│ │• Position    │
│• Caching     │ │• Momentum    │ │  Sizing      │
│• Polling     │ │• Mean Rev    │ │• Stop Loss   │
│• Rate Limit  │ │• Indicators  │ │• Drawdown    │
└──────────────┘ └──────────────┘ └──────────────┘
   │                  │                  │
   └──────────────────┼──────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │  In-Memory Cache     │
           │  (Phase 1)           │
           │  Redis (Phase 2)     │
           └──────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│               Logging & Monitoring                           │
│  • Trade audit trail  • System health  • Error tracking      │
└──────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Data Layer (`src/data/`)
- **twelve_data_client.py**: Twelve Data API integration
- **pipeline.py**: Data orchestration and backfilling
- **cache.py**: In-memory caching with TTL
- **models.py**: OHLCV, Tick, Quote data models

**Responsibilities:**
- Real-time and historical price data retrieval
- Rate limit handling (800 req/min)
- Caching for performance
- Error handling and retries

### Strategy Engine (`src/strategies/`)
- **base_strategy.py**: Abstract strategy interface
- **ma_crossover.py**: 20/50-day moving average
- **momentum.py**: Trend-following strategy
- **mean_reversion.py**: Bollinger Bands + RSI
- **indicators.py**: Technical indicator library

**Responsibilities:**
- Signal generation (BUY/SELL/HOLD)
- Feature engineering
- Strategy configuration and parameters
- Performance tracking

### Trading Engine (`src/engine/`)
- **order.py**: Order types and management
- **execution.py**: Order execution with slippage
- **position.py**: Position tracking
- **portfolio.py**: Portfolio analytics

**Responsibilities:**
- Realistic market simulation
- Order execution with slippage modeling
- Position management
- P&L calculation (realized/unrealized)
- Portfolio performance metrics

### Risk Management (`src/risk/`)
- **position_sizer.py**: Fixed fractional, Kelly sizing
- **risk_limits.py**: Position and drawdown limits
- **risk_metrics.py**: VaR, Sharpe, max drawdown
- **stop_loss.py**: Stop-loss and take-profit logic

**Responsibilities:**
- Position size calculation
- Risk limit enforcement
- Circuit breaker implementation
- Trade restrictions

### API Server (`src/api/`)
- **main.py**: FastAPI application
- **routes/**: REST endpoints
- **ws/**: WebSocket handlers
- **schemas/**: Request/response models

**Responsibilities:**
- HTTP API for frontend
- WebSocket real-time updates
- Trade execution requests
- Portfolio queries

### Frontend (`frontend/`)
- **pages/dashboard.tsx**: Main dashboard
- **components/**: Reusable UI components
- **hooks/useWebSocket.ts**: WebSocket client
- **styles/**: Tailwind CSS styling

**Responsibilities:**
- User interface
- Real-time updates via WebSocket
- Portfolio visualization
- Trade management

## Data Flow

### Trading Execution Flow
```
1. Data Layer receives market data
   ↓
2. Strategy Engine generates signals
   ↓
3. Risk Manager validates position size
   ↓
4. Trading Engine executes order
   ↓
5. Execution report created
   ↓
6. Position updated
   ↓
7. API broadcasts update to Frontend
   ↓
8. Dashboard shows new position
```

### State Management
```
Portfolio State (in-memory):
- Cash balance
- Open positions
- Order history
- Trade history

Updated by:
- Order execution
- Strategy signals
- Risk limit checks

Accessed by:
- Frontend queries
- Risk calculations
- Performance analytics
```

## Configuration

All configuration is centralized in `src/config.py`:

```python
DataConfig:
  - API key
  - Rate limits
  - Cache TTL

TradingConfig:
  - Initial capital
  - Slippage model
  - Commission
  - Position limits

RiskConfig:
  - Drawdown limits
  - Daily loss limits
  - Sector concentration

APIConfig:
  - Host/port
  - CORS origins
  - Debug mode

LoggingConfig:
  - Log level
  - Output file
  - Rotation settings
```

## Deployment

### Development (Local)
```bash
# Without Docker
python3 -m uvicorn src.api.main:app --reload

# With Docker Compose
docker-compose up
```

### Production
```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes (Phase 2)
kubectl apply -f k8s/
```

## Monitoring & Health

Health check endpoint: `GET /health`

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

## Error Handling

### Graceful Degradation
- API remains responsive even if data service fails
- Orders queue if execution is temporarily unavailable
- Cached data used if API rate limit exceeded

### Circuit Breaker
- Automatic stop trading if max drawdown exceeded
- Daily loss limit enforcement
- Position size restrictions

### Logging
- All trades logged with timestamps
- Strategy signals recorded
- Errors captured with stack traces
- Performance metrics tracked

## Scalability (Future)

### Horizontal Scaling
- API: Multiple FastAPI instances behind load balancer
- Strategy: Separate strategy workers for different assets
- Cache: Distributed Redis cluster

### Database
- Phase 1: In-memory storage
- Phase 2: PostgreSQL for persistence
- Phase 3: Time-series DB for OHLCV data

### Message Queue
- Trade execution: RabbitMQ/Kafka
- Signal distribution: Pub/Sub
- Alert system: Message queue

## Testing Strategy

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction
- **End-to-End Tests**: Full trading workflows
- **Backtesting**: Historical performance (Phase 2)
- **Paper Trading**: Live simulation (Phase 1)

## CI/CD Pipeline

1. **Code Push**
   - Run linting (flake8)
   - Run unit tests
   - Calculate coverage

2. **Branch Merge to Develop**
   - Build Docker images
   - Run integration tests
   - Deploy to staging

3. **Release to Main**
   - Run full test suite
   - Deploy to production
   - Monitor health

## Security Considerations

- API keys in environment variables only
- CORS configured for frontend origin
- Trade history immutable (append-only)
- No sensitive data in logs
- Rate limiting on API endpoints
- Input validation on all endpoints

## Future Enhancements

- Real broker API integration
- Machine learning strategies
- Advanced backtesting framework
- Portfolio optimization
- Risk model improvements
- Mobile application
- Notifications/alerts
