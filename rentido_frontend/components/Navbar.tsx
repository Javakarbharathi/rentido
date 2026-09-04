'use client';

import React from 'react';
import { 
  ShieldCheck, 
  MapPin, 
  Search, 
  Sparkles, 
  Wrench, 
  PackagePlus, 
  LogIn, 
  ShieldAlert, 
  FolderClock,
  ExternalLink
} from 'lucide-react';
import { isAdminUser, isOwnerUser, isRenterUser, getRoleBadgeInfo, getPrimaryRole } from '@/lib/auth';

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
  onOpenAdminPortal?: () => void;
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
  onOpenOwnerStudio,
  onOpenAdminPortal,
}: NavbarProps) {
  const isAdmin = isAdminUser(user);
  const isOwner = isOwnerUser(user);
  const isRenter = isRenterUser(user);
  const roleBadge = getRoleBadgeInfo(user);
  const primaryRole = getPrimaryRole(user);

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-100 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 cursor-pointer select-none" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-200">
              <ShieldCheck className="w-6 h-6 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-2xl font-black tracking-tight text-gray-950 font-sans">
                Rent<span className="text-indigo-600">ido</span>
              </span>
              <div className="text-[10px] uppercase font-bold tracking-widest text-gray-500 -mt-1">
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

        {/* Role-Specific Navigation Actions */}
        <div className="flex items-center gap-3">
          
          {/* Trust Score Engine (All users) */}
          <button 
            type="button"
            onClick={onOpenTrustModal}
            className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-amber-500" />
            <span>Trust Score</span>
          </button>

          {/* 1. ADMIN-SPECIFIC ACTION: Admin Portal Deck (Only visible to Admin) */}
          {isAdmin && (
            <button 
              type="button"
              onClick={onOpenAdminPortal}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-purple-50 hover:bg-purple-100 border border-purple-200 text-purple-700 text-xs font-bold rounded-full transition-all cursor-pointer shadow-xs"
              title="Platform Governance & System Health"
            >
              <Wrench className="w-3.5 h-3.5 text-purple-700" />
              <span>Admin Deck</span>
            </button>
          )}

          {/* 2. OWNER-SPECIFIC ACTION: List Gear / Owner Studio (Only for Owners or Admins) */}
          {(isOwner || !user) && (
            <button
              type="button"
              onClick={onOpenOwnerStudio}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white text-xs font-bold rounded-full shadow-sm shadow-indigo-200 transition-all cursor-pointer hover:shadow-md select-none"
            >
              <PackagePlus className="w-3.5 h-3.5" />
              <span>List Gear</span>
            </button>
          )}

          {/* 3. RENTER-SPECIFIC ACTION: My Rentals & OTPs (Only for Renters) */}
          {user && isRenter && !isOwner && !isAdmin && (
            <button
              type="button"
              onClick={onOpenDashboard}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 text-indigo-700 text-xs font-bold rounded-full transition-all cursor-pointer shadow-xs"
            >
              <FolderClock className="w-3.5 h-3.5" />
              <span>My Rentals</span>
            </button>
          )}

          {/* User Auth Widget with Role Badging */}
          {user ? (
            <div className="flex items-center gap-2">
              <button 
                type="button"
                onClick={() => {
                  if (isAdmin && onOpenAdminPortal) {
                    onOpenAdminPortal();
                  } else if (isOwner) {
                    onOpenOwnerStudio();
                  } else {
                    onOpenDashboard();
                  }
                }}
                className={`flex items-center gap-2 px-3.5 py-1.5 border rounded-full text-xs font-bold transition-all cursor-pointer select-none ${roleBadge.colorClass}`}
                title={`Logged in as ${roleBadge.title} - Click to open dashboard`}
              >
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>{roleBadge.badge}</span>
                <span className="opacity-80 font-normal">
                  ({user.email.split('@')[0]})
                </span>
              </button>

              <button 
                type="button"
                onClick={onLogout}
                className="text-xs text-gray-500 hover:text-red-700 p-2 rounded-lg cursor-pointer transition-colors"
                title="Sign Out"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenAuth}
              className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-full shadow-sm shadow-indigo-300 transition-all hover:shadow-md cursor-pointer select-none active:scale-95"
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
