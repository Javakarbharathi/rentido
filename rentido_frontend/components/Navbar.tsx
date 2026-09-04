'use client';

import React from 'react';
import { 
  ShieldCheck, 
  MapPin, 
  Search, 
  Bell, 
  User, 
  LogIn, 
  Sparkles,
  Wrench,
  ChevronDown,
  PackagePlus
} from 'lucide-react';

interface NavbarProps {
  selectedCity: string;
  onCityChange: (city: string) => void;
  user: any;
  unreadCount: number;
  onOpenAuth: () => void;
  onLogout: () => void;
  onOpenDashboard: () => void;
  onOpenTrustModal: () => void;
  onOpenOwnerStudio: () => void;
}

const CITIES = ['All Cities', 'Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Chennai', 'Pune'];

export default function Navbar({
  selectedCity,
  onCityChange,
  user,
  unreadCount,
  onOpenAuth,
  onLogout,
  onOpenDashboard,
  onOpenTrustModal,
  onOpenOwnerStudio
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-100 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-200">
              <ShieldCheck className="w-6 h-6 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-2xl font-black tracking-tight text-gray-950 font-sans">
                Rent<span className="text-indigo-600">ido</span>
              </span>
              <div className="text-[10px] uppercase font-bold tracking-widest text-gray-700 -mt-1">
                Escrow · Logistics · Trust
              </div>
            </div>
          </div>

          {/* City Selector */}
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-xs font-semibold text-gray-700">
            <MapPin className="w-3.5 h-3.5 text-indigo-600" />
            <select 
              value={selectedCity}
              onChange={(e) => onCityChange(e.target.value)}
              className="bg-transparent outline-none cursor-pointer text-gray-800 pr-1"
            >
              {CITIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="hidden md:flex flex-1 max-w-md mx-2 relative">
          <input 
            type="text"
            placeholder="Search cameras, drones, laptops, tools..."
            className="w-full bg-gray-50 border border-gray-200 rounded-full pl-10 pr-4 py-2 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
          />
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-2.5" />
        </div>

        {/* Navigation Actions */}
        <div className="flex items-center gap-3">
          
          <button 
            onClick={onOpenTrustModal}
            className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Sparkles className="w-4 h-4 text-amber-700" />
            <span>Trust Score</span>
          </button>

          <button
            onClick={onOpenOwnerStudio}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white text-xs font-bold rounded-full shadow-sm shadow-indigo-200 transition-all cursor-pointer hover:shadow-md"
          >
            <PackagePlus className="w-3.5 h-3.5" />
            <span>List Gear</span>
          </button>


          <a 
            href="http://127.0.0.1:8000/admin/" 
            target="_blank" 
            rel="noreferrer"
            className="hidden md:flex items-center gap-1 text-xs font-semibold text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Wrench className="w-3.5 h-3.5 text-gray-700" />
            <span>Admin</span>
          </a>

          {/* User Auth Widget */}
          {user ? (
            <div className="flex items-center gap-2">
              <button 
                onClick={onOpenDashboard}
                className="flex items-center gap-2 px-3.5 py-1.5 bg-indigo-50 border border-indigo-100 rounded-full text-xs font-bold text-indigo-700 hover:bg-indigo-100 transition-colors"
              >
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>{user.email.split('@')[0]}</span>
                <span className="bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded-full text-[10px]">
                  ⭐ 150
                </span>
              </button>

              <button 
                onClick={onLogout}
                className="text-xs text-gray-700 hover:text-red-700 p-2 rounded-lg"
                title="Log Out"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-full shadow-sm shadow-indigo-300 transition-all hover:shadow-md"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </button>
          )}

        </div>
      </div>
    </header>
  );
}
