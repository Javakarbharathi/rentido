'use client';

import React from 'react';
import { X, Award, ShieldCheck, TrendingUp, AlertTriangle, Sparkles, CheckCircle2 } from 'lucide-react';

interface TrustBadgeModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: any;
}

export default function TrustBadgeModal({ isOpen, onClose, user }: TrustBadgeModalProps) {
  if (!isOpen) return null;

  const score = user ? 150 : 150; // Default baseline score
  const tier = score >= 650 ? 'Platinum' : score >= 400 ? 'Gold' : score >= 150 ? 'Silver' : 'Bronze';

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto cursor-pointer"
    >
      <div className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden my-8 cursor-default">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-amber-500/10 via-indigo-50 to-white">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center shadow-md shadow-amber-200">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-black text-gray-950">Rentido Trust Score Engine</h2>
              <p className="text-xs text-gray-700">Dynamic reputation score (0 – 1000)</p>
            </div>
          </div>
          <button 
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-700 hover:text-gray-900 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          
          {/* Current Score Gauge */}
          <div className="p-5 rounded-2xl bg-gray-50 border border-gray-100 text-center">
            <div className="text-xs font-bold uppercase tracking-wider text-gray-700">Your Current Reputation Tier</div>
            <div className="text-3xl font-black text-gray-950 mt-1 flex items-center justify-center gap-2">
              <span>🥈 {tier} Member</span>
            </div>
            <div className="text-sm font-bold text-indigo-700 mt-0.5">{score} / 1000 Points</div>

            {/* Score progress bar */}
            <div className="w-full bg-gray-200 h-2.5 rounded-full mt-3 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-amber-500 to-indigo-600 h-full rounded-full transition-all duration-500"
                style={{ width: `${(score / 1000) * 100}%` }}
              />
            </div>
          </div>

          {/* 4 Trust Tiers Breakdown */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-3">Marketplace Trust Tiers</h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-3 rounded-xl border border-gray-100 bg-white">
                <div className="font-bold text-gray-900">🥉 Bronze</div>
                <div className="text-gray-700 text-[11px]">&lt; 150 pts · Baseline / Disputed</div>
              </div>
              <div className="p-3 rounded-xl border border-indigo-200 bg-indigo-50/50">
                <div className="font-bold text-indigo-900">🥈 Silver</div>
                <div className="text-indigo-700 text-[11px]">150 – 399 pts · Verified Renter</div>
              </div>
              <div className="p-3 rounded-xl border border-amber-200 bg-amber-50/40">
                <div className="font-bold text-amber-900">🥇 Gold</div>
                <div className="text-amber-700 text-[11px]">400 – 649 pts · High Trust</div>
              </div>
              <div className="p-3 rounded-xl border border-purple-200 bg-purple-50/40">
                <div className="font-bold text-purple-900">💎 Platinum</div>
                <div className="text-purple-700 text-[11px]">650+ pts · Elite Marketplace Star</div>
              </div>
            </div>
          </div>

          {/* Scoring Rules Matrix */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-3">How Points Are Earned & Deducted</h4>
            <div className="space-y-1.5 text-xs">
              <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-50/60 text-emerald-800">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Government ID / KYC Verified</span>
                </span>
                <span className="font-bold">+50 pts</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-50/60 text-emerald-800">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Successful Rental Completed</span>
                </span>
                <span className="font-bold">+15 pts</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-50/60 text-emerald-800">
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Positive Review (4–5★)</span>
                </span>
                <span className="font-bold">+15 pts</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-red-50/60 text-red-800">
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-600 shrink-0" />
                  <span>Late Return Incident</span>
                </span>
                <span className="font-bold">-15 pts</span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-red-50/60 text-red-800">
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-600 shrink-0" />
                  <span>Asset Damaged Incident</span>
                </span>
                <span className="font-bold">-30 pts</span>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-full bg-gray-900 hover:bg-black text-white font-bold py-3 px-4 rounded-xl text-xs transition-colors cursor-pointer"
          >
            Close
          </button>

        </div>

      </div>
    </div>
  );
}
