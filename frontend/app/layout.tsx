import type { Metadata } from 'next'
import './globals.css'
import Navigation from './components/Navigation'

export const metadata: Metadata = {
  title: 'Volatility Edge Lab - Futures Trend v1',
  description: 'Futures trend-following trading system with volatility-based position sizing',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <div className="min-h-screen flex flex-col">
          <Navigation />
          <main className="flex-1">
            {children}
          </main>
          <footer className="bg-gray-800 text-white py-4 text-center text-sm">
            <p>Volatility Edge Lab © 2024 - Futures Trend Following System v1.0</p>
          </footer>
        </div>
      </body>
    </html>
  )
}

