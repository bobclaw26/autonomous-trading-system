import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface ChartProps {
  data: Record<string, number>
}

export default function Chart({ data }: ChartProps) {
  // Mock data for demonstration
  const mockData = [
    { time: '9:00 AM', price: 100, ma20: 99.5, ma50: 99 },
    { time: '10:00 AM', price: 102, ma20: 100.2, ma50: 99.3 },
    { time: '11:00 AM', price: 101, ma20: 100.8, ma50: 99.6 },
    { time: '12:00 PM', price: 103, ma20: 101.5, ma50: 99.9 },
    { time: '1:00 PM', price: 104, ma20: 102.3, ma50: 100.3 },
    { time: '2:00 PM', price: 105, ma20: 103.2, ma50: 100.7 },
    { time: '3:00 PM', price: 106, ma20: 104.1, ma50: 101.1 },
    { time: '4:00 PM', price: 105.5, ma20: 104.6, ma50: 101.5 },
  ]

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-white mb-4">Price Chart</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={mockData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="time" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #4B5563' }}
            labelStyle={{ color: '#FFFFFF' }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#3B82F6" 
            dot={false}
            name="Current Price"
          />
          <Line 
            type="monotone" 
            dataKey="ma20" 
            stroke="#F59E0B" 
            dot={false}
            strokeDasharray="5 5"
            name="MA 20"
          />
          <Line 
            type="monotone" 
            dataKey="ma50" 
            stroke="#EF4444" 
            dot={false}
            strokeDasharray="5 5"
            name="MA 50"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
