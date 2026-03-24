interface SystemStatusProps {
  status: 'healthy' | 'warning' | 'unhealthy'
}

export default function SystemStatus({ status }: SystemStatusProps) {
  const statusColors = {
    healthy: 'bg-green-900 text-green-200',
    warning: 'bg-yellow-900 text-yellow-200',
    unhealthy: 'bg-red-900 text-red-200',
  }

  const statusIcons = {
    healthy: '✅',
    warning: '⚠️',
    unhealthy: '❌',
  }

  const statusTexts = {
    healthy: 'System Healthy',
    warning: 'System Warning',
    unhealthy: 'System Unhealthy',
  }

  return (
    <div className={`rounded-lg p-4 mb-8 flex items-center gap-3 ${statusColors[status]}`}>
      <span className="text-2xl">{statusIcons[status]}</span>
      <div>
        <h4 className="font-semibold">{statusTexts[status]}</h4>
        <p className="text-sm opacity-75">
          {status === 'healthy' && 'All systems operational'}
          {status === 'warning' && 'Minor issues detected'}
          {status === 'unhealthy' && 'System experiencing issues'}
        </p>
      </div>
    </div>
  )
}
