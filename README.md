# Autonomous Trading System

A production-grade autonomous algorithmic trading platform that simulates trades using the Twelve Data API.

## Project Status
🚀 Phase 1 MVP (In Development)

## Tech Stack
- **Backend:** Python 3.10+ (FastAPI)
- **Frontend:** Next.js + React
- **Database:** Redis + PostgreSQL
- **Data:** Twelve Data API
- **Infrastructure:** Docker, GitHub Actions

## Project Structure
```
autonomous-trading-system/
├── src/
│   ├── data/              # Data layer (Twelve Data integration)
│   ├── strategies/        # Trading strategies
│   ├── engine/            # Paper trading engine
│   ├── risk/              # Risk management
│   └── api/               # REST API
├── frontend/              # React dashboard
├── tests/                 # Test suite
├── docker-compose.yml     # Multi-container setup
└── docs/                  # Documentation
```

## Phase 1 MVP Features
- ✅ Twelve Data API integration
- ✅ Moving Average Crossover strategy (20/50)
- ✅ Paper trading engine ($100k simulated)
- ✅ Risk controls (2% stop-loss, 5% max position)
- ✅ Real-time dashboard
- ✅ GitHub CI/CD

## Getting Started
See `docs/` for setup and architecture guides.

## Team
- 🏗️ Data Architect
- ⚙️ Trading Engineer
- 📊 Quant Strategist
- 🛡️ Risk Manager
- 💻 Frontend Developer
- 🔧 DevOps/Architecture (pending)

## License
MIT
