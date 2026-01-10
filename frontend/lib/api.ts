/**
 * API client for backend communication
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8432'

export interface Instrument {
  id: number
  symbol: string
  name: string
  exchange: string
  tick_size: number
  multiplier: number
  currency: string
  active: boolean
  created_at: string
}

export interface BacktestConfig {
  instruments: string[]
  start_date: string
  end_date: string
  initial_capital: number
  atr_period?: number
  ma_period?: number
  ma_slope_period?: number
  breakout_period?: number
  exit_period?: number
  stop_atr_multiple?: number
  cooldown_days?: number
  risk_per_trade?: number
  max_contracts_per_instrument?: number | null
  max_gross_exposure?: number | null
  max_correlated_exposure?: number | null
  slippage_ticks?: number
  commission_per_contract?: number
  entry_timing?: string
  drawdown_warning_pct?: number
  drawdown_halt_pct?: number
  daily_loss_limit_pct?: number
}

export interface BacktestRun {
  id: number
  name: string
  description: string | null
  start_date: string
  end_date: string
  config: any
  initial_capital: number
  final_equity: number | null
  total_return: number | null
  cagr: number | null
  sharpe_ratio: number | null
  sortino_ratio: number | null
  max_drawdown: number | null
  max_drawdown_duration: number | null
  win_rate: number | null
  profit_factor: number | null
  total_trades: number | null
  status: string
  error_message: string | null
  created_at: string
  completed_at: string | null
}

export interface PortfolioSnapshot {
  id: number
  date: string
  equity: number
  cash: number
  unrealized_pnl: number
  realized_pnl: number
  daily_pnl: number
  drawdown: number
  total_exposure: number
  num_positions: number
}

export interface Signal {
  id: number
  instrument_id: number
  date: string
  signal_type: string
  price: number | null
  target_contracts: number
  stop_price: number | null
  reason: string | null
  created_at: string
  instrument?: Instrument
}

export interface Position {
  id: number
  instrument_id: number
  date: string
  quantity: number
  entry_price: number
  current_price: number | null
  stop_price: number | null
  unrealized_pnl: number
  instrument?: Instrument
}

export interface RiskStatus {
  current_equity: number
  peak_equity: number
  current_drawdown: number
  daily_pnl: number
  daily_pnl_pct: number
  risk_mode: string
  can_open_new_trades: boolean
  active_positions: number
  total_exposure: number
  message: string
}

export interface JournalEntry {
  id: number
  date: string
  title: string
  content: string
  tags: string | null
  signal_id: number | null
  order_id: number | null
  backtest_run_id: number | null
  created_at: string
  updated_at: string
}

class APIClient {
  private baseUrl: string

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Instruments
  async getInstruments(): Promise<Instrument[]> {
    return this.request('/instruments')
  }

  async getInstrument(id: number): Promise<Instrument> {
    return this.request(`/instruments/${id}`)
  }

  // Backtests
  async createBacktest(data: {
    name: string
    description?: string
    config: BacktestConfig
  }): Promise<BacktestRun> {
    return this.request('/backtest/run', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getBacktests(limit: number = 50): Promise<BacktestRun[]> {
    return this.request(`/backtest/runs?limit=${limit}`)
  }

  async getBacktest(id: number): Promise<BacktestRun> {
    return this.request(`/backtest/${id}`)
  }

  async getBacktestResults(id: number): Promise<{
    backtest: BacktestRun
    portfolio_snapshots: PortfolioSnapshot[]
    signals: Signal[]
    positions: Position[]
    metrics: any
  }> {
    return this.request(`/backtest/${id}/results`)
  }

  async deleteBacktest(id: number): Promise<void> {
    return this.request(`/backtest/${id}`, { method: 'DELETE' })
  }

  // Signals
  async getTodaySignals(): Promise<Signal[]> {
    return this.request('/signals/today')
  }

  async getRecentSignals(days: number = 7): Promise<Signal[]> {
    return this.request(`/signals/recent?days=${days}`)
  }

  // Portfolio
  async getPortfolioStatus(): Promise<{
    snapshot: PortfolioSnapshot
    positions: Position[]
    risk_status: RiskStatus
  }> {
    return this.request('/portfolio/status')
  }

  async getCurrentPositions(): Promise<Position[]> {
    return this.request('/portfolio/positions')
  }

  async getEquityCurve(days: number = 365): Promise<PortfolioSnapshot[]> {
    return this.request(`/portfolio/equity-curve?days=${days}`)
  }

  // Journal
  async getJournalEntries(params?: {
    start_date?: string
    end_date?: string
    limit?: number
  }): Promise<JournalEntry[]> {
    const queryParams = new URLSearchParams()
    if (params?.start_date) queryParams.set('start_date', params.start_date)
    if (params?.end_date) queryParams.set('end_date', params.end_date)
    if (params?.limit) queryParams.set('limit', params.limit.toString())
    
    const query = queryParams.toString()
    return this.request(`/journal${query ? `?${query}` : ''}`)
  }

  async getJournalEntry(id: number): Promise<JournalEntry> {
    return this.request(`/journal/${id}`)
  }

  async createJournalEntry(data: {
    date: string
    title: string
    content: string
    tags?: string
    signal_id?: number
    order_id?: number
    backtest_run_id?: number
  }): Promise<JournalEntry> {
    return this.request('/journal', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateJournalEntry(
    id: number,
    data: Partial<{
      title: string
      content: string
      tags: string
    }>
  ): Promise<JournalEntry> {
    return this.request(`/journal/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteJournalEntry(id: number): Promise<void> {
    return this.request(`/journal/${id}`, { method: 'DELETE' })
  }

  // Features
  async recomputeFeatures(instrumentId: number): Promise<any> {
    return this.request(`/features/recompute/${instrumentId}`, {
      method: 'POST',
    })
  }

  async recomputeAllFeatures(): Promise<any> {
    return this.request('/features/recompute-all', {
      method: 'POST',
    })
  }
}

export const api = new APIClient()

