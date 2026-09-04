'use client';

import React, { useState } from 'react';
import { 
  X, 
  KeyRound, 
  Clock, 
  ShieldCheck, 
  Truck, 
  CheckCircle2, 
  Lock, 
  Sparkles, 
  Share2, 
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { AuthUser, isRenterUser } from '@/lib/auth';

interface RenterDashboardModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: AuthUser | null;
  onBrowseGear?: () => void;
}

export default function RenterDashboardModal({
  isOpen,
  onClose,
  user,
  onBrowseGear,
}: RenterDashboardModalProps) {
  if (!isOpen) return null;

  const [activeTab, setActiveTab] = useState<'rentals' | 'escrow' | 'trust' | 'referrals'>('rentals');

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto cursor-pointer"
    >
      <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden my-8 cursor-default flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="px-6 py-5 bg-gradient-to-r from-blue-950 via-indigo-950 to-gray-950 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300 shadow-md">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-black text-white tracking-tight">Renter Command Center</h3>
                <span className="bg-indigo-500/30 text-indigo-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-indigo-400/30">
                  Verified Renter
                </span>
              </div>
              <p className="text-xs text-indigo-200/80">
                Welcome, {user?.first_name || user?.email?.split('@')[0] || 'Renter'} · Protected by Double-Entry Escrow
              </p>
            </div>
          </div>

          <button 
            type="button"
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-full hover:bg-white/10 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-100 px-6 gap-6 text-xs font-bold bg-gray-50/50">
          <button
            type="button"
            onClick={() => setActiveTab('rentals')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'rentals' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Active Rentals & OTPs
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('escrow')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'escrow' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Escrow Deposit Vault
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('trust')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'trust' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Trust Level & Benefits
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('referrals')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'referrals' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Refer & Earn
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          
          {/* Active Rentals Tab */}
          {activeTab === 'rentals' && (
            <div className="space-y-4">
              
              {/* Sample Active Rental Card */}
              <div className="p-5 rounded-2xl bg-gray-50 border border-gray-200">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-gray-200">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-gray-950">Sony FX3 Full-Frame Cinema Camera</span>
                      <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                        ACTIVE RENTAL
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">Booking #RTD-8821 · Bangalore (Indiranagar)</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">Rental Period</div>
                    <div className="text-xs font-bold text-gray-900">Sep 04 – Sep 06 (2 Days)</div>
                  </div>
                </div>

                {/* Handover OTP Verification Widget */}
                <div className="mt-4 p-4 rounded-xl bg-white border border-indigo-100 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
                      <KeyRound className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-gray-900">Return Handover Secret OTP</div>
                      <div className="text-[11px] text-gray-500">Share this code with the driver/owner upon equipment return</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 bg-indigo-50 px-4 py-2 rounded-xl border border-indigo-200">
                    <span className="font-mono text-lg font-black tracking-widest text-indigo-700">749 201</span>
                  </div>
                </div>

                {/* Logistics Status */}
                <div className="mt-3 flex items-center justify-between text-xs text-gray-600 px-1">
                  <div className="flex items-center gap-1.5">
                    <Truck className="w-3.5 h-3.5 text-indigo-600" />
                    <span>Fulfilled via Rentido Logistics (Driver: Ramesh K.)</span>
                  </div>
                  <span className="text-emerald-600 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Pre-inspection Passed
                  </span>
                </div>
              </div>

              {/* Browse More Gear Action */}
              <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-100 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-indigo-950">Looking to rent more high-end gear?</h4>
                  <p className="text-[11px] text-indigo-700">Drones, cinema cameras, lighting, laptops & e-bikes available across 6 cities.</p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    onClose();
                    if (onBrowseGear) onBrowseGear();
                  }}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all cursor-pointer flex items-center gap-1"
                >
                  <span>Explore Gear</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

            </div>
          )}

          {/* Escrow Deposit Tab */}
          {activeTab === 'escrow' && (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-start gap-3">
                <Lock className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-bold text-emerald-950">Double-Entry Security Deposit Guarantee</h4>
                  <p className="text-[11px] text-emerald-800 mt-1 leading-relaxed">
                    Your refundable deposits are locked in Rentido's regulated ledger vault. Neither owners nor third parties have direct access until physical handover is inspected and approved.
                  </p>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-gray-50 border border-gray-200">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-xs font-bold text-gray-700">Active Refundable Deposit Held</span>
                  <span className="text-xl font-black text-emerald-700 font-mono">₹15,000.00</span>
                </div>
                <div className="text-[11px] text-gray-500 space-y-1">
                  <div className="flex justify-between">
                    <span>Associated Rental:</span>
                    <span className="font-semibold text-gray-800">Sony FX3 (Body) #RTD-8821</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Deposit Release Condition:</span>
                    <span className="text-emerald-700 font-semibold">Automatic refund upon return OTP verification</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Trust Score Tab */}
          {activeTab === 'trust' && (
            <div className="space-y-4">
              <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 text-center">
                <div className="text-[11px] font-bold uppercase tracking-wider text-amber-800">Your Current Trust Score</div>
                <div className="text-3xl font-black text-amber-950 my-1">150 / 1000</div>
                <div className="text-xs font-bold text-amber-700">Tier: Silver Verified Renter</div>
                <p className="text-[11px] text-amber-900/80 mt-2 max-w-md mx-auto leading-relaxed">
                  Complete on-time returns and zero-damage equipment rentals to increase your score to <strong>Gold (400+)</strong> for a <strong>20% security deposit reduction</strong>!
                </p>
              </div>

              <div className="space-y-2 text-xs">
                <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between">
                  <span>Phone & Email Identity Verified</span>
                  <span className="text-emerald-600 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> +50 pts
                  </span>
                </div>
                <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between">
                  <span>First Booking Successful Handover</span>
                  <span className="text-emerald-600 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> +100 pts
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Referrals Tab */}
          {activeTab === 'referrals' && (
            <div className="space-y-4">
              <div className="p-5 rounded-2xl bg-indigo-50 border border-indigo-100 text-center">
                <Share2 className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
                <h4 className="text-sm font-black text-indigo-950">Refer Creators, Filmmakers & Freelancers</h4>
                <p className="text-xs text-indigo-700 mt-1 max-w-md mx-auto">
                  Share your referral link with peers. When they complete their first rental, both of you get <strong>₹500 rental credits</strong>!
                </p>
                <div className="mt-4 p-2 bg-white rounded-xl border border-indigo-200 flex items-center justify-between max-w-sm mx-auto">
                  <span className="text-xs font-mono font-bold text-indigo-900 pl-2">
                    rentido.com/r/{user?.email?.split('@')[0] || 'creator'}
                  </span>
                  <button
                    type="button"
                    onClick={() => navigator.clipboard?.writeText(`https://rentido.com/r/${user?.email?.split('@')[0] || 'creator'}`)}
                    className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-bold rounded-lg cursor-pointer"
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
