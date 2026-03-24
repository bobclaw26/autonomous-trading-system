"""Portfolio endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_portfolio():
    """Get portfolio overview."""
    return {
        "balance": 100000.00,
        "cash": 50000.00,
        "pnl": 5000.00,
        "return_percent": 5.00,
        "sharpe_ratio": 1.45,
        "max_drawdown": 3.25,
        "win_rate": 62.5,
        "open_positions": 3,
        "closed_positions": 12
    }


@router.get("/positions")
async def get_positions():
    """Get open positions."""
    return {
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 100,
                "entry_price": 150.00,
                "current_price": 155.00,
                "pnl": 500.00,
                "pnl_percent": 3.33
            },
            {
                "symbol": "MSFT",
                "quantity": 50,
                "entry_price": 380.00,
                "current_price": 385.00,
                "pnl": 250.00,
                "pnl_percent": 1.32
            }
        ]
    }


@router.get("/metrics")
async def get_metrics():
    """Get detailed portfolio metrics."""
    return {
        "total_trades": 15,
        "winning_trades": 10,
        "losing_trades": 5,
        "profit_factor": 2.5,
        "avg_win": 750.00,
        "avg_loss": 300.00,
        "largest_win": 2500.00,
        "largest_loss": 1200.00,
        "consecutive_wins": 4,
        "consecutive_losses": 2
    }
