interface Trade {
  id: string
  symbol: string
  side: string
  quantity: number
  price: number
  timestamp: string
  pnl: number
}

interface TradeHistoryProps {
  trades: Trade[]
}

export default function TradeHistory({ trades }: TradeHistoryProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-white mb-4">Recent Trades</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left text-gray-400 py-3">Symbol</th>
              <th className="text-left text-gray-400 py-3">Side</th>
              <th className="text-left text-gray-400 py-3">Quantity</th>
              <th className="text-left text-gray-400 py-3">Price</th>
              <th className="text-left text-gray-400 py-3">P&L</th>
              <th className="text-left text-gray-400 py-3">Time</th>
            </tr>
          </thead>
          <tbody>
            {trades.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center text-gray-500 py-8">
                  No trades yet
                </td>
              </tr>
            ) : (
              trades.slice(0, 10).map((trade) => (
                <tr key={trade.id} className="border-b border-gray-700 hover:bg-gray-700">
                  <td className="text-white py-3 font-semibold">{trade.symbol}</td>
                  <td className={`py-3 font-semibold ${trade.side === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                    {trade.side}
                  </td>
                  <td className="text-gray-300 py-3">{trade.quantity}</td>
                  <td className="text-gray-300 py-3">${trade.price.toFixed(2)}</td>
                  <td className={`py-3 font-semibold ${trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${trade.pnl.toFixed(2)}
                  </td>
                  <td className="text-gray-500 py-3 text-sm">{new Date(trade.timestamp).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
