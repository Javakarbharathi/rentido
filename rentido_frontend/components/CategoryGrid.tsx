'use client';

import React from 'react';
import { Camera, Laptop, Mic2, Gamepad2, Bike, Wrench, SunMedium, Compass } from 'lucide-react';

interface CategoryGridProps {
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
}

const CATEGORIES = [
  { id: 'all', name: 'All Gear', icon: Compass, count: '120+ items' },
  { id: 'cameras', name: 'Cameras & Optics', icon: Camera, count: '34 items' },
  { id: 'drones', name: 'Drones & Aerial', icon: SunMedium, count: '18 items' },
  { id: 'computers', name: 'Laptops & Workstations', icon: Laptop, count: '26 items' },
  { id: 'audio', name: 'Audio & Studio', icon: Mic2, count: '22 items' },
  { id: 'gaming', name: 'Gaming & VR', icon: Gamepad2, count: '15 items' },
  { id: 'bikes', name: 'E-Bikes & Mobility', icon: Bike, count: '12 items' },
  { id: 'tools', name: 'Power Tools', icon: Wrench, count: '29 items' },
];

export default function CategoryGrid({ selectedCategory, onSelectCategory }: CategoryGridProps) {
  return (
    <section className="py-8 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900 tracking-tight">Explore by Equipment Category</h2>
            <p className="text-xs text-gray-700 mt-0.5">Filter vetted assets with guaranteed condition inspections</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isSelected = selectedCategory === cat.id;

            return (
              <button
                key={cat.id}
                onClick={() => onSelectCategory(cat.id)}
                className={`flex flex-col items-center justify-center p-3.5 rounded-2xl border transition-all cursor-pointer group text-center ${
                  isSelected
                    ? 'bg-indigo-600 border-indigo-600 text-white shadow-md shadow-indigo-200'
                    : 'bg-white border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/30 text-gray-700'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2 transition-colors ${
                  isSelected ? 'bg-white/20 text-white' : 'bg-gray-50 group-hover:bg-indigo-100 text-indigo-600'
                }`}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold leading-tight line-clamp-1">{cat.name}</span>
                <span className={`text-[10px] mt-0.5 ${isSelected ? 'text-indigo-100' : 'text-gray-700'}`}>
                  {cat.count}
                </span>
              </button>
            );
          })}
        </div>

      </div>
    </section>
  );
}
