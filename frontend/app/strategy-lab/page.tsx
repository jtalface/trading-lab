'use client'

import { useState, useEffect } from 'react'
import { api, Instrument, BacktestConfig } from '@/lib/api'

export default function StrategyLabPage() {
  const [instruments, setInstruments] = useState<Instrument[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const [config, setConfig] = useState<BacktestConfig>({
    instruments: ['ES', 'NQ'],
    start_date: '2023-01-03',
    end_date: '2023-03-31',
    initial_capital: 100000,
    atr_period: 20,
    ma_period: 50,
    ma_slope_period: 10,
    breakout_period: 20,
    exit_period: 10,
    stop_atr_multiple: 2.0,
    cooldown_days: 3,
    risk_per_trade: 0.005,
    max_contracts_per_instrument: 5,
    max_gross_exposure: 0.5,
    max_correlated_exposure: 0.3,
    slippage_ticks: 1.0,
    commission_per_contract: 2.50,
    entry_timing: 'next_open',
    drawdown_warning_pct: 0.10,
    drawdown_halt_pct: 0.15,
    daily_loss_limit_pct: 0.02,
  })

  useEffect(() => {
    loadInstruments()
  }, [])

  const loadInstruments = async () => {
    try {
      const data = await api.getInstruments()
      setInstruments(data)
    } catch (err) {
      console.error('Error loading instruments:', err)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const backtest = await api.createBacktest({
        name: `Backtest ${new Date().toLocaleString()}`,
        description: `Strategy test on ${config.instruments.join(', ')}`,
        config,
      })

      setSuccess(`Backtest #${backtest.id} created and running in background!`)
      
      // Redirect to results page after a delay
      setTimeout(() => {
        window.location.href = `/results?id=${backtest.id}`
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to create backtest')
    } finally {
      setLoading(false)
    }
  }

  const toggleInstrument = (symbol: string) => {
    setConfig(prev => ({
      ...prev,
      instruments: prev.instruments.includes(symbol)
        ? prev.instruments.filter(s => s !== symbol)
        : [...prev.instruments, symbol]
    }))
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Strategy Lab</h1>
        <p className="text-gray-600">
          Configure and backtest your futures trend-following strategy
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Instruments Selection */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">1. Select Instruments</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {instruments.map(inst => (
              <label key={inst.symbol} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.instruments.includes(inst.symbol)}
                  onChange={() => toggleInstrument(inst.symbol)}
                  className="w-4 h-4 text-primary-600 rounded"
                />
                <span className="font-medium">{inst.symbol}</span>
                <span className="text-sm text-gray-500">- {inst.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Date Range & Capital */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">2. Backtest Parameters</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="label">Start Date</label>
              <input
                type="date"
                value={config.start_date}
                onChange={e => setConfig({ ...config, start_date: e.target.value })}
                className="input"
                required
              />
            </div>
            <div>
              <label className="label">End Date</label>
              <input
                type="date"
                value={config.end_date}
                onChange={e => setConfig({ ...config, end_date: e.target.value })}
                className="input"
                required
              />
            </div>
            <div>
              <label className="label">Initial Capital ($)</label>
              <input
                type="number"
                value={config.initial_capital}
                onChange={e => setConfig({ ...config, initial_capital: Number(e.target.value) })}
                className="input"
                required
                min="1000"
                step="1000"
              />
            </div>
          </div>
        </div>

        {/* Strategy Parameters */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">3. Strategy Parameters</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="label">ATR Period</label>
              <input
                type="number"
                value={config.atr_period}
                onChange={e => setConfig({ ...config, atr_period: Number(e.target.value) })}
                className="input"
                min="5"
                max="100"
              />
            </div>
            <div>
              <label className="label">MA Period</label>
              <input
                type="number"
                value={config.ma_period}
                onChange={e => setConfig({ ...config, ma_period: Number(e.target.value) })}
                className="input"
                min="10"
                max="200"
              />
            </div>
            <div>
              <label className="label">MA Slope Period</label>
              <input
                type="number"
                value={config.ma_slope_period}
                onChange={e => setConfig({ ...config, ma_slope_period: Number(e.target.value) })}
                className="input"
                min="5"
                max="50"
              />
            </div>
            <div>
              <label className="label">Breakout Period</label>
              <input
                type="number"
                value={config.breakout_period}
                onChange={e => setConfig({ ...config, breakout_period: Number(e.target.value) })}
                className="input"
                min="5"
                max="100"
              />
            </div>
            <div>
              <label className="label">Exit Period</label>
              <input
                type="number"
                value={config.exit_period}
                onChange={e => setConfig({ ...config, exit_period: Number(e.target.value) })}
                className="input"
                min="5"
                max="50"
              />
            </div>
            <div>
              <label className="label">Stop ATR Multiple</label>
              <input
                type="number"
                value={config.stop_atr_multiple}
                onChange={e => setConfig({ ...config, stop_atr_multiple: Number(e.target.value) })}
                className="input"
                min="0.5"
                max="5"
                step="0.1"
              />
            </div>
            <div>
              <label className="label">Cooldown Days</label>
              <input
                type="number"
                value={config.cooldown_days}
                onChange={e => setConfig({ ...config, cooldown_days: Number(e.target.value) })}
                className="input"
                min="0"
                max="20"
              />
            </div>
          </div>
        </div>

        {/* Risk Parameters */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">4. Risk Management</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="label">Risk Per Trade (%)</label>
              <input
                type="number"
                value={(config.risk_per_trade || 0.005) * 100}
                onChange={e => setConfig({ ...config, risk_per_trade: Number(e.target.value) / 100 })}
                className="input"
                min="0.1"
                max="5"
                step="0.1"
              />
            </div>
            <div>
              <label className="label">Max Contracts Per Instrument</label>
              <input
                type="number"
                value={config.max_contracts_per_instrument || ''}
                onChange={e => setConfig({ ...config, max_contracts_per_instrument: e.target.value ? Number(e.target.value) : null })}
                className="input"
                min="1"
                placeholder="No limit"
              />
            </div>
            <div>
              <label className="label">Max Gross Exposure (%)</label>
              <input
                type="number"
                value={(config.max_gross_exposure || 0.5) * 100}
                onChange={e => setConfig({ ...config, max_gross_exposure: Number(e.target.value) / 100 })}
                className="input"
                min="10"
                max="200"
                step="10"
              />
            </div>
            <div>
              <label className="label">Drawdown Warning (%)</label>
              <input
                type="number"
                value={(config.drawdown_warning_pct || 0.10) * 100}
                onChange={e => setConfig({ ...config, drawdown_warning_pct: Number(e.target.value) / 100 })}
                className="input"
                min="5"
                max="50"
                step="1"
              />
            </div>
            <div>
              <label className="label">Drawdown Halt (%)</label>
              <input
                type="number"
                value={(config.drawdown_halt_pct || 0.15) * 100}
                onChange={e => setConfig({ ...config, drawdown_halt_pct: Number(e.target.value) / 100 })}
                className="input"
                min="5"
                max="50"
                step="1"
              />
            </div>
            <div>
              <label className="label">Daily Loss Limit (%)</label>
              <input
                type="number"
                value={(config.daily_loss_limit_pct || 0.02) * 100}
                onChange={e => setConfig({ ...config, daily_loss_limit_pct: Number(e.target.value) / 100 })}
                className="input"
                min="0.5"
                max="10"
                step="0.5"
              />
            </div>
          </div>
        </div>

        {/* Execution Parameters */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">5. Execution Settings</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="label">Slippage (Ticks)</label>
              <input
                type="number"
                value={config.slippage_ticks}
                onChange={e => setConfig({ ...config, slippage_ticks: Number(e.target.value) })}
                className="input"
                min="0"
                max="10"
                step="0.5"
              />
            </div>
            <div>
              <label className="label">Commission Per Contract ($)</label>
              <input
                type="number"
                value={config.commission_per_contract}
                onChange={e => setConfig({ ...config, commission_per_contract: Number(e.target.value) })}
                className="input"
                min="0"
                max="20"
                step="0.5"
              />
            </div>
            <div>
              <label className="label">Entry Timing</label>
              <select
                value={config.entry_timing}
                onChange={e => setConfig({ ...config, entry_timing: e.target.value })}
                className="input"
              >
                <option value="next_open">Next Day Open</option>
                <option value="next_close">Next Day Close</option>
              </select>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="btn btn-secondary"
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={loading || config.instruments.length === 0}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Running Backtest...' : 'Run Backtest'}
          </button>
        </div>
      </form>
    </div>
  )
}

