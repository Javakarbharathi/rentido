'use client';

import React, { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import CategoryGrid from '@/components/CategoryGrid';
import ListingCard from '@/components/ListingCard';
import BookingModal from '@/components/BookingModal';
import TrustBadgeModal from '@/components/TrustBadgeModal';
import AuthModal from '@/components/AuthModal';
import DashboardModal from '@/components/DashboardModal';
import OwnerStudioModal from '@/components/OwnerStudioModal';
import { fetchListings, Listing } from '@/lib/api';
import { Shield, Sparkles, Truck, Wrench, HeartHandshake } from 'lucide-react';

// Fallback curated gear if the database is newly initialized
const FALLBACK_GEAR: Listing[] = [
  {
    id: 101,
    title: 'Sony FX3 Full-Frame Cinema Camera (Body)',
    description: '12.1MP Exmor R CMOS Sensor, UHD 4K up to 120p, 10-Bit 4:2:2 XAVC S-I, 15+ stops dynamic range.',
    rental_price: '2800.00',
    pricing_model: 'DAILY',
    security_deposit: '15000.00',
    city: 'Bangalore',
    area: 'Indiranagar',
    pincode: '560038',
    is_delivery_available: true,
    is_self_pickup_available: true,
    status: 'PUBLISHED',
    owner_tier: 'Gold Owner',
    owner_trust_score: 620,
    image_url: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80'
  },
  {
    id: 102,
    title: 'Apple MacBook Pro 16" (M3 Max, 64GB Unified RAM, 1TB SSD)',
    description: 'Workstation powerhouse for 8K rendering, Premiere Pro, Davinci Resolve, and Unreal Engine.',
    rental_price: '2200.00',
    pricing_model: 'DAILY',
    security_deposit: '20000.00',
    city: 'Bangalore',
    area: 'Koramangala',
    pincode: '560034',
    is_delivery_available: true,
    is_self_pickup_available: true,
    status: 'PUBLISHED',
    owner_tier: 'Platinum Owner',
    owner_trust_score: 710,
    image_url: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80'
  },
  {
    id: 103,
    title: 'DJI Mavic 3 Pro Cine Combo Drone (Tri-Camera System)',
    description: 'Hasselblad 4/3 CMOS camera, dual tele lenses, Apple ProRes 422 HQ recording, 43 min flight time.',
    rental_price: '3200.00',
    pricing_model: 'DAILY',
    security_deposit: '18000.00',
    city: 'Mumbai',
    area: 'Bandra West',
    pincode: '400050',
    is_delivery_available: true,
    is_self_pickup_available: true,
    status: 'PUBLISHED',
    owner_tier: 'Gold Owner',
    owner_trust_score: 580,
    image_url: 'https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&auto=format&fit=crop&q=80'
  },
  {
    id: 104,
    title: 'Shure SM7B Vocal Dynamic Mic + Cloudlifter CL-1',
    description: 'The industry standard for podcasting, studio vocal recording, and live broadcasting.',
    rental_price: '850.00',
    pricing_model: 'DAILY',
    security_deposit: '5000.00',
    city: 'Delhi',
    area: 'Connaught Place',
    pincode: '110001',
    is_delivery_available: false,
    is_self_pickup_available: true,
    status: 'PUBLISHED',
    owner_tier: 'Silver Owner',
    owner_trust_score: 340,
    image_url: 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&auto=format&fit=crop&q=80'
  },
  {
    id: 105,
    title: 'Canon EOS R5 Mirrorless Camera Body (8K Raw)',
    description: '45MP Full-Frame sensor, 8K30 Raw, sensor-shift image stabilization, dual memory card slots.',
    rental_price: '2500.00',
    pricing_model: 'DAILY',
    security_deposit: '12000.00',
    city: 'Bangalore',
    area: 'Whitefield',
    pincode: '560066',
    is_delivery_available: true,
    is_self_pickup_available: true,
    status: 'PUBLISHED',
    owner_tier: 'Gold Owner',
    owner_trust_score: 590,
    image_url: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80'
  },
  {
    id: 106,
    title: 'Aputure LS 600d Pro Daylight LED Monolight Kit',
    description: 'Professional high-output cinema light with Bowens mount, wireless control, and weather resistance.',
    rental_price: '1800.00',
    pricing_model: 'DAILY',
    security_deposit: '10000.00',
    city: 'Hyderabad',
    area: 'Hitec City',
    pincode: '500081',
    is_delivery_available: true,
    is_self_pickup_available: true,
    status: 'PUBLISHED',
    owner_tier: 'Silver Owner',
    owner_trust_score: 290,
    image_url: 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800&auto=format&fit=crop&q=80'
  }
];

export default function Home() {
  const [selectedCity, setSelectedCity] = useState('All Cities');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [listings, setListings] = useState<Listing[]>(FALLBACK_GEAR);

  // Modals state
  const [selectedListingForBooking, setSelectedListingForBooking] = useState<Listing | null>(null);
  const [isTrustModalOpen, setIsTrustModalOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isDashboardOpen, setIsDashboardOpen] = useState(false);
  const [isOwnerStudioOpen, setIsOwnerStudioOpen] = useState(false);

  // User state
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string>('');

  const loadData = async () => {
    const cityQuery = selectedCity === 'All Cities' ? undefined : selectedCity;
    const apiListings = await fetchListings(cityQuery);
    if (apiListings && apiListings.length > 0) {
      setListings(apiListings);
    } else {
      // Filter fallback gear by city if selected
      if (selectedCity !== 'All Cities') {
        setListings(FALLBACK_GEAR.filter((g) => g.city.toLowerCase() === selectedCity.toLowerCase()));
      } else {
        setListings(FALLBACK_GEAR);
      }
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedCity]);

  // Filter listings by search & category
  const filteredListings = listings.filter((l) => {
    const matchesSearch = !searchQuery || l.title.toLowerCase().includes(searchQuery.toLowerCase()) || l.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  const handleLoginSuccess = (userData: any, accessToken: string) => {
    setUser(userData);
    setToken(accessToken);
  };

  const handleLogout = () => {
    setUser(null);
    setToken('');
  };

  return (
    <div className="min-h-screen flex flex-col bg-white text-gray-900 font-sans">
      
      {/* Navigation */}
      <Navbar
        selectedCity={selectedCity}
        onCityChange={setSelectedCity}
        user={user}
        unreadCount={0}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onLogout={handleLogout}
        onOpenDashboard={() => setIsDashboardOpen(true)}
        onOpenTrustModal={() => setIsTrustModalOpen(true)}
        onOpenOwnerStudio={() => {
          if (!user) {
            setIsAuthModalOpen(true);
          } else {
            setIsOwnerStudioOpen(true);
          }
        }}
      />

      {/* Hero Section */}
      <Hero
        selectedCity={selectedCity}
        onCityChange={setSelectedCity}
        onSearch={setSearchQuery}
      />

      {/* Category Explorer */}
      <CategoryGrid
        selectedCategory={selectedCategory}
        onSelectCategory={setSelectedCategory}
      />

      {/* Marketplace Listings Section */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full">
        
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between mb-8 pb-4 border-b border-gray-100 gap-2">
          <div>
            <h2 className="text-2xl font-black tracking-tight text-gray-950">
              Verified Rental Equipment ({filteredListings.length})
            </h2>
            <p className="text-xs text-gray-700 mt-1">
              Every item has passed a physical serial inspection and is backed by double-blind OTP handover.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs font-semibold text-gray-700">
            <span>Showing:</span>
            <span className="bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-full font-bold">
              {selectedCity}
            </span>
          </div>
        </div>

        {/* Listings Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredListings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              onBook={(l) => setSelectedListingForBooking(l)}
            />
          ))}
        </div>

      </main>

      {/* Trust & Guarantee Banner */}
      <section className="bg-gray-950 text-white py-14 mt-16 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center md:text-left">
            
            <div className="flex flex-col md:flex-row items-center md:items-start gap-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                <Shield className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">Escrow Deposit Protection</h4>
                <p className="text-xs text-gray-400 mt-1 leading-relaxed">
                  Renters never pay deposits directly to owners. All deposits are held in a double-entry financial ledger until physical return inspection.
                </p>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-center md:items-start gap-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
                <Truck className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">Rentido Logistics Fleet</h4>
                <p className="text-xs text-gray-400 mt-1 leading-relaxed">
                  Trained drivers transport equipment with pre-loading photographic proof and 2-stage OTP verification at pickup and drop-off.
                </p>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-center md:items-start gap-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">Automated Trust Engine</h4>
                <p className="text-xs text-gray-400 mt-1 leading-relaxed">
                  Dynamic 0–1000 reputation score unlocking lower deposits and priority bookings as you build rental history.
                </p>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 text-xs py-8 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">Rentido Inc.</span>
            <span>· Trusted Local Rental Marketplace + Logistics + Asset Services</span>
          </div>

          <div className="flex items-center gap-4">
            <a href="http://127.0.0.1:8000/api/docs/" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
              OpenAPI Swagger
            </a>
            <a href="http://127.0.0.1:8000/admin/" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
              Django Admin Portal
            </a>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <BookingModal
        listing={selectedListingForBooking}
        onClose={() => setSelectedListingForBooking(null)}
        user={user}
        onOpenAuth={() => setIsAuthModalOpen(true)}
      />

      <TrustBadgeModal
        isOpen={isTrustModalOpen}
        onClose={() => setIsTrustModalOpen(false)}
        user={user}
      />

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleLoginSuccess}
      />

      <DashboardModal
        isOpen={isDashboardOpen}
        onClose={() => setIsDashboardOpen(false)}
        user={user}
      />

      <OwnerStudioModal
        isOpen={isOwnerStudioOpen}
        onClose={() => setIsOwnerStudioOpen(false)}
        user={user}
        token={token}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onListingCreated={loadData}
      />

    </div>
  );
}
