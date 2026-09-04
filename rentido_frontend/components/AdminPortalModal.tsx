'use client';

import React, { useState } from 'react';
import { 
  X, 
  ShieldAlert, 
  ShieldCheck, 
  Layers, 
  Database, 
  Lock, 
  Users, 
  Coins, 
  ArrowUpRight, 
  AlertTriangle, 
  Activity, 
  Truck, 
  FileCheck2,
  ExternalLink
} from 'lucide-react';
import { isAdminUser, AuthUser } from '@/lib/auth';

interface AdminPortalModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: AuthUser | null;
}

export default function AdminPortalModal({ isOpen, onClose, user }: AdminPortalModalProps) {
  if (!isOpen) return null;

  const isAuthorized = isAdminUser(user);
  const [activeTab, setActiveTab] = useState<'metrics' | 'escrow' | 'moderation'>('metrics');

  if (!isAuthorized) {
    return (
      <div 
        onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm cursor-pointer"
      >
        <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-red-200 overflow-hidden cursor-default p-8 text-center">
          <div className="w-16 h-16 rounded-2xl bg-red-100 text-red-600 flex items-center justify-center mx-auto mb-4">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-black text-gray-950">403 Forbidden - Access Denied</h3>
          <p className="text-xs text-gray-600 mt-2 leading-relaxed">
            You are signed in as <strong className="text-gray-900">{user?.email || 'Anonymous'}</strong>.
            This section requires <strong>Super Admin</strong> or <strong>Operations Admin</strong> credentials.
          </p>
          <div className="mt-6 flex justify-center">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 bg-gray-900 hover:bg-gray-800 text-white text-xs font-bold rounded-xl cursor-pointer"
            >
              Close & Return to Marketplace
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto cursor-pointer"
    >
      <div className="relative w-full max-w-4xl bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden my-8 cursor-default flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="px-6 py-5 bg-gradient-to-r from-purple-950 via-indigo-950 to-gray-950 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-400/30 flex items-center justify-center text-purple-400 shadow-md">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-black text-white tracking-tight">Admin Executive Command Deck</h3>
                <span className="bg-purple-500/30 text-purple-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-purple-400/30">
                  Super Admin View
                </span>
              </div>
              <p className="text-xs text-purple-200/80">
                Governance, Escrow Ledger Integrity, Arbitration, and System Status
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <a
              href="http://127.0.0.1:8000/admin/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-xs font-semibold rounded-lg transition-colors"
            >
              <span>Django Portal</span>
              <ExternalLink className="w-3 h-3" />
            </a>
            <button 
              type="button"
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white rounded-full hover:bg-white/10 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-100 px-6 gap-6 text-xs font-bold bg-gray-50/50">
          <button
            type="button"
            onClick={() => setActiveTab('metrics')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'metrics' ? 'border-purple-600 text-purple-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            System Metrics & Health
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('escrow')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'escrow' ? 'border-purple-600 text-purple-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Double-Entry Escrow Ledger
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('moderation')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'moderation' ? 'border-purple-600 text-purple-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Governance & Arbitration
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          
          {activeTab === 'metrics' && (
            <div className="space-y-6">
              
              {/* Stat Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-purple-50/60 border border-purple-100">
                  <div className="text-[11px] font-bold text-purple-700 uppercase tracking-wider">Total Escrow Vault</div>
                  <div className="text-2xl font-black text-purple-950 mt-1">₹85,000</div>
                  <div className="text-[10px] text-purple-600 font-medium mt-1 flex items-center gap-1">
                    <Lock className="w-3 h-3" /> Double-entry balanced
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-100">
                  <div className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider">Verified Listings</div>
                  <div className="text-2xl font-black text-emerald-950 mt-1">8 Active</div>
                  <div className="text-[10px] text-emerald-600 font-medium mt-1 flex items-center gap-1">
                    <FileCheck2 className="w-3 h-3" /> Serial verified
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-100">
                  <div className="text-[11px] font-bold text-blue-700 uppercase tracking-wider">Logistics Fleet</div>
                  <div className="text-2xl font-black text-blue-950 mt-1">100% Operational</div>
                  <div className="text-[10px] text-blue-600 font-medium mt-1 flex items-center gap-1">
                    <Truck className="w-3 h-3" /> Double-blind OTP active
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-100">
                  <div className="text-[11px] font-bold text-amber-700 uppercase tracking-wider">Dispute Rate</div>
                  <div className="text-2xl font-black text-amber-950 mt-1">0.00%</div>
                  <div className="text-[10px] text-amber-600 font-medium mt-1 flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" /> Zero unresolved claims
                  </div>
                </div>
              </div>

              {/* Admin Quick Action Shortcuts */}
              <div className="p-5 rounded-2xl bg-gray-50 border border-gray-100">
                <h4 className="text-xs font-black uppercase tracking-wider text-gray-700 mb-3">
                  Administrative Management Modules
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  
                  <a
                    href="http://127.0.0.1:8000/admin/payments/escrowledger/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-900 group-hover:text-purple-600">Escrow Ledger</div>
                      <div className="text-[11px] text-gray-500 mt-0.5">Audit debit & credit accounts</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  <a
                    href="http://127.0.0.1:8000/admin/assets/asset/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-900 group-hover:text-purple-600">Physical Asset Registry</div>
                      <div className="text-[11px] text-gray-500 mt-0.5">Serial numbers & conditions</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  <a
                    href="http://127.0.0.1:8000/admin/users/user/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-900 group-hover:text-purple-600">User Identity & Roles</div>
                      <div className="text-[11px] text-gray-500 mt-0.5">KYC, roles, and profiles</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  <a
                    href="http://127.0.0.1:8000/admin/inspections/inspectionrecord/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-900 group-hover:text-purple-600">Inspection Proofs</div>
                      <div className="text-[11px] text-gray-500 mt-0.5">Pickup & return photo evidence</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  <a
                    href="http://127.0.0.1:8000/admin/logistics/dispatchorder/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-900 group-hover:text-purple-600">Fleet Dispatches</div>
                      <div className="text-[11px] text-gray-500 mt-0.5">OTP verification logs</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  <a
                    href="http://127.0.0.1:8000/admin/promotions/surgemultiplierrule/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-3.5 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-900 group-hover:text-purple-600">Surge Pricing Engine</div>
                      <div className="text-[11px] text-gray-500 mt-0.5">Weekend & festival multipliers</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                </div>
              </div>

            </div>
          )}

          {activeTab === 'escrow' && (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-start gap-3">
                <Lock className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                <div className="text-xs text-indigo-900 leading-relaxed">
                  <strong>Double-Entry Ledger Integrity:</strong> Every rental transaction creates matching debits and credits across the Renter Escrow Account, Owner Liability Account, Platform Fee Revenue, and Payment Gateway clearing accounts.
                </div>
              </div>

              <div className="border border-gray-200 rounded-2xl overflow-hidden text-xs">
                <table className="w-full text-left">
                  <thead className="bg-gray-50 border-b border-gray-200 text-gray-500 font-bold uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Account Name</th>
                      <th className="p-3">Account Type</th>
                      <th className="p-3">Debits</th>
                      <th className="p-3">Credits</th>
                      <th className="p-3">Net Balance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 font-mono text-[11px]">
                    <tr>
                      <td className="p-3 font-sans font-semibold text-gray-900">ESCROW_HOLDING_VAULT</td>
                      <td className="p-3 text-gray-600 font-sans">Asset (Restricted)</td>
                      <td className="p-3 text-emerald-600">₹85,000.00</td>
                      <td className="p-3 text-gray-400">₹0.00</td>
                      <td className="p-3 font-bold text-emerald-700">+₹85,000.00</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-sans font-semibold text-gray-900">RENTER_SECURITY_DEPOSITS</td>
                      <td className="p-3 text-gray-600 font-sans">Liability</td>
                      <td className="p-3 text-gray-400">₹0.00</td>
                      <td className="p-3 text-amber-600">₹85,000.00</td>
                      <td className="p-3 font-bold text-amber-700">-₹85,000.00</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-sans font-semibold text-gray-900">PLATFORM_FEE_REVENUE</td>
                      <td className="p-3 text-gray-600 font-sans">Revenue</td>
                      <td className="p-3 text-gray-400">₹0.00</td>
                      <td className="p-3 text-indigo-600">₹1,250.00</td>
                      <td className="p-3 font-bold text-indigo-700">+₹1,250.00</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'moderation' && (
            <div className="space-y-4 text-xs">
              <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-between">
                <div>
                  <h5 className="font-bold text-gray-900">Marketplace Dispute Arbitration</h5>
                  <p className="text-gray-500 text-[11px] mt-0.5">Pre-inspection photos vs. Return inspection photographic proof</p>
                </div>
                <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                  All Resolved
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-between">
                <div>
                  <h5 className="font-bold text-gray-900">Physical Serial Verification</h5>
                  <p className="text-gray-500 text-[11px] mt-0.5">8 equipment listings verified and approved for marketplace booking</p>
                </div>
                <span className="px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 font-bold text-[10px]">
                  Queue Clear
                </span>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
