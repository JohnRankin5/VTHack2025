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
    <header className="bg-gray-900/50 backdrop-blur-sm border-b border-white/10 p-4 shadow-lg">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo/Title */}
        <div className="flex items-center gap-4">
          <div className="relative">
            <img 
              src="/fireguard-logo.svg" 
              alt="FireGuard Logo" 
              className="w-12 h-12"
            />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-pulse shadow-lg"></div>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent">FireGuard</h1>
            <p className="text-xs text-gray-400 font-medium">Tactical Command System</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex gap-2">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                pathname === item.href
                  ? 'bg-blue-500 text-white shadow-lg'
                  : 'bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white'
              }`}
            >
              <span className="text-base">{item.icon}</span>
              <span className="hidden sm:inline text-sm">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Status Indicator */}
        <div className="flex items-center gap-3 text-white">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium hidden md:inline">System Online</span>
          </div>
          <div className="text-xs text-gray-400 font-mono">
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
