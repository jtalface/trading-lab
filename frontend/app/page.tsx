import Link from 'next/link'

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Volatility Edge Lab
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Futures Trend Following System v1.0
        </p>
        <p className="text-lg text-gray-700 max-w-3xl mx-auto">
          Professional-grade futures trading system implementing a trend-following 
          breakout strategy with volatility-based position sizing, comprehensive 
          risk management, and robust backtesting capabilities.
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <FeatureCard
          title="Strategy Lab"
          description="Design and backtest your trading strategies with powerful configuration options and real-time parameter tuning."
          href="/strategy-lab"
          icon="🔬"
        />
        <FeatureCard
          title="Results & Analytics"
          description="Comprehensive performance metrics, equity curves, drawdown analysis, and trade-by-trade breakdown."
          href="/results"
          icon="📊"
        />
        <FeatureCard
          title="Live Signals"
          description="Monitor real-time entry and exit signals with target position sizes and stop levels."
          href="/signals"
          icon="🎯"
        />
        <FeatureCard
          title="Risk Console"
          description="Track portfolio risk metrics, drawdown status, and automated risk management guardrails."
          href="/risk"
          icon="🛡️"
        />
        <FeatureCard
          title="Trading Journal"
          description="Document your trading decisions, market observations, and strategy refinements."
          href="/journal"
          icon="📝"
        />
        <div className="card bg-gradient-to-br from-primary-50 to-primary-100 border-2 border-primary-200">
          <div className="text-4xl mb-3">⚡</div>
          <h3 className="text-xl font-semibold mb-2 text-primary-900">
            Quick Start
          </h3>
          <p className="text-primary-700 mb-4">
            Get started with our demo backtest and sample data
          </p>
          <Link href="/strategy-lab" className="btn btn-primary inline-block">
            Run Demo Backtest
          </Link>
        </div>
      </div>

      <div className="card bg-gray-800 text-white">
        <h2 className="text-2xl font-bold mb-4">Strategy Overview</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2 text-primary-300">Entry Rules</h3>
            <ul className="space-y-2 text-gray-300">
              <li>• Trend filter: Close vs MA(50) + Slope confirmation</li>
              <li>• Breakout: HH(20) for long, LL(20) for short</li>
              <li>• Initial stop: 2× ATR(20) from entry</li>
              <li>• Position sizing: 0.5% risk per trade</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2 text-primary-300">Exit Rules</h3>
            <ul className="space-y-2 text-gray-300">
              <li>• Exit long: Close crosses LL(10)</li>
              <li>• Exit short: Close crosses HH(10)</li>
              <li>• Catastrophe stop: Always enforced</li>
              <li>• Cooldown: 3 days after exit before re-entry</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ title, description, href, icon }: {
  title: string
  description: string
  href: string
  icon: string
}) {
  return (
    <Link href={href} className="card hover:shadow-lg transition-shadow duration-200">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </Link>
  )
}

