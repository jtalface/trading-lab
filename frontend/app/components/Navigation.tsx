'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navItems = [
  { name: 'Strategy Lab', href: '/strategy-lab' },
  { name: 'Results', href: '/results' },
  { name: 'Live Signals', href: '/signals' },
  { name: 'Risk Console', href: '/risk' },
  { name: 'Journal', href: '/journal' },
]

export default function Navigation() {
  const pathname = usePathname()
  
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <div className="text-2xl font-bold text-primary-600">
                Volatility Edge Lab
              </div>
              <span className="ml-2 text-sm text-gray-500">v1.0</span>
            </Link>
          </div>
          
          <div className="flex items-center space-x-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

