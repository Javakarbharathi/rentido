'use client';

import React, { useState } from 'react';
import { X, KeyRound, Clock, ShieldCheck, Share2, Award, Truck, CheckCircle2 } from 'lucide-react';

interface DashboardModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: any;
}

export default function DashboardModal({ isOpen, onClose, user }: DashboardModalProps) {
  if (!isOpen) return null;

  const [activeTab, setActiveTab] = useState<'rentals' | 'referrals' | 'trust'>('rentals');

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto cursor-pointer"
    >
      <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden my-8 cursor-default">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gray-50/50">
          <div>
            <span className="text-[11px] uppercase font-bold tracking-wider text-indigo-600">Participant Portal</span>
            <h2 className="text-lg font-black text-gray-950 mt-0.5">Welcome, {user?.email || 'Member'}</h2>
          </div>
          <button 
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-700 hover:text-gray-900 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-100 px-6 gap-6 text-xs font-bold">
          <button
            onClick={() => setActiveTab('rentals')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'rentals' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-700 hover:text-gray-900'
            }`}
          >
            Active Rentals & OTPs
          </button>
          <button
            onClick={() => setActiveTab('referrals')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'referrals' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-700 hover:text-gray-900'
            }`}
          >
            Refer & Earn
          </button>
          <button
            onClick={() => setActiveTab('trust')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'trust' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-700 hover:text-gray-900'
            }`}
          >
            Trust Level
          </button>
        </div>

        <div className="p-6">
          
          {activeTab === 'rentals' && (
            <div className="space-y-4">
              {/* Sample Active Rental Card with Handover OTP */}
              <div className="p-4 rounded-2xl border border-indigo-100 bg-indigo-50/30">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">
                    ● ACTIVE RENTAL #4092
                  </span>
                  <span className="text-xs text-gray-700 font-medium">Return in 18 hours</span>
                </div>

                <div className="mt-2.5">
                  <h4 className="text-sm font-bold text-gray-950">Sony FX3 Cinema Camera Kit (8K)</h4>
                  <p className="text-xs text-gray-700">Security deposit of ₹15,000 held in Escrow Ledger.</p>
                </div>

                {/* Handover OTP box */}
                <div className="mt-3 p-3 rounded-xl bg-white border border-indigo-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <KeyRound className="w-4 h-4 text-indigo-600" />
                    <div>
                      <div className="text-[10px] uppercase font-bold text-gray-700">Handover / Return OTP</div>
                      <div className="text-sm font-black text-indigo-700 tracking-wider">849 201</div>
                    </div>
                  </div>
                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-1 rounded-lg">
                    Dispatched with Driver
                  </span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'referrals' && (
            <div className="space-y-4 text-center p-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
                <Share2 className="w-6 h-6" />
              </div>

              <div>
                <h4 className="text-base font-bold text-gray-950">Invite Friends, Earn 25 Trust Points</h4>
                <p className="text-xs text-gray-700 mt-1 max-w-sm mx-auto">
                  When your invited friend registers and completes their first rental, both of you earn instant trust boosts and rental credits.
                </p>
              </div>

              <div className="p-3 bg-gray-50 rounded-2xl border border-gray-200 flex items-center justify-between max-w-sm mx-auto">
                <span className="font-mono text-xs font-bold text-gray-900 tracking-wider">ADMIN1</span>
                <button
                  onClick={() => alert('Referral link copied to clipboard!')}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-bold px-3 py-1.5 rounded-lg cursor-pointer"
                >
                  Copy Link
                </button>
              </div>
            </div>
          )}

          {activeTab === 'trust' && (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-amber-50/50 border border-amber-100 flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-amber-500 text-white flex items-center justify-center text-xl font-bold">
                  🥈
                </div>
                <div>
                  <div className="text-xs font-bold text-amber-900">Silver Member (Standard Trusted)</div>
                  <div className="text-xl font-black text-gray-950">150 / 1000 Trust Score</div>
                  <div className="text-[11px] text-gray-700 mt-0.5">Eligible for up to ₹25,000 instant escrow deposit waiver</div>
                </div>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
