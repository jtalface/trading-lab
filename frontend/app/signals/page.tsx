'use client'

import { useState, useEffect } from 'react'
import { api, Signal } from '@/lib/api'
import { format } from 'date-fns'

export default function SignalsPage() {
  const [todaySignals, setTodaySignals] = useState<Signal[]>([])
  const [recentSignals, setRecentSignals] = useState<Signal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [days, setDays] = useState(7)

  useEffect(() => {
    loadSignals()
  }, [days])

  const loadSignals = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [today, recent] = await Promise.all([
        api.getTodaySignals(),
        api.getRecentSignals(days)
      ])
      
      setTodaySignals(today)
      setRecentSignals(recent)
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Live Trading Signals</h1>
        <p className="text-gray-600">
          Monitor entry and exit signals with position sizing and stops
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
          {/* Today's Signals */}
          <div className="card mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Today's Signals</h2>
              <span className="text-sm text-gray-500">
                {format(new Date(), 'EEEE, MMMM dd, yyyy')}
              </span>
            </div>
            
            {todaySignals.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No signals generated today</p>
                <p className="text-sm mt-2">Signals will appear here when market conditions trigger entry or exit criteria</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Signal</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contracts</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stop</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {todaySignals.map(signal => (
                      <tr key={signal.id} className="hover:bg-gray-50">
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

          {/* Recent Signals */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Recent Signals</h2>
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value={7}>Last 7 days</option>
                <option value={14}>Last 14 days</option>
                <option value={30}>Last 30 days</option>
              </select>
            </div>
            
            {recentSignals.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No recent signals found</p>
                <p className="text-sm mt-2">Run a backtest or wait for live signals</p>
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
                    {recentSignals.map(signal => (
                      <tr key={signal.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {format(new Date(signal.date), 'MMM dd')}
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

