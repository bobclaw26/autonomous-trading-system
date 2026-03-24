import React, { useState, useEffect } from 'react'
import Dashboard from '../components/Dashboard'

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setIsLoading(false)
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="text-white text-2xl">Loading Trading Dashboard...</div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gray-900">
      <Dashboard />
    </main>
  )
}
