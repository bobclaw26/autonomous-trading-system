interface PortfolioCardProps {
  title: string
  value: string
  change: string
  icon: string
}

export default function PortfolioCard({ title, value, change, icon }: PortfolioCardProps) {
  const isPositive = parseFloat(change) >= 0
  
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 transition">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className="text-3xl font-bold text-white mb-2">{value}</div>
      {change && (
        <div className={`text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? '+' : ''}{change}%
        </div>
      )}
    </div>
  )
}
