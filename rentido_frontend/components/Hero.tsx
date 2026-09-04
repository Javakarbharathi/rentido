'use client';

import React from 'react';
import { Search, Calendar, MapPin, Shield, Truck, Award, ArrowRight } from 'lucide-react';

interface HeroProps {
  selectedCity: string;
  onCityChange: (city: string) => void;
  onSearch: (term: string) => void;
}

export default function Hero({ selectedCity, onCityChange, onSearch }: HeroProps) {
  const [searchTerm, setSearchTerm] = React.useState('');

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-indigo-50/60 via-white to-white pt-10 pb-14 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Trust Badges Bar */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-indigo-100 shadow-xs text-xs font-semibold text-indigo-900">
            <span className="flex h-2 w-2 rounded-full bg-emerald-700"></span>
            <span>Rentido Escrow Protection Active</span>
            <span className="text-gray-700">·</span>
            <span className="text-gray-700">Zero Risk Deposits</span>
          </div>
        </div>

        {/* Main Title & Subtitle */}
        <div className="text-center max-w-3xl mx-auto mb-10">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-gray-950 leading-tight">
            Rent Premium Gear. <br />
            <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-800 bg-clip-text text-transparent">
              Protected by Escrow.
            </span>
          </h1>
          <p className="mt-4 text-base sm:text-lg text-gray-700 font-medium">
            From cinema cameras and Apple silicon workstations to electric mobility and power tools.
            Delivered to your door with double-blind OTP handovers.
          </p>
        </div>

        {/* Search & Booking Control Card */}
        <div className="max-w-4xl mx-auto bg-white rounded-3xl p-3 sm:p-4 shadow-xl shadow-indigo-100/50 border border-gray-100">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            
            {/* Gear Query Input */}
            <div className="md:col-span-2 flex items-center gap-3 px-4 py-3 bg-gray-50/80 rounded-2xl border border-gray-100 focus-within:border-indigo-500 focus-within:bg-white transition-all">
              <Search className="w-5 h-5 text-indigo-600 shrink-0" />
              <div className="flex-1">
                <div className="text-[11px] uppercase font-bold tracking-wider text-gray-700">What do you need?</div>
                <input 
                  type="text" 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="e.g. Sony FX3, MacBook M3, DJI Mavic 3"
                  className="w-full bg-transparent text-sm font-semibold text-gray-900 outline-none placeholder-gray-400"
                />
              </div>
            </div>

            {/* City Picker */}
            <div className="flex items-center gap-3 px-4 py-3 bg-gray-50/80 rounded-2xl border border-gray-100 focus-within:border-indigo-500 focus-within:bg-white transition-all">
              <MapPin className="w-5 h-5 text-indigo-600 shrink-0" />
              <div className="flex-1">
                <div className="text-[11px] uppercase font-bold tracking-wider text-gray-700">Location</div>
                <select 
                  value={selectedCity}
                  onChange={(e) => onCityChange(e.target.value)}
                  className="w-full bg-transparent text-sm font-semibold text-gray-900 outline-none cursor-pointer"
                >
                  <option value="All Cities">All Cities</option>
                  <option value="Bangalore">Bangalore</option>
                  <option value="Mumbai">Mumbai</option>
                  <option value="Delhi">Delhi NCR</option>
                  <option value="Hyderabad">Hyderabad</option>
                  <option value="Chennai">Chennai</option>
                  <option value="Pune">Pune</option>
                </select>
              </div>
            </div>

            {/* Search CTA */}
            <div className="flex items-stretch">
              <button 
                onClick={() => onSearch(searchTerm)}
                className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white font-bold text-sm rounded-2xl py-3.5 px-6 shadow-md shadow-indigo-300 hover:shadow-lg transition-all flex items-center justify-center gap-2 group cursor-pointer"
              >
                <span>Find Gear</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>

          </div>

          {/* Quick Filter Tags */}
          <div className="flex flex-wrap items-center gap-2 pt-3 px-2 text-xs text-gray-700">
            <span className="font-semibold text-gray-700">Trending Now:</span>
            {['Sony FX3 Cinema', 'MacBook Pro M3 Max', 'DJI Mavic 3 Cine', 'Canon EOS R5', 'Aputure 600d Light'].map((tag) => (
              <button
                key={tag}
                onClick={() => {
                  setSearchTerm(tag);
                  onSearch(tag);
                }}
                className="bg-gray-100 hover:bg-indigo-50 hover:text-indigo-600 text-gray-600 px-2.5 py-1 rounded-full transition-colors cursor-pointer"
              >
                {tag}
              </button>
            ))}
          </div>

        </div>

        {/* 3 Core Value Pillars */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto mt-12">
          
          <div className="flex items-start gap-3.5 p-4 rounded-2xl bg-white border border-gray-100 shadow-xs">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-gray-900">100% Escrow Holding</h4>
              <p className="text-xs text-gray-700 mt-0.5">Security deposits locked securely in escrow ledger until pre-return inspection.</p>
            </div>
          </div>

          <div className="flex items-start gap-3.5 p-4 rounded-2xl bg-white border border-gray-100 shadow-xs">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <Truck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-gray-900">2-Stage OTP Logistics</h4>
              <p className="text-xs text-gray-700 mt-0.5">Fleet drivers verify physical condition at pickup and handover with mutual OTP codes.</p>
            </div>
          </div>

          <div className="flex items-start gap-3.5 p-4 rounded-2xl bg-white border border-gray-100 shadow-xs">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-gray-900">Dynamic Trust Scoring</h4>
              <p className="text-xs text-gray-700 mt-0.5">0-1000 score engine rewarding KYC verification and punctuality across Bronze to Platinum tiers.</p>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
