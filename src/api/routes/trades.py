"""Trade endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_trades(limit: int = 20):
    """Get recent trades."""
    return {
        "trades": [
            {
                "id": f"TRADE-{i}",
                "symbol": "AAPL",
                "side": "BUY" if i % 2 == 0 else "SELL",
                "quantity": 100,
                "price": 150.00 + i,
                "timestamp": "2026-03-24T16:00:00Z",
                "pnl": 500.00 if i % 2 == 0 else -200.00
            }
            for i in range(min(limit, 20))
        ]
    }


@router.get("/{trade_id}")
async def get_trade(trade_id: str):
    """Get specific trade details."""
    return {
        "id": trade_id,
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 100,
        "entry_price": 150.00,
        "exit_price": 155.00,
        "pnl": 500.00,
        "commission": 10.00,
        "entry_time": "2026-03-24T10:00:00Z",
        "exit_time": "2026-03-24T14:00:00Z"
    }
