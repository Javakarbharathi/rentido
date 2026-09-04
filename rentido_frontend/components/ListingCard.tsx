'use client';

import React from 'react';
import { ShieldCheck, MapPin, Truck, Award, Sparkles } from 'lucide-react';
import { Listing } from '@/lib/api';

interface ListingCardProps {
  listing: Listing;
  onBook: (listing: Listing) => void;
}

export default function ListingCard({ listing, onBook }: ListingCardProps) {
  // Placeholder stock image mappings for gear
  const getListingImage = (title: string) => {
    const t = title.toLowerCase();
    if (t.includes('canon') || t.includes('camera') || t.includes('sony')) {
      return 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80';
    }
    if (t.includes('macbook') || t.includes('laptop')) {
      return 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80';
    }
    if (t.includes('drone') || t.includes('dji')) {
      return 'https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&auto=format&fit=crop&q=80';
    }
    if (t.includes('mic') || t.includes('shure') || t.includes('audio')) {
      return 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&auto=format&fit=crop&q=80';
    }
    if (t.includes('bike') || t.includes('cycle')) {
      return 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800&auto=format&fit=crop&q=80';
    }
    return 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800&auto=format&fit=crop&q=80';
  };

  const imageUrl = listing.image_url || getListingImage(listing.title);

  return (
    <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-xs hover:shadow-xl hover:shadow-indigo-100/50 hover:-translate-y-1 transition-all flex flex-col group">
      
      {/* Visual Image Header */}
      <div className="relative aspect-4/3 overflow-hidden bg-gray-100">
        <img 
          src={imageUrl} 
          alt={listing.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        
        {/* Verification Status Pill */}
        <div className="absolute top-3 left-3">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-600/90 backdrop-blur-md text-white text-[11px] font-bold shadow-xs">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Verified Asset</span>
          </span>
        </div>

        {/* Fulfillment Badge */}
        <div className="absolute top-3 right-3">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md text-white text-[11px] font-medium">
            <Truck className="w-3 h-3 text-indigo-400" />
            <span>{listing.is_delivery_available ? 'Delivery Available' : 'Self Pickup'}</span>
          </span>
        </div>

        {/* Location overlay */}
        <div className="absolute bottom-3 left-3">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-white/90 backdrop-blur-md text-gray-800 text-[10px] font-semibold">
            <MapPin className="w-3 h-3 text-indigo-600" />
            <span>{listing.city} · {listing.area || 'Central'}</span>
          </span>
        </div>
      </div>

      {/* Body Content */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        
        <div>
          {/* Owner Trust Badge */}
          <div className="flex items-center justify-between mb-1.5 text-xs">
            <span className="inline-flex items-center gap-1 text-amber-600 font-bold bg-amber-50 px-2 py-0.5 rounded-md text-[11px]">
              <Sparkles className="w-3 h-3" />
              <span>{listing.owner_tier || 'Gold Owner'}</span>
              <span className="text-amber-800 font-semibold">({listing.owner_trust_score || 550}★)</span>
            </span>
            <span className="text-gray-700 text-[11px]">Verified Payout</span>
          </div>

          <h3 className="font-bold text-gray-950 text-base line-clamp-1 group-hover:text-indigo-600 transition-colors">
            {listing.title}
          </h3>

          <p className="text-xs text-gray-700 mt-1 line-clamp-2 leading-relaxed">
            {listing.description}
          </p>
        </div>

        {/* Pricing & Deposit Footer */}
        <div className="pt-4 mt-4 border-t border-gray-100 flex items-end justify-between gap-2">
          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-black text-gray-950">₹{listing.rental_price}</span>
              <span className="text-xs text-gray-700 font-semibold">/{listing.pricing_model.toLowerCase()}</span>
            </div>
            <div className="text-[11px] font-semibold text-emerald-600 mt-0.5">
              ₹{listing.security_deposit} Escrow Deposit
            </div>
          </div>

          <button
            onClick={() => onBook(listing)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow-xs hover:shadow-md transition-all cursor-pointer shrink-0"
          >
            Rent Now
          </button>
        </div>

      </div>

    </div>
  );
}
