'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const Navbar = () => {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Dashboard', icon: '🏠' },
    { href: '/live-feed', label: 'Live Feed', icon: '📹' },
    { href: '/map', label: 'Map View', icon: '🗺️' }
  ];

  return (
    <header className="bg-red-600 p-4 shadow-lg">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo/Title */}
        <div className="flex items-center gap-3">
          <div className="text-2xl">🔥</div>
          <h1 className="text-2xl font-bold text-white">Firefighter Helmet HUD</h1>
        </div>

        {/* Navigation Links */}
        <nav className="flex gap-2">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-4 py-2 rounded font-semibold transition-colors ${
                pathname === item.href
                  ? 'bg-red-700 text-white shadow-md'
                  : 'bg-red-500 hover:bg-red-700 text-white'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="hidden sm:inline">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 text-white">
          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm hidden md:inline">System Online</span>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
