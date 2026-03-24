"""FastAPI application and endpoints."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Autonomous Trading System API",
    description="Real-time trading API with backtesting and strategies",
    version="2.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from .routes import portfolio, trades, health

# Include routes
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
