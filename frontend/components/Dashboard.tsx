import React, { useState, useEffect } from 'react'
import PortfolioCard from './PortfolioCard'
import TradeHistory from './TradeHistory'
import Chart from './Chart'
import SystemStatus from './SystemStatus'

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState({
    balance: 100000,
    pnl: 0,
    return_percent: 0,
    sharpe_ratio: 0,
    max_drawdown: 0,
    win_rate: 0,
    open_positions: 0,
    closed_positions: 0,
  })

  const [trades, setTrades] = useState([])
  const [prices, setPrices] = useState({})
  const [systemHealth, setSystemHealth] = useState('healthy')

  useEffect(() => {
    // Fetch initial data
    fetchPortfolioData()
    fetchSystemHealth()
    
    // Setup WebSocket for real-time updates
    const ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ws/portfolio`.replace('http', 'ws')
    )
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setPortfolio(data)
    }
    
    ws.onerror = () => {
      console.log('WebSocket connection failed, using polling')
    }
    
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [])

  const fetchPortfolioData = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/portfolio`)
      if (response.ok) {
        const data = await response.json()
        setPortfolio(data)
      }
    } catch (error) {
      console.error('Failed to fetch portfolio:', error)
    }
  }

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
      if (response.ok) {
        setSystemHealth('healthy')
      }
    } catch (error) {
      setSystemHealth('unhealthy')
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Trading Dashboard</h1>
        <p className="text-gray-400">Autonomous Trading System - Real-Time Portfolio Monitor</p>
      </div>

      {/* System Status */}
      <SystemStatus status={systemHealth} />

      {/* Top Row - Portfolio Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <PortfolioCard
          title="Portfolio Value"
          value={`$${portfolio.balance?.toFixed(2) || '0.00'}`}
          change={portfolio.return_percent?.toFixed(2) || '0.00'}
          icon="💰"
        />
        <PortfolioCard
          title="Total P&L"
          value={`$${portfolio.pnl?.toFixed(2) || '0.00'}`}
          change={portfolio.return_percent?.toFixed(2) || '0.00'}
          icon="📈"
        />
        <PortfolioCard
          title="Sharpe Ratio"
          value={portfolio.sharpe_ratio?.toFixed(2) || '0.00'}
          change=""
          icon="📊"
        />
        <PortfolioCard
          title="Max Drawdown"
          value={`${portfolio.max_drawdown?.toFixed(2) || '0.00'}%`}
          change=""
          icon="📉"
        />
      </div>

      {/* Second Row - Chart & Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <Chart data={prices} />
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Portfolio Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Win Rate:</span>
              <span className="text-white font-semibold">{portfolio.win_rate?.toFixed(1) || '0.0'}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Open Positions:</span>
              <span className="text-white font-semibold">{portfolio.open_positions || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Closed Positions:</span>
              <span className="text-white font-semibold">{portfolio.closed_positions || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Return:</span>
              <span className={`font-semibold ${portfolio.return_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {portfolio.return_percent?.toFixed(2) || '0.00'}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Trade History */}
      <TradeHistory trades={trades} />
    </div>
  )
}
