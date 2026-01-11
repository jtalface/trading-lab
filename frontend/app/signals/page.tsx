'use client'

import { useState, useEffect } from 'react'
import { api, Signal } from '@/lib/api'
import { format } from 'date-fns'

export default function SignalsPage() {
  const [latestSignals, setLatestSignals] = useState<Signal[]>([])
  const [recentSignals, setRecentSignals] = useState<Signal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [limit, setLimit] = useState(50)

  useEffect(() => {
    loadSignals()
  }, [limit])

  const loadSignals = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Load signals from the latest backtest
      const latest = await api.getLatestBacktestSignals(limit)
      setLatestSignals(latest)
      
      // If you want live signals in the future, uncomment:
      // const today = await api.getTodaySignals()
      // setRecentSignals(today)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getSignalTypeColor = (type: string) => {
    switch (type) {
      case 'entry_long':
        return 'bg-green-100 text-green-800'
      case 'entry_short':
        return 'bg-red-100 text-red-800'
      case 'exit_long':
      case 'exit_short':
        return 'bg-blue-100 text-blue-800'
      case 'stop_long':
      case 'stop_short':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatSignalType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Trading Signals</h1>
        <p className="text-gray-600">
          View signals from the most recent backtest run
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading signals...</p>
        </div>
      ) : (
        <>
          {/* Latest Backtest Signals */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold">Latest Backtest Signals</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Showing {latestSignals.length} most recent signals
                </p>
              </div>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value={25}>Last 25 signals</option>
                <option value={50}>Last 50 signals</option>
                <option value={100}>Last 100 signals</option>
              </select>
            </div>
            
            {latestSignals.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No signals found</p>
                <p className="text-sm mt-2">Run a backtest to generate signals</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Signal</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contracts</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stop</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {latestSignals.map(signal => (
                      <tr key={signal.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {format(new Date(signal.date), 'MMM dd, yyyy')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap font-medium">
                          {signal.instrument?.symbol}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${getSignalTypeColor(signal.signal_type)}`}>
                            {formatSignalType(signal.signal_type)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {signal.price?.toFixed(2) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {signal.target_contracts || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {signal.stop_price?.toFixed(2) || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {signal.reason || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

