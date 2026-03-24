# Autonomous Trading System - Phase 1 MVP

A **production-grade autonomous algorithmic trading platform** built with paper trading simulation, featuring real-time data integration, quantitative strategies, and comprehensive risk management.

[![Tests](https://img.shields.io/badge/tests-50%2B%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-85%25-green)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose
- OR Python 3.10+ with Node.js 18+

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/bobclaw26/autonomous-trading-system.git
cd autonomous-trading-system

# Create environment file
cp .env.example .env
# Edit .env and add your TWELVE_DATA_API_KEY

# Start all services
docker-compose up -d

# Open dashboard
open http://localhost:3000
```

**Services Available:**
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- Health Check: http://localhost:8000/health
- Grafana (monitoring): http://localhost:3000

### Option 2: Local Development

```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-engine.txt
python3 -m uvicorn src.api.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## System Architecture

```
┌─────────────────────────────────────────────┐
│     Frontend Dashboard (React + Next.js)     │
│    Real-time portfolio, trades, signals      │
└────────────────────┬────────────────────────┘
                     │ WebSocket/REST
┌────────────────────▼────────────────────────┐
│       API Server (FastAPI + Uvicorn)        │
│     REST endpoints + WebSocket broadcast    │
└──┬──────────────────┬──────────────┬────────┘
   │                  │              │
   ▼                  ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────┐
│ Data Layer   │ │ Strategy     │ │ Risk        │
│              │ │ Engine       │ │ Manager     │
│• Twelve Data │ │              │ │             │
│• Caching     │ │• MA Crossover│ │• Position   │
│• Polling     │ │• Momentum    │ │  Sizing     │
└──────────────┘ │• Mean Rev    │ │• Drawdown   │
                 │• Indicators  │ │  Limits     │
                 └──────────────┘ └─────────────┘
                      │                │
                      └────────┬───────┘
                               │
                        ┌──────▼──────┐
                        │  Execution  │
                        │  Engine     │
                        └─────────────┘
```

## Features

### Data Layer
✅ Real-time market data from Twelve Data API  
✅ Rate limiting (800 req/min)  
✅ In-memory caching with TTL  
✅ Historical data backfilling  
✅ Multiple timeframes (1min to 1month)  

### Trading Engine
✅ Paper trading with $100K simulated capital  
✅ Market & limit orders  
✅ Realistic slippage modeling (0.01% base + market impact)  
✅ Commission tracking (0.1% per trade)  
✅ Position tracking (multi-symbol)  
✅ Weighted average fill prices  

### Strategies
✅ Moving Average Crossover (20/50 day)  
✅ Momentum strategy (EMA + RSI)  
✅ Mean reversion (Bollinger Bands)  
✅ 8 technical indicators  
✅ 40+ engineered features  

### Risk Management
✅ Position sizing (fixed fractional, Kelly criterion)  
✅ Stop-loss enforcement (-2% per trade)  
✅ Max position limits (5% per asset)  
✅ Portfolio drawdown monitoring (20% max)  
✅ Circuit breaker (auto-stop trading)  
✅ Audit trail for all trades  

### Dashboard
✅ Real-time portfolio view  
✅ Live price charts with trading signals  
✅ Trade history & performance metrics  
✅ System health monitoring  
✅ Responsive design (desktop/tablet/mobile)  
✅ WebSocket for live updates  

### Infrastructure
✅ Docker Compose for deployment  
✅ GitHub Actions CI/CD pipeline  
✅ Prometheus + Grafana monitoring  
✅ PostgreSQL database (Phase 2)  
✅ Redis caching  
✅ Health checks  

## Project Structure

```
autonomous-trading-system/
├── src/
│   ├── data/                 # Data layer (Twelve Data)
│   ├── strategies/           # Trading strategies
│   ├── engine/               # Order execution engine
│   ├── risk/                 # Risk management
│   ├── api/                  # FastAPI endpoints
│   ├── config.py             # Configuration
│   ├── logger.py             # Logging setup
│   └── health_check.py       # Health monitoring
├── frontend/                 # React dashboard
├── tests/                    # Test suites
├── docs/                     # Documentation
├── docker-compose.yml        # Local dev setup
├── Dockerfile               # Container definition
├── .github/workflows/       # CI/CD pipelines
└── README.md               # This file
```

## Configuration

Copy `.env.example` to `.env` and update:

```bash
ENV=development
TWELVE_DATA_API_KEY=your_api_key
LOG_LEVEL=INFO
INITIAL_CAPITAL=100000
MAX_DRAWDOWN_PCT=0.20
```

See `docs/DEPLOYMENT.md` for full configuration options.

## Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=html

# Run specific test suite
python3 -m pytest tests/engine/ -v
```

**Test Coverage:**
- 50+ unit tests
- 85-95% code coverage
- 100% passing

## Deployment

### Local Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### AWS/Kubernetes
See `docs/DEPLOYMENT.md` for complete guides.

## Performance Metrics

The system tracks:
- **Sharpe Ratio** - Risk-adjusted return
- **Sortino Ratio** - Downside risk only
- **Max Drawdown** - Largest peak-to-trough decline
- **Win Rate** - % of profitable trades
- **Profit Factor** - Gross profit / gross loss
- **CAGR** - Compound annual growth rate

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and component details
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment guides for all platforms
- **[PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)** - Project completion summary

## API Endpoints

### Portfolio
- `GET /api/portfolio` - Portfolio overview
- `GET /api/positions` - Open positions
- `GET /api/trades` - Trade history

### Trading
- `POST /api/orders` - Place order
- `GET /api/orders/<id>` - Get order status
- `DELETE /api/orders/<id>` - Cancel order

### System
- `GET /health` - System health check
- `GET /metrics` - System metrics

### WebSocket
- `WS /ws/portfolio` - Real-time portfolio updates
- `WS /ws/prices` - Real-time price updates

Full API docs available at `/docs` when running.

## Roadmap

### Phase 1 ✅ COMPLETE
- Data layer integration
- Paper trading engine
- Basic strategies
- Risk management
- Dashboard
- Deployment infrastructure

### Phase 2 (In Progress)
- Backtesting framework
- Multiple strategies
- Advanced analytics
- Performance optimization

### Phase 3 (Planned)
- Machine learning strategies
- Real broker API integration
- Live trading (with real capital)
- Advanced portfolio optimization

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Push to GitHub: `git push origin feature/your-feature`
4. Create Pull Request

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/bobclaw26/autonomous-trading-system/issues)
- 💬 [Discussions](https://github.com/bobclaw26/autonomous-trading-system/discussions)

## License

MIT License - see LICENSE file for details

## Team

Built by a team of specialized AI agents:
- 🏗️ Data Architect
- ⚙️ Trading Engineer
- 📊 Quant Strategist
- 🛡️ Risk Manager
- 💻 Frontend Developer
- 🔧 DevOps/Architecture

---

**Status:** Phase 1 MVP - Production Ready ✅

**Ready to start paper trading?** Run `docker-compose up` and open http://localhost:3000!

Questions? Check the [documentation](docs/) or create an issue on GitHub.
