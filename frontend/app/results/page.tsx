'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { api, BacktestRun, PortfolioSnapshot } from '@/lib/api'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Area, AreaChart
} from 'recharts'
import { format } from 'date-fns'

export default function ResultsPage() {
  const searchParams = useSearchParams()
  const backtestId = searchParams.get('id')
  
  const [backtests, setBacktests] = useState<BacktestRun[]>([])
  const [selectedBacktest, setSelectedBacktest] = useState<BacktestRun | null>(null)
  const [snapshots, setSnapshots] = useState<PortfolioSnapshot[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadBacktests()
  }, [])

  useEffect(() => {
    if (backtestId) {
      loadBacktestResults(Number(backtestId))
    }
  }, [backtestId])

  const loadBacktests = async () => {
    try {
      const data = await api.getBacktests(20)
      setBacktests(data)
      
      // If no specific backtest selected, load the latest completed one
      if (!backtestId && data.length > 0) {
        const completed = data.find(b => b.status === 'completed')
        if (completed) {
          setSelectedBacktest(completed)
          loadBacktestResults(completed.id)
        }
      }
    } catch (err: any) {
      setError(err.message)
    }
  }

  const loadBacktestResults = async (id: number) => {
    setLoading(true)
    setError(null)
    
    try {
      const [backtest, results] = await Promise.all([
        api.getBacktest(id),
        api.getBacktestResults(id)
      ])
      
      setSelectedBacktest(backtest)
      setSnapshots(results.portfolio_snapshots)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const formatPercent = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A'
    return `${(value * 100).toFixed(2)}%`
  }

  const formatCurrency = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A'
    return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const formatNumber = (value: number | null, decimals: number = 2) => {
    if (value === null || value === undefined) return 'N/A'
    return value.toFixed(decimals)
  }

  // Prepare chart data
  const equityData = snapshots.map(s => ({
    date: s.date,
    equity: s.equity,
    drawdown: s.drawdown * 100,
  }))

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Backtest Results</h1>
        <p className="text-gray-600">
          Analyze performance metrics and review trading history
        </p>
      </div>

      {/* Backtest Selector */}
      <div className="card mb-6">
        <label className="label">Select Backtest</label>
        <select
          value={selectedBacktest?.id || ''}
          onChange={(e) => loadBacktestResults(Number(e.target.value))}
          className="input max-w-md"
        >
          <option value="">Select a backtest...</option>
          {backtests.map(bt => (
            <option key={bt.id} value={bt.id}>
              #{bt.id} - {bt.name} ({bt.status})
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading results...</p>
        </div>
      )}

      {!loading && selectedBacktest && (
        <>
          {/* Status Banner */}
          {selectedBacktest.status === 'running' && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-700">
              Backtest is still running. Refresh to see updated results.
            </div>
          )}
          
          {selectedBacktest.status === 'failed' && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              Backtest failed: {selectedBacktest.error_message}
            </div>
          )}

          {/* Performance Metrics */}
          {selectedBacktest.status === 'completed' && (
            <>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard
                  title="Total Return"
                  value={formatPercent(selectedBacktest.total_return)}
                  subtitle={`${formatCurrency(selectedBacktest.initial_capital)} → ${formatCurrency(selectedBacktest.final_equity)}`}
                  positive={selectedBacktest.total_return ? selectedBacktest.total_return > 0 : false}
                />
                <MetricCard
                  title="CAGR"
                  value={formatPercent(selectedBacktest.cagr)}
                  subtitle="Annualized Return"
                />
                <MetricCard
                  title="Sharpe Ratio"
                  value={formatNumber(selectedBacktest.sharpe_ratio)}
                  subtitle="Risk-adjusted Return"
                />
                <MetricCard
                  title="Sortino Ratio"
                  value={formatNumber(selectedBacktest.sortino_ratio)}
                  subtitle="Downside Risk-adjusted"
                />
                <MetricCard
                  title="Max Drawdown"
                  value={formatPercent(selectedBacktest.max_drawdown)}
                  subtitle={`${selectedBacktest.max_drawdown_duration || 0} days`}
                  negative={true}
                />
                <MetricCard
                  title="Win Rate"
                  value={formatPercent(selectedBacktest.win_rate)}
                  subtitle={`${selectedBacktest.total_trades || 0} total trades`}
                />
                <MetricCard
                  title="Profit Factor"
                  value={formatNumber(selectedBacktest.profit_factor)}
                  subtitle="Gross Profit / Loss"
                />
                <MetricCard
                  title="Total Trades"
                  value={selectedBacktest.total_trades?.toString() || '0'}
                  subtitle="Completed Trades"
                />
              </div>

              {/* Equity Curve */}
              <div className="card mb-6">
                <h2 className="text-xl font-semibold mb-4">Equity Curve</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={equityData}>
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
                    <Area 
                      type="monotone" 
                      dataKey="equity" 
                      stroke="#0ea5e9" 
                      fill="#0ea5e9" 
                      fillOpacity={0.3}
                      name="Equity"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Drawdown Chart */}
              <div className="card mb-6">
                <h2 className="text-xl font-semibold mb-4">Drawdown</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={equityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={(date) => format(new Date(date), 'MMM dd')}
                    />
                    <YAxis tickFormatter={(value) => `${value.toFixed(1)}%`} />
                    <Tooltip 
                      formatter={(value: any) => `${value.toFixed(2)}%`}
                      labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
                    />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="drawdown" 
                      stroke="#ef4444" 
                      fill="#ef4444" 
                      fillOpacity={0.3}
                      name="Drawdown %"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Configuration Details */}
              <div className="card">
                <h2 className="text-xl font-semibold mb-4">Backtest Configuration</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-medium text-gray-700 mb-2">Period</h3>
                    <p className="text-sm text-gray-600">
                      {format(new Date(selectedBacktest.start_date), 'MMM dd, yyyy')} - {format(new Date(selectedBacktest.end_date), 'MMM dd, yyyy')}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-700 mb-2">Instruments</h3>
                    <p className="text-sm text-gray-600">
                      {selectedBacktest.config.instruments?.join(', ')}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-700 mb-2">Strategy</h3>
                    <p className="text-sm text-gray-600">
                      MA({selectedBacktest.config.ma_period}), ATR({selectedBacktest.config.atr_period}), 
                      Breakout({selectedBacktest.config.breakout_period})
                    </p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-700 mb-2">Risk</h3>
                    <p className="text-sm text-gray-600">
                      {formatPercent(selectedBacktest.config.risk_per_trade)} per trade, 
                      {formatPercent(selectedBacktest.config.max_gross_exposure)} max exposure
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}
        </>
      )}

      {!loading && !selectedBacktest && (
        <div className="text-center py-12 text-gray-500">
          <p>No backtest selected. Run a backtest from the Strategy Lab.</p>
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

