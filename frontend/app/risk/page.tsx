'use client'

import { useState, useEffect } from 'react'
import { api, RiskStatus, Position, PortfolioSnapshot } from '@/lib/api'
import { format } from 'date-fns'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts'

export default function RiskConsolePage() {
  const [status, setStatus] = useState<any>(null)
  const [equityCurve, setEquityCurve] = useState<PortfolioSnapshot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadRiskStatus()
    loadEquityCurve()
  }, [])

  const loadRiskStatus = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await api.getPortfolioStatus()
      setStatus(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadEquityCurve = async () => {
    try {
      const data = await api.getEquityCurve(90)
      setEquityCurve(data)
    } catch (err: any) {
      console.error('Error loading equity curve:', err)
    }
  }

  const getRiskModeColor = (mode: string) => {
    switch (mode) {
      case 'normal':
        return 'bg-green-100 text-green-800'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800'
      case 'halt':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Risk Console</h1>
        <p className="text-gray-600">
          Monitor portfolio risk metrics and automated guardrails
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
          <p className="mt-4 text-gray-600">Loading risk metrics...</p>
        </div>
      ) : status ? (
        <>
          {/* Risk Mode Banner */}
          <div className={`card mb-6 ${
            status.risk_status?.risk_mode === 'halt' 
              ? 'border-2 border-red-500' 
              : status.risk_status?.risk_mode === 'warning'
              ? 'border-2 border-yellow-500'
              : ''
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold mb-2">Risk Mode</h2>
                <span className={`inline-block px-4 py-2 text-lg font-medium rounded-lg ${
                  getRiskModeColor(status.risk_status?.risk_mode || 'normal')
                }`}>
                  {(status.risk_status?.risk_mode || 'normal').toUpperCase()}
                </span>
                <p className="mt-2 text-gray-700">{status.risk_status?.message}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Can Open New Trades</p>
                <p className={`text-3xl font-bold ${
                  status.risk_status?.can_open_new_trades ? 'text-green-600' : 'text-red-600'
                }`}>
                  {status.risk_status?.can_open_new_trades ? '✓' : '✗'}
                </p>
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <MetricCard
              title="Current Equity"
              value={formatCurrency(status.risk_status?.current_equity || 0)}
              subtitle="Portfolio Value"
            />
            <MetricCard
              title="Current Drawdown"
              value={formatPercent(status.risk_status?.current_drawdown || 0)}
              subtitle={`Peak: ${formatCurrency(status.risk_status?.peak_equity || 0)}`}
              negative={true}
            />
            <MetricCard
              title="Daily P&L"
              value={formatCurrency(status.risk_status?.daily_pnl || 0)}
              subtitle={formatPercent(status.risk_status?.daily_pnl_pct || 0)}
              positive={status.risk_status?.daily_pnl > 0}
              negative={status.risk_status?.daily_pnl < 0}
            />
            <MetricCard
              title="Active Positions"
              value={status.risk_status?.active_positions?.toString() || '0'}
              subtitle={`Exposure: ${formatCurrency(status.risk_status?.total_exposure || 0)}`}
            />
          </div>

          {/* Current Positions */}
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">Current Positions</h2>
            
            {!status.positions || status.positions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No open positions</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Side</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contracts</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entry</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stop</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unrealized P&L</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {status.positions.map((pos: any) => (
                      <tr key={pos.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap font-medium">
                          {pos.instrument?.symbol}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            pos.quantity > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {pos.quantity > 0 ? 'LONG' : 'SHORT'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {Math.abs(pos.quantity)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {pos.entry_price.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {pos.current_price?.toFixed(2) || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {pos.stop_price?.toFixed(2) || '-'}
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap font-medium ${
                          pos.unrealized_pnl > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(pos.unrealized_pnl)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Equity History */}
          {equityCurve.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">90-Day Equity History</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={equityCurve}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(date) => format(new Date(date), 'MMM dd')}
                  />
                  <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                  <Tooltip 
                    formatter={(value: any) => formatCurrency(value)}
                    labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="equity" 
                    stroke="#0ea5e9" 
                    strokeWidth={2}
                    name="Equity"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <p>No portfolio data available</p>
          <p className="text-sm mt-2">Run a backtest to see risk metrics</p>
        </div>
      )}
    </div>
  )
}

function MetricCard({ 
  title, 
  value, 
  subtitle, 
  positive, 
  negative 
}: { 
  title: string
  value: string
  subtitle?: string
  positive?: boolean
  negative?: boolean
}) {
  return (
    <div className="card">
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className={`text-2xl font-bold ${
        positive ? 'text-green-600' : negative ? 'text-red-600' : 'text-gray-900'
      }`}>
        {value}
      </p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  )
}

