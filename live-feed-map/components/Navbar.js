'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const Navbar = () => {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Command Center', icon: '🎯' },
    { href: '/live-feed', label: 'Live Feed', icon: '📹' },
    { href: '/map', label: 'Tactical Map', icon: '🗺️' }
  ];

  return (
    <header className="bg-gradient-to-r from-red-900 via-red-800 to-orange-800 p-4 shadow-2xl border-b-4 border-orange-500">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo/Title */}
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="text-3xl">🔥</div>
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-wide">FIREGUARD</h1>
            <p className="text-xs text-orange-200 font-medium">TACTICAL COMMAND SYSTEM</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex gap-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all duration-200 ${
                pathname === item.href
                  ? 'bg-orange-600 text-white shadow-lg transform scale-105'
                  : 'bg-red-700 hover:bg-orange-600 text-white hover:shadow-md'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="hidden sm:inline text-sm">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Status Indicator */}
        <div className="flex items-center gap-3 text-white">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-lg"></div>
            <span className="text-sm font-medium hidden md:inline">SYSTEM ONLINE</span>
          </div>
          <div className="text-xs text-orange-200 font-mono">
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
